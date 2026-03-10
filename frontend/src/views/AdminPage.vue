<template>
    <div class="admin-wrapper">
    
        <div class="admin-content">
    
            <!-- page header -->
            <div class="page-header">
                <h1>Admin <span class="text-pink">Panel</span></h1>
                <p>Manage users, roles, and teacher accounts</p>
            </div>
    
            <!-- success banner -->
            <transition name="fade">
                <div v-if="store.successMessage" class="alert alert--success">
                    <span class="material-symbols-outlined">check_circle</span> {{ store.successMessage }}
                    <button class="alert-close" @click="store.clearMessages">
                                <span class="material-symbols-outlined">close</span>
                            </button>
                </div>
            </transition>
    
            <!-- error banner -->
            <transition name="fade">
                <div v-if="store.error" class="alert alert--error">
                    <span class="material-symbols-outlined">error</span> {{ store.error }}
                    <button class="alert-close" @click="store.clearMessages">
                                <span class="material-symbols-outlined">close</span>
                            </button>
                </div>
            </transition>
    
            <!-- invite teacher section -->
            <div class="section-card">
                <div class="section-title-row">
                    <span class="material-symbols-outlined section-icon">person_add</span>
                    <div>
                        <h2>Invite Teacher</h2>
                        <p>Enter full name and email, username and password are auto-generated and sent by email.</p>
                    </div>
                </div>
    
                <div class="form-row">
                    <div class="form-group">
                        <label>Full Name</label>
                        <input v-model="invite.full_name" type="text" placeholder="e.g. John Doe" :disabled="store.loading" />
                    </div>
                    <div class="form-group">
                        <label>Email Address</label>
                        <input v-model="invite.email" type="email" placeholder="e.g. john.doe@university.edu" :disabled="store.loading" />
                    </div>
                </div>
    
                <button class="btn-action" :disabled="store.loading || !invite.full_name || !invite.email" @click="handleInvite">
                            <span class="material-symbols-outlined">send</span>
                            {{ store.loading ? 'Sending…' : 'Send Invite' }}
                        </button>
            </div>
    
            <!-- users section -->
            <div class="section-card">
                <div class="section-title-row">
                    <span class="material-symbols-outlined section-icon">group</span>
                    <div>
                        <h2>All Accounts</h2>
                        <p>Filter, change roles, or deactivate user accounts.</p>
                    </div>
                </div>
    
                <!-- role filter tabs -->
                <div class="filter-tabs">
                    <div v-for="f in filters" :key="f.label" class="filter-tab" :class="{ active: activeFilter === f.value }" @click="applyFilter(f.value)">
                        {{ f.label }}
                    </div>
                </div>
    
                <!-- skeleton loading -->
                <div v-if="store.loading && !store.users.length" class="skeleton-list">
                    <div v-for="i in 4" :key="i" class="skeleton-row" />
                </div>
    
                <!-- empty state -->
                <div v-else-if="!store.users.length" class="empty-state">
                    <span class="material-symbols-outlined">person_search</span>
                    <p>No accounts found.</p>
                </div>
    
                <!-- user rows -->
                <ul v-else class="user-list">
                    <li v-for="user in store.users" :key="user.id" class="user-row" :class="{ 'user-row--inactive': !user.is_active }">
                        <!-- avatar + info -->
                        <div class="user-identity">
                            <div class="user-avatar" :data-role="user.role">
                                {{ initials(user.full_name || user.username) }}
                            </div>
                            <div class="user-meta">
                                <span class="user-name">{{ user.full_name || user.username }}</span>
                                <span class="user-email">{{ user.email }}</span>
                            </div>
                        </div>
    
                        <!-- role badge -->
                        <span class="role-badge" :class="`role-badge--${user.role}`">
                                    {{ user.role }}
                                </span>
    
                        <!-- email sent indicator for teachers -->
                        <span v-if="user.role === 'teacher'" class="email-status" :class="user.email_sent ? 'email-status--sent' : 'email-status--pending'">
                                    <span class="material-symbols-outlined" style="font-size: 14px">
                                        {{ user.email_sent ? 'mark_email_read' : 'schedule_send' }}
                                    </span> {{ user.email_sent ? 'Sent' : 'Pending' }}
                        </span>
    
                        <!-- active user actions -->
                        <div v-if="user.is_active" class="user-actions">
                            <button v-if="user.role === 'teacher'" class="btn-ghost" :disabled="store.loading" @click="handleResend(user)">
                                        Resend Email
                                    </button>
    
                            <select class="role-select" :value="user.role" :disabled="store.loading" @change="handleRoleChange(user, $event.target.value)">
                                        <option value="student">student</option>
                                        <option value="teacher">teacher</option>
                                        <option value="admin">admin</option>
                                    </select>
    
                            <button class="btn-danger" :disabled="store.loading" @click="confirmDeactivate(user)">
                                        <span class="material-symbols-outlined">block</span>
                                        Deactivate
                                    </button>
                        </div>
    
                        <span v-else class="inactive-label">
                                    <span class="material-symbols-outlined" style="font-size: 15px">block</span> Inactive
                        </span>
                    </li>
                </ul>
            </div>
    
        </div>
    
        <Footer />
    
        <!-- confirm deactivate modal -->
        <transition name="fade">
            <div v-if="confirm.show" class="modal-overlay" @click.self="confirm.show = false">
                <div class="modal-card">
                    <h3>Deactivate Account?</h3>
                    <p>
                        This will prevent
                        <strong>{{ confirm.user?.full_name || confirm.user?.username }}</strong> from logging in.
                    </p>
                    <div class="modal-actions">
                        <button class="btn-ghost" @click="confirm.show = false">Cancel</button>
                        <button class="btn-action btn-action--danger" @click="handleDeactivate">Confirm</button>
                    </div>
                </div>
            </div>
        </transition>
    
    </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useAdminStore } from '@/store/adminStore'

