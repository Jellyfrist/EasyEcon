<template>
    <div class="settings-wrapper">

        <!-- ── Full-width page header, grounded with border ── -->
        <div class="page-banner">
            <div class="page-banner-inner">
                <!-- left: page title -->
                <div class="banner-title">
                    <h1>Account <span class="text-pink">Settings</span></h1>
                    <p class="text-muted">Manage your profile and security preferences</p>
                </div>
                <!-- right: profile info -->
                <div class="banner-profile">
                    <div class="user-avatar" :data-role="user?.role">{{ initials }}</div>
                    <div class="banner-profile-info">
                        <span class="banner-username">{{ user?.full_name || user?.username }}</span>
                        <span class="role-badge" :class="`role-badge--${user?.role}`">{{ user?.role }}</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- ── Content ── -->
        <div class="settings-body">

            <transition name="fade">
                <div v-if="successMsg" class="alert alert--success">
                    <span class="material-symbols-outlined">check_circle</span>
                    <span>{{ successMsg }}</span>
                    <button class="alert-close" @click="successMsg = ''">
                        <span class="material-symbols-outlined">close</span>
                    </button>
                </div>
            </transition>

            <transition name="fade">
                <div v-if="errorMsg" class="alert alert--error">
                    <span class="material-symbols-outlined">error</span>
                    <span>{{ errorMsg }}</span>
                    <button class="alert-close" @click="errorMsg = ''">
                        <span class="material-symbols-outlined">close</span>
                    </button>
                </div>
            </transition>

            <!-- ── Profile Card ── -->
            <section class="card section-card">
                <div class="section-title-row">
                    <div class="section-icon-wrap">
                        <span class="material-symbols-outlined">manage_accounts</span>
                    </div>
                    <div>
                        <h2>Profile</h2>
                        <p class="text-muted">Your personal information</p>
                    </div>
                </div>

                <div class="section-divider"></div>

                <div class="grid-2 fields-grid">

                    <div class="form-group">
                        <label>Username</label>
                        <div v-if="isStudent" class="input-with-btn">
                            <input class="input-field" v-model="form.username" type="text"
                                :placeholder="user?.username" :disabled="saving" />
                            <button class="btn btn-green btn-save"
                                :disabled="saving || !form.username || form.username === user?.username"
                                @click="saveUsername">
                                {{ saving ? '…' : 'Save' }}
                            </button>
                        </div>
                        <div v-else class="read-field">{{ user?.username }}</div>
                    </div>

                    <div class="form-group">
                        <label>Email Address</label>
                        <div class="read-field">{{ user?.email }}</div>
                        <span class="field-hint">contact admin to change</span>
                    </div>

                    <div v-if="!isStudent" class="form-group">
                        <label>Full Name</label>
                        <div class="read-field">{{ user?.full_name || '—' }}</div>
                        <span class="field-hint">shown on published content</span>
                    </div>

                </div>

                <div v-if="!isStudent" class="notice-box">
                    <span class="material-symbols-outlined">info</span>
                    <p>Your account is managed by the administrator. To update your details or reset your password, contact your admin.</p>
                </div>
            </section>

            <!-- ── Password Card ── -->
            <section v-if="isStudent" class="card section-card">
                <div class="section-title-row">
                    <div class="section-icon-wrap section-icon-wrap--pink">
                        <span class="material-symbols-outlined">lock</span>
                    </div>
                    <div>
                        <h2>Change Password</h2>
                        <p class="text-muted">Choose a new password — at least 8 characters</p>
                    </div>
                </div>

                <div class="section-divider"></div>

                <div class="grid-2 fields-grid">
                    <div class="form-group">
                        <label>New Password</label>
                        <div class="password-wrapper">
                            <input class="input-field" v-model="pw.new_password"
                                :type="pw.showNew ? 'text' : 'password'"
                                placeholder="min. 8 characters" :disabled="saving" />
                            <button type="button" class="toggle-btn" @click="pw.showNew = !pw.showNew">
                                <span class="material-symbols-outlined">{{ pw.showNew ? 'visibility_off' : 'visibility' }}</span>
                            </button>
                        </div>
                    </div>

                    <div class="form-group">
                        <label>Confirm Password</label>
                        <div class="password-wrapper">
                            <input class="input-field" v-model="pw.confirm"
                                :type="pw.showConfirm ? 'text' : 'password'"
                                placeholder="repeat new password" :disabled="saving" />
                            <button type="button" class="toggle-btn" @click="pw.showConfirm = !pw.showConfirm">
                                <span class="material-symbols-outlined">{{ pw.showConfirm ? 'visibility_off' : 'visibility' }}</span>
                            </button>
                        </div>
                        <span v-if="pw.confirm && pw.new_password !== pw.confirm" class="field-error">
                            passwords do not match
                        </span>
                    </div>
                </div>

                <button class="btn btn-primary btn-update-pw"
                    :disabled="saving || !passwordValid" @click="savePassword">
                    <span class="material-symbols-outlined">lock_reset</span>
                    {{ saving ? 'Saving…' : 'Update Password' }}
                </button>
            </section>

        </div>

        <Footer />
    </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/authStore'
