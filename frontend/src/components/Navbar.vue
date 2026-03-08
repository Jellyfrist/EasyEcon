<template>
    <nav class="navbar">
        <div class="container">
            <div class="nav-left">
                <!-- Logo: route to each role dashboard -->
                <div v-if="authStore.isStudent">
                    <router-link to="/dashboard" class="logo-box">
                        <div class="logo-icon">
                            <img src="@/assets/EasyEcon_logo_pink.png" alt="EasyEcon Logo" class="logo-icon" />
                        </div>
                        <div class="logo-text">
                            <span>Easy</span>
                            <span class="pink">Econ</span>
                        </div>
                    </router-link>
                </div>
                <div v-else-if="authStore.isTeacher">
                    <router-link to="/teacher" class="logo-box">
                        <div class="logo-icon">
                            <img src="@/assets/EasyEcon_logo_pink.png" alt="EasyEcon Logo" class="logo-icon" />
                        </div>
                        <div class="logo-text">
                            <span>Easy</span>
                            <span class="pink">Econ</span>
                        </div>
                    </router-link>
                </div>
                <div v-else-if="authStore.isAdmin">
                    <router-link to="/admin" class="logo-box">
                        <div class="logo-icon">
                            <img src="@/assets/EasyEcon_logo_pink.png" alt="EasyEcon Logo" class="logo-icon" />
                        </div>
                        <div class="logo-text">
                            <span>Easy</span>
                            <span class="pink">Econ</span>
                        </div>
                    </router-link>
                </div>

                <!-- Study Tools --
                <div class="nav-item dropdown" v-if="!authStore.isAdmin">
                    <button class="nav-link" @click.stop="toggleDropdown('tools')">
                        Study tools
                        <span class="material-symbols-outlined">expand_more</span>
                    </button>
                    <div v-if="activeDropdown === 'tools'" class="dropdown-menu">
                        <template v-if="authStore.isStudent">
                            <router-link to="/flashcards" class="dropdown-item" @click="activeDropdown = null">Flashcards</router-link>
                            <router-link to="/learning" class="dropdown-item" @click="activeDropdown = null">Learn</router-link>
                            <router-link to="/test" class="dropdown-item" @click="activeDropdown = null">Practice Tests</router-link>
                        </template>
                        <template v-else-if="authStore.isTeacher">
                            <router-link to="/teacher/flashcards" class="dropdown-item" @click="activeDropdown = null">Flashcards</router-link>
                            <router-link to="/teacher/learning" class="dropdown-item" @click="activeDropdown = null">Learn</router-link>
                            <router-link to="/teacher/test" class="dropdown-item" @click="activeDropdown = null">Practice Tests</router-link>
                        </template>
                    </div>
                </div>
                -->
            </div>

            <div class="nav-center" v-if="!authStore.isAdmin">
                <div class="search-box" v-click-outside="closeSearch">
                    <span class="material-symbols-outlined search-icon">search</span>
                    <input
                        type="text"
                        placeholder="Search flashcard sets, learning topics, tests..."
                        v-model="searchQuery"
                        @focus="isSearchFocused = true"
                        @input="onSearchInput"
                        @keydown.escape="closeSearch"
                    />

                    <!-- Dropdown results -->
                    <div v-if="isSearchFocused && searchQuery.length > 0" class="search-dropdown">

                        <!-- Loading -->
                        <div v-if="isSearching" class="search-loading">
                            <span class="material-symbols-outlined spinning">progress_activity</span>
                            Searching...
                        </div>

                        <!-- No results -->
                        <div v-else-if="searchResults.total === 0 && !isSearching" class="search-empty">
                            No results for "{{ searchQuery }}"
                        </div>

                        <!-- Results by category -->
                        <template v-else>
                            <div v-if="searchResults.courses.length" class="search-group">
                                <div class="search-group-label">
                                    <span class="material-symbols-outlined">school</span> Courses
                                </div>
                                <div
                                    v-for="item in searchResults.courses"
                                    :key="`course-${item.id}`"
                                    class="search-item"
                                    @mousedown="goToResult(item)"
                                >
                                    {{ item.title }}
                                    <span v-if="item.description" class="search-item-desc">{{ item.description }}</span>
                                </div>
                            </div>

                            <div v-if="searchResults.flashcards.length" class="search-group">
                                <div class="search-group-label">
                                    <span class="material-symbols-outlined">style</span> Flashcards
                                </div>
                                <div
                                    v-for="item in searchResults.flashcards"
                                    :key="`flash-${item.id}`"
                                    class="search-item"
                                    @mousedown="goToResult(item)"
                                >
                                    {{ item.title }}
                                </div>
                            </div>

                            <div v-if="searchResults.learning.length" class="search-group">
                                <div class="search-group-label">
                                    <span class="material-symbols-outlined">menu_book</span> Learning
                                </div>
                                <div
                                    v-for="item in searchResults.learning"
                                    :key="`learn-${item.id}`"
                                    class="search-item"
                                    @mousedown="goToResult(item)"
                                >
                                    {{ item.title }}
                                </div>
                            </div>

                            <div v-if="searchResults.exams.length" class="search-group">
                                <div class="search-group-label">
                                    <span class="material-symbols-outlined">quiz</span> Practice Tests
                                </div>
                                <div
                                    v-for="item in searchResults.exams"
                                    :key="`exam-${item.id}`"
                                    class="search-item"
                                    @mousedown="goToResult(item)"
                                >
                                    {{ item.title }}
                                </div>
                            </div>
                        </template>
                    </div>
                </div>
            </div>

            <div class="nav-right">
                <div v-if="authStore.isAuthenticated" class="user-menu">
                    <div class="user-info" @click.stop="toggleDropdown('user')">
                        <span class="material-symbols-outlined dropdown-arrow pink">expand_more</span>

                        <div class="user-meta">
                            <div class="user-name">
                                <span v-if="authStore.isAdmin">Admin</span>
                                <span v-else>{{ authStore.fullName }}</span>
                            </div>
                            <div class="user-email" v-if="!authStore.isAdmin">{{ authStore.email }}</div>
                        </div>

                        <div class="user-avatar">
                            <span v-if="authStore.isAdmin" class="material-symbols-outlined">shield_person</span>
                            <span v-else>{{ userInitials }}</span>
                        </div>
                    </div>

                    <div v-if="activeDropdown === 'user'" class="dropdown-menu dropdown-right">
                        <!-- Student -->
                        <template v-if="authStore.isStudent">
                            <router-link to="/courses" class="dropdown-item" @click="activeDropdown = null">
                                <span class="material-symbols-outlined">school</span> Courses
                            </router-link>
                            <router-link to="/settings" class="dropdown-item" @click="activeDropdown = null">
                                <span class="material-symbols-outlined">settings</span> Settings
                            </router-link>
                        </template>

                        <!-- Student -->
                        <template v-if="authStore.isTeacher">
                            <router-link to="/teacher/courses" class="dropdown-item" @click="activeDropdown = null">
                                <span class="material-symbols-outlined">school</span> Courses
                            </router-link>
                            <router-link to="/settings" class="dropdown-item" @click="activeDropdown = null">
                                <span class="material-symbols-outlined">settings</span> Settings
                            </router-link>
                        </template>

                        <div class="dropdown-divider"></div>

                        <button @click="handleLogout" class="dropdown-item logout">
                            <span class="material-symbols-outlined">logout</span>
                            Log out
                        </button>
                    </div>
                </div>

                <!--If not authenticated -->
                <router-link v-else to="/login" class="btn-login">
                    Log in
                </router-link>
            </div>
        </div>
    </nav>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/store/authStore';