const store = useAdminStore()

const invite = reactive({ full_name: '', email: '' })
const activeFilter = ref(null)
const confirm = reactive({ show: false, user: null })

const filters = [
    { label: 'All', value: null },
    { label: 'Students', value: 'student' },
    { label: 'Teachers', value: 'teacher' },
    { label: 'Admins', value: 'admin' },
]

onMounted(() => store.fetchUsers())

function initials(name) {
    return (name || '?')
        .split(' ')
        .map(w => w[0])
        .slice(0, 2)
        .join('')
        .toUpperCase()
}

function applyFilter(role) {
    activeFilter.value = role
    store.fetchUsers(role)
}

async function handleInvite() {
    if (!invite.full_name || !invite.email) return
    const result = await store.inviteTeacher({ ...invite })
    if (result) {
        invite.full_name = ''
        invite.email = ''
    }
}

function handleRoleChange(user, newRole) {
    if (newRole !== user.role) store.changeRole(user.id, newRole)
}

function confirmDeactivate(user) {
    confirm.user = user
    confirm.show = true
}

async function handleDeactivate() {
    if (!confirm.user) return
    await store.deactivateUser(confirm.user.id)
    confirm.show = false
    confirm.user = null
}

async function handleResend(user) {
    await store.sendCredentials(user.id)
}
</script>

<style scoped>
.admin-wrapper {
    min-height: 100vh;
    background: var(--background-light);
    display: flex;
    flex-direction: column;
}

.admin-content {
    flex: 1;
    max-width: 900px;
    width: 100%;
    margin: 0 auto;
    padding: 48px 24px 40px;
    display: flex;
    flex-direction: column;
    gap: 28px;
}

/* page header */

.page-header h1 {
    font-size: 28px;
    font-weight: 800;
    color: #111827;
    margin-bottom: 6px;
}

.text-pink {
    color: var(--primary-hover);
}

.page-header p {
    font-size: 14px;
    color: #6b7280;
}