import userService from '@/services/userService'

const router = useRouter()
const authStore = useAuthStore()

const user = computed(() => authStore.user)
const isStudent = computed(() => authStore.isStudent)

const saving = ref(false)
const successMsg = ref('')
const errorMsg = ref('')

const form = reactive({ username: '' })

const pw = reactive({
    new_password: '',
    confirm: '',
    showNew: false,
    showConfirm: false,
})

const initials = computed(() =>
    (user.value?.full_name || user.value?.username || '?')
    .split(' ').map(w => w[0]).slice(0, 2).join('').toUpperCase()
)

const passwordValid = computed(() =>
    pw.new_password.length >= 8 && pw.new_password === pw.confirm
)

onMounted(() => {
    if (!authStore.isAuthenticated) {
        router.push('/login')
        return
    }
    form.username = user.value?.username || ''
})

function _handleError(err) {
    errorMsg.value = err?.response?.data?.detail || err.message || 'something went wrong'
    successMsg.value = ''
}

async function saveUsername() {
    if (!form.username || form.username === user.value?.username) return
    saving.value = true
    errorMsg.value = ''
    try {
        const res = await userService.updateUsername(form.username)
        const newUsername = res.data?.username ?? form.username
        const updatedUser = { ...authStore.user, username: newUsername }
        authStore._setUser(updatedUser)
        localStorage.setItem('user', JSON.stringify(updatedUser))
        form.username = newUsername
        successMsg.value = 'username updated'
    } catch (err) {
        _handleError(err)
    } finally {
        saving.value = false
    }
}

async function savePassword() {
    if (!passwordValid.value) return
    saving.value = true
    errorMsg.value = ''
    try {
        await userService.changePassword(pw.new_password)
        pw.new_password = ''
        pw.confirm = ''
        successMsg.value = 'password updated successfully'
    } catch (err) {
        _handleError(err)
    } finally {
        saving.value = false
    }
}
</script>

<style scoped>

.settings-wrapper {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

/* ── Page Banner — blends with app gradient, no harsh color ── */
.page-banner {
    width: 100%;
    background: rgba(255, 255, 255, 0.55);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--card-border);
}

.page-banner-inner {
    max-width: 800px;
    margin: 0 auto;
    padding: 28px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
}

/* right block */
.banner-profile {
    display: flex;
    align-items: center;
    gap: 14px;
}

.banner-profile-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.banner-username {
    font-size: 15px;
    font-weight: 700;
    color: var(--text-main);
}

/* left block */
.banner-title {
    text-align: left;
}

.banner-title h1 {
    font-size: 24px;
    font-weight: 800;
    color: var(--text-main);
    margin-bottom: 4px;
}

.text-pink { color: var(--primary-pink); }

/* ── Avatar in banner ── */
.user-avatar {
    width: 60px;
    height: 60px;
    border-radius: var(--radius-lg);
    background: var(--light-green);
    color: var(--forest-green);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    font-weight: 800;
    flex-shrink: 0;
    border: 2px solid #fff;
    box-shadow: var(--shadow-sm);
}