const router = useRouter()
const route = useRoute();
const authStore = useAuthStore();

const activeDropdown = ref(null);

// userInitials
const userInitials = computed(() => {
    if (authStore.isAdmin) return '';

    const name = authStore.fullName
    const parts = name.trim().split(' ');
    if (parts.length >= 2) {
        return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    }
    return parts[0]?.[0]?.toUpperCase() ?? '?';
});

// Dropdown
const toggleDropdown = (dropdown) => {
    activeDropdown.value = activeDropdown.value === dropdown ? null : dropdown;
};

const closeDropdowns = (e) => {
    if (!e.target.closest('.dropdown') && !e.target.closest('.user-menu')) {
        activeDropdown.value = null;
    }
};

// Logout
const handleLogout = async () => {
    activeDropdown.value = null;
    await authStore.logout(true);
};

// Search
const searchQuery = ref('')
const isSearchFocused = ref(false)
const isSearching = ref(false)
const searchResults = ref({ courses: [], flashcards: [], learning: [], exams: [], total: 0 })

let debounceTimer = null

const onSearchInput = () => {
    clearTimeout(debounceTimer)
    if (searchQuery.value.trim().length < 1) {
        searchResults.value = { courses: [], flashcards: [], learning: [], exams: [], total: 0 }
        return
    }
    isSearching.value = true
    debounceTimer = setTimeout(() => fetchSearch(), 350)
}