/* alert banners */

.alert {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 13px 16px;
    border-radius: 12px;
    font-size: 14px;
    font-weight: 500;
}

.alert--success {
    background: #ecfdf5;
    color: #065f46;
    border: 1px solid #a7f3d0;
}

.alert--error {
    background: #fff1f2;
    color: #be123c;
    border: 1px solid #fecdd3;
}

.alert-close {
    margin-left: auto;
    background: none;
    border: none;
    cursor: pointer;
    color: inherit;
    opacity: 0.5;
    display: flex;
    align-items: center;
}

.alert-close:hover {
    opacity: 1;
}

/* section card — same look as social-btn/form containers in Login.vue */

.section-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 28px;
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.section-title-row {
    display: flex;
    align-items: flex-start;
    gap: 14px;
}

.section-icon {
    font-size: 22px;
    color: var(--primary-hover);
    margin-top: 2px;
}

.section-title-row h2 {
    font-size: 18px;
    font-weight: 700;
    color: #111827;
    margin-bottom: 4px;
}

.section-title-row p {
    font-size: 13px;
    color: #6b7280;
}

/* invite form row */

.form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin-bottom: 0;
}

.form-group label {
    font-size: 14px;
    font-weight: 600;
    color: #374151;
}

input {
    width: 100%;
    padding: 12px 16px;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    background: #f9fafb;
    font-size: 15px;
    font-family: inherit;
    box-sizing: border-box;
    transition: all 0.2s;
}

input:focus {
    outline: none;
    border-color: var(--forest-green);
    background: white;
    box-shadow: 0 0 0 4px rgba(10, 112, 60, 0.1);
}

input:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

/* primary action button — same style as btn-login */

.btn-action {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 12px 24px;
    background: var(--forest-green);
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: 700;
    font-size: 15px;
    cursor: pointer;
    font-family: inherit;
    transition: all 0.2s;
    align-self: flex-start;
}

.btn-action:hover:not(:disabled) {
    filter: brightness(1.15);
    box-shadow: 0 4px 12px rgba(10, 112, 60, 0.2);
}

.btn-action:active {
    transform: scale(0.98);
}

.btn-action:disabled {
    opacity: 0.4;
    cursor: not-allowed;
}

.btn-action--danger {
    background: #be123c;
}

.btn-action--danger:hover:not(:disabled) {
    filter: brightness(1.1);
    box-shadow: 0 4px 12px rgba(190, 18, 60, 0.2);
}

/* ghost button — same look as social-btn */

.btn-ghost {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 8px 14px;
    border: 1px solid #e5e7eb;
    background: white;
    border-radius: 10px;
    font-weight: 600;
    font-size: 13px;
    cursor: pointer;
    font-family: inherit;
    color: #374151;
    transition: background 0.2s;
}

.btn-ghost:hover:not(:disabled) {
    background: #f9fafb;
}

.btn-ghost:disabled {
    opacity: 0.4;
    cursor: not-allowed;
}

/* danger outline button */

.btn-danger {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 8px 14px;
    border: 1px solid #fecdd3;
    background: white;
    border-radius: 10px;
    font-weight: 600;
    font-size: 13px;
    cursor: pointer;
    font-family: inherit;
    color: #be123c;
    transition: all 0.2s;
}

.btn-danger:hover:not(:disabled) {
    background: #fff1f2;
}

.btn-danger:disabled {
    opacity: 0.4;
    cursor: not-allowed;
}

/* filter tabs — reuses nav-tab pattern from Login.vue */

.filter-tabs {
    display: flex;
    background: #f1f3f7;
    padding: 4px;
    border-radius: 12px;
    gap: 4px;
}

.filter-tab {
    flex: 1;
    text-align: center;
    padding: 10px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 13px;
    cursor: pointer;
    color: #6b7280;
    transition: all 0.2s;
}