.user-avatar[data-role="teacher"] { background: var(--light-yellow); color: #c2410c; }
.user-avatar[data-role="student"] { background: var(--light-pink);   color: var(--primary-pink); }

/* ── Role badge ── */
.role-badge {
    display: inline-block;
    font-size: 11px;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 20px;
    text-transform: capitalize;
    flex-shrink: 0;
}

.role-badge--student { background: var(--light-pink);   color: var(--primary-pink); }
.role-badge--teacher { background: var(--light-yellow); color: #c2410c; }
.role-badge--admin   { background: var(--light-green);  color: var(--forest-green); }

/* ── Body ── */
.settings-body {
    flex: 1;
    max-width: 800px;
    width: 100%;
    margin: 0 auto;
    padding: 32px 32px 48px;
    display: flex;
    flex-direction: column;
    gap: 20px;
}

/* ── Alerts ── */
.alert {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 16px;
    border-radius: var(--radius-md);
    font-size: 14px;
    font-weight: 500;
}

.alert--success { background: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }
.alert--error   { background: #fff1f2; color: #be123c; border: 1px solid #fecdd3; }

.alert-close {
    margin-left: auto;
    background: none;
    border: none;
    cursor: pointer;
    color: inherit;
    opacity: 0.5;
    display: flex;
    align-items: center;
    transition: opacity 0.15s;
}
.alert-close:hover { opacity: 1; }

/* ── Cards ── */
.section-card {
    display: flex;
    flex-direction: column;
    gap: 20px;
    padding: 24px 28px;
}

.section-title-row {
    display: flex;
    align-items: center;
    gap: 12px;
}

.section-icon-wrap {
    width: 36px;
    height: 36px;
    border-radius: var(--radius-md);
    background: var(--light-green);
    color: var(--forest-green);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.section-icon-wrap--pink {
    background: var(--light-pink);
    color: var(--primary-pink);
}

.section-icon-wrap .material-symbols-outlined { font-size: 18px; }

.section-title-row h2 {
    font-size: 15px;
    font-weight: 700;
    color: var(--text-main);
    margin-bottom: 2px;
}

.section-divider { height: 1px; background: var(--card-border); }

/* ── Fields ── */
.fields-grid { gap: 16px; }
.section-card .form-group { margin-bottom: 0; }
.section-card .form-group label {
    font-size: 12px;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
}

.read-field {
    padding: 11px 14px;
    border: 1px solid var(--card-border);
    border-radius: var(--radius-md);
    background: var(--gray-light);
    font-size: 14px;
    color: var(--text-muted);
}

.field-hint  { display: block; font-size: 11px; color: #d1d5db; margin-top: 4px; }
.field-error { display: block; font-size: 12px; color: #be123c;  margin-top: 4px; }

.input-with-btn { display: flex; gap: 8px; }
.input-with-btn .input-field { flex: 1; }

.btn-save {
    padding: 0 18px;
    font-size: 13px;
    white-space: nowrap;
    flex-shrink: 0;
    height: 44px;
}
.btn-save:disabled { opacity: 0.4; cursor: not-allowed; }

/* ── Password ── */
.password-wrapper { position: relative; }
.password-wrapper .input-field { padding-right: 42px; }

.toggle-btn {
    position: absolute;
    right: 10px;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    color: var(--text-muted);
    cursor: pointer;
    display: flex;
    align-items: center;
    padding: 4px;
    border-radius: 6px;
    transition: color 0.15s;
}
.toggle-btn:hover { color: var(--text-main); }
.toggle-btn .material-symbols-outlined { font-size: 18px; }

.btn-update-pw { align-self: flex-start; padding: 12px 28px; font-size: 14px; }
.btn-update-pw:disabled { opacity: 0.4; cursor: not-allowed; }

/* ── Notice ── */
.notice-box {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    background: var(--light-yellow);
    border: 1px solid #fde68a;
    border-radius: var(--radius-md);
    padding: 14px 16px;
    color: #92400e;
    font-size: 13px;
    line-height: 1.6;
}
.notice-box .material-symbols-outlined { font-size: 18px; flex-shrink: 0; margin-top: 1px; }

/* ── Transitions ── */
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* ── Responsive ── */
@media (max-width: 600px) {
    .page-banner-inner { padding: 20px 16px; gap: 14px; }
    .page-banner-inner h1 { font-size: 20px; }
    .user-avatar { width: 48px; height: 48px; font-size: 16px; }
    .role-badge { display: none; }
    .settings-body { padding: 20px 16px 40px; }
    .section-card { padding: 18px 16px; }
    .fields-grid { grid-template-columns: 1fr !important; }
    .input-with-btn { flex-direction: column; }
    .btn-save { height: auto; padding: 11px 18px; }
    .btn-update-pw { align-self: stretch; }
}
</style>