const fetchSearch = async () => {
    try {
        const endpoint = authStore.isTeacher
            ? `${BACKEND_URL}/search/teacher`
            : `${BACKEND_URL}/search/student`

        const { data } = await axios.get(endpoint, {
            params: { q: searchQuery.value.trim() }
        })
        searchResults.value = data
    } catch (err) {
        console.error('Search error:', err)
    } finally {
        isSearching.value = false
    }
}

const goToResult = (item) => {
    closeSearch()

    if (authStore.isStudent) {
        const routes = {
            course:    `/courses/${item.id}`,
            flashcard: `/flashcards/${item.course_id}`,
            learning:  `/courses/${item.course_id}/modules`,
            exam:      `/exam/${item.course_id}`,
        }
        router.push(routes[item.type] ?? '/dashboard')

    } else if (authStore.isTeacher) {
        const routes = {
            course:    `/teacher/courses/${item.id}/edit`,
            flashcard: `/teacher/flashcards/${item.course_id}`,
            learning:  `/teacher/learning/${item.course_id}`,
            exam:      `/teacher/exam/${item.course_id}`,
        }
        router.push(routes[item.type] ?? '/teacher')
    }
}

const closeSearch = () => {
    isSearchFocused.value = false
    searchQuery.value = ''
    searchResults.value = { courses: [], flashcards: [], learning: [], exams: [], total: 0 }
}

// Route watch
watch(() => route.path, () => {
    authStore.refreshUser();
});

onMounted(() => {
    document.addEventListener('click', closeDropdowns);
    authStore.refreshUser();
});

onUnmounted(() => {
    document.removeEventListener('click', closeDropdowns);
});

</script>