.filter-tab.active {
    background: white;
    color: var(--primary-hover);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

/* skeleton */

.skeleton-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.skeleton-row {
    height: 62px;
    background: linear-gradient(90deg, #f1f3f7 25%, #f9fafb 50%, #f1f3f7 75%);
    background-size: 200% 100%;
    border-radius: 12px;
    animation: shimmer 1.4s infinite;
}

@keyframes shimmer {
    0% {
        background-position: 200% 0;
    }
    100% {
        background-position: -200% 0;
    }
}

/* empty state */

.empty-state {
    text-align: center;
    padding: 40px;
    color: #9ca3af;
}

.empty-state .material-symbols-outlined {
    font-size: 40px;
    display: block;
    margin-bottom: 8px;
    color: #d1d5db;
}

/* user list */

.user-list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 0;
}

.user-row {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 14px 4px;
    border-bottom: 1px solid #f3f4f6;
    transition: background 0.15s;
    border-radius: 8px;
}

.user-row:last-child {
    border-bottom: none;
}

.user-row:hover {
    background: #f9fafb;
}

.user-row--inactive {
    opacity: 0.4;
}

/* avatar */

.user-avatar {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    background: #fff6fd;
    color: var(--primary-hover);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 13px;
    flex-shrink: 0;
}

.user-avatar[data-role="teacher"] {
    background: #f2ffed;
    color: var(--accent-green);
}

.user-avatar[data-role="admin"] {
    background: #e7faff;
    color: #00145d;
}

.user-identity {
    display: flex;
    align-items: center;
    gap: 12px;
    flex: 1;
    min-width: 0;
}

.user-meta {
    display: flex;
    flex-direction: column;
    min-width: 0;
}

.user-name {
    font-size: 14px;
    font-weight: 600;
    color: #111827;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.user-email {
    font-size: 12px;
    color: #9ca3af;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* role badge */

.role-badge {
    font-size: 11px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    flex-shrink: 0;
}

.role-badge--student {
    background: #fff6fd;
    color: var(--primary-hover);
}

.role-badge--teacher {
    background: #f2ffed;
    color: var(--accent-green);
}

.role-badge--admin {
    background: #e7faff;
    color: #00145d;
}

/* email status */

.email-status {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 11px;
    font-weight: 500;
    padding: 3px 8px;
    border-radius: 20px;
    flex-shrink: 0;
}

.email-status--sent {
    background: #e7faff;
    color: var(--accent-green);
}

.email-status--pending {
    background: #fefce8;
    color: var(--warning-yellow);
}

/* user actions */

.user-actions {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-shrink: 0;
}

.role-select {
    padding: 8px 10px;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    font-family: inherit;
    font-size: 13px;
    background: #f9fafb;
    cursor: pointer;
    color: #374151;
    transition: all 0.2s;
}

.role-select:focus {
    outline: none;
    border-color: var(--forest-green);
    box-shadow: 0 0 0 4px rgba(10, 112, 60, 0.1);
}

.role-select:disabled {
    opacity: 0.4;
    cursor: not-allowed;
}

.inactive-label {
    font-size: 12px;
    color: #9ca3af;
    display: inline-flex;
    align-items: center;
    gap: 4px;
}

/* modal */

.modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.35);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 100;
}

.modal-card {
    background: white;
    border-radius: 16px;
    padding: 32px;
    max-width: 400px;
    width: 90%;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.modal-card h3 {
    font-size: 18px;
    font-weight: 700;
    color: #111827;
    margin-bottom: 10px;
}

.modal-card p {
    font-size: 14px;
    color: #6b7280;
    line-height: 1.6;
    margin-bottom: 24px;
}

.modal-actions {
    display: flex;
    gap: 10px;
    justify-content: flex-end;
}

/* transitions */

.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.2s;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}

/* responsive */

@media (max-width: 640px) {
    .form-row {
        grid-template-columns: 1fr;
    }
    .user-row {
        flex-wrap: wrap;
    }
    .user-actions {
        width: 100%;
        flex-wrap: wrap;
    }
}
</style>