<style scoped>
.navbar {
    background: white;
    border-bottom: 1px solid #e5e7eb;
    padding: 0;
    position: sticky;
    top: 0;
    z-index: 1000;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.container {
    max-width: 100%;
    margin: 0 auto;
    padding: 0 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 64px;
}

/* Left Section */

.nav-left {
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Logo */

.logo-box {
    display: flex;
    align-items: center;
    gap: 3px;
    text-decoration: none;
    padding: 6px 6px;
    border-radius: 10px;
    transition: background 0.2s;
}

.logo-box:hover {
    background: #f9fafb;
}

.logo-icon {
    width: 60px;
    height: 45px;
    border-radius: 3px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.material-symbols-outlined {
    font-size: 24px;
}

.logo-text {
    display: flex;
    align-items: baseline;
    font-weight: 900;
    font-size: 25px;
    color: black;
}

.pink {
    color: var(--primary-pink);
}

/* Navigation Items */

.nav-item {
    position: relative;
}

.nav-link {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 8px 12px;
    background: none;
    border: none;
    font-size: 14px;
    font-weight: 500;
    color: #4b5563;
    cursor: pointer;
    border-radius: 6px;
    transition: all 0.2s;
}

.nav-link:hover {
    background: #f3f4f6;
    color: #1f2937;
}

.nav-link .material-symbols-outlined {
    font-size: 20px;
}

/* Dropdown Menu */

.dropdown-menu {
    position: absolute;
    top: calc(100% + 8px);
    left: 0;
    background: white;
    border-radius: 12px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
    padding: 8px;
    min-width: 200px;
    z-index: 100;
    animation: slideDown 0.2s ease-out;
}

.dropdown-right {
    left: auto;
    right: 0;
    min-width: 240px;
}

@keyframes slideDown {
    from {
        opacity: 0;
        transform: translateY(-10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.dropdown-item {
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%;
    padding: 10px 12px;
    background: none;
    border: none;
    border-radius: 8px;
    font-size: 14px;
    color: #374151;
    text-decoration: none;
    cursor: pointer;
    transition: background 0.2s;
    text-align: left;
}

.dropdown-item:hover {
    background: #f3f4f6;
}

.dropdown-item .material-symbols-outlined {
    font-size: 20px;
    color: #6b7280;
}

.dropdown-item.logout {
    color: #ef4444;
}

.dropdown-item.logout:hover {
    background: #fef2f2;
}

.dropdown-divider {
    height: 1px;
    background: #e5e7eb;
    margin: 8px 0;
}

/* ----- User Info ----- */

.user-info {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 14px;
    border-radius: 14px;
    cursor: pointer;
    transition: all 0.25s ease;
}

.user-info:hover {
    background: rgba(0, 0, 0, 0.05);
}

/* User Avatar */

.user-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 14px;
    color: white;
    background: linear-gradient(135deg, #ff4d8d, #e91e63);
}

.user-avatar:hover {
    transform: scale(1.05);
}

/* Meta */

.user-meta {
    display: flex;
    flex-direction: column;
    line-height: 1.2;
    text-align: right;
}

.user-name {
    font-weight: 600;
    font-size: 14px;
    color: var(--text--main);
}

.user-email {
    font-size: 12px;
    color: var(--text--muted);
}

/* Center Section - Search */
.nav-center {
    flex: 1;
    max-width: 40%;
    margin: 0 20px;
    position: relative; /* ย้าย relative มาไว้ที่นี่แทน */
}

.search-box {
    display: flex;
    align-items: center;
    gap: 10px;
    background: #f3f4f6;
    padding: 10px 16px;
    border-radius: 24px;
    transition: all 0.2s;
    /* ลบ position: relative ออกจากที่นี่ */
}

.search-dropdown {
    position: absolute;
    top: calc(100% + 8px);
    left: 0;
    right: 0;        /* กว้างเท่า .nav-center เป๊ะ */
    background: white;
    border-radius: 16px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
    border: 1px solid var(--card-border);
    padding: 8px;
    z-index: 200;
    max-height: 420px;
    overflow-y: auto;
    animation: slideDown 0.2s ease-out;
}

.search-box:focus-within {
    background: white;
    box-shadow: 0 0 0 2px var(--primary-pink);
}

.search-icon {
    font-size: 20px;
    color: #9ca3af;
}

.search-box input {
    flex: 1;
    border: none;
    background: none;
    outline: none;
    font-size: 14px;
    color: #1f2937;
}

.search-box input::placeholder {
    color: #9ca3af;
}

/* Right Section */

.nav-right {
    display: flex;
    align-items: center;
    gap: 12px;
}

/* Icon Button */

.icon-btn {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    border: none;
    background: none;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    color: #6b7280;
    transition: all 0.2s;
}

.icon-btn:hover {
    background: #f3f4f6;
    color: #1f2937;
}

/* Login Button */

.btn-login {
    padding: 8px 20px;
    background: #ec4899;
    color: white;
    border-radius: 20px;
    font-size: 14px;
    font-weight: 600;
    text-decoration: none;
    transition: background 0.2s;
}

.btn-login:hover {
    background: #db2777;
}

/* Responsive */

@media (max-width: 768px) {
    .nav-center {
        display: none;
    }
    .nav-item {
        display: none;
    }
    .logo-text {
        font-size: 16px;
    }
}

@media (max-width: 480px) {
    .logo-icon {
        width: 32px;
        height: 32px;
    }
    .logo-icon .material-symbols-outlined {
        font-size: 20px;
    }
}
</style>