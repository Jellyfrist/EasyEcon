<template>
    <aside class="sidebar" :class="[complete ? 'complete-sidebar' : 'study-sidebar', { 'reader-sidebar': reader, 'sidebar-collapsed': reader && collapsed }]" aria-label="Lesson outline">
        <NavigationHeading v-if="reader" :title="dashboard.module.title" :collapsed="collapsed" @toggle="collapsed = !collapsed" />
        <div class="sidebar-header">
            <button class="nav-btn" type="button" :aria-label="reader ? 'All modules' : 'Back to Modules'" :title="reader && collapsed ? 'All modules' : undefined" @click="$emit('back')">
                <div class="back-icon-circle">
                    <span v-if="reader" class="material-symbols-outlined" aria-hidden="true">menu_book</span>
                    <svg v-else aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <line x1="19" y1="12" x2="5" y2="12"></line>
                        <polyline points="12 19 5 12 12 5"></polyline>
                    </svg>
                </div>
                <span v-show="!reader || !collapsed" class="nav-text">{{ reader ? 'All modules' : (complete ? 'Back to Modules' : 'Back to Module') }}</span>
            </button>
        </div>
        <div v-show="!reader || !collapsed" class="module-info">
            <p class="info-label">{{ complete ? 'MODULE COMPLETE' : 'CURRENT MODULE' }}</p>
            <h3 v-if="!reader" class="info-title">{{ dashboard.module.title }}</h3>
            <div class="progress-bar-wrap">
                <div class="progress-bar-fill" :style="{ width: progress + '%' }"></div>
            </div>
            <p class="progress-pct">PROGRESS: {{ progress }}%</p>
        </div>
        <div class="lesson-nav">
            <p class="nav-label">LESSONS</p>
            <div class="nav-list">
                <button v-for="(page, index) in dashboard.pages" :key="page.id" class="nav-item"
                    :class="{ active: !complete && page.id == pageId, completed: !complete && page.status === 'completed' }"
                    :aria-label="page.title" :title="reader && collapsed ? page.title : undefined"
                    :aria-current="!complete && page.id == pageId ? 'page' : undefined"
                    @click="!complete && $emit('select', page.id)">
                    <span class="material-symbols-outlined nav-icon" aria-hidden="true">
                        {{ complete ? 'check_circle' : (page.id == pageId ? 'radio_button_checked' : (page.status === 'completed' ? 'check_circle' : (reader ? 'description' : 'play_circle'))) }}
                    </span>
                    <span v-show="!reader || !collapsed" class="nav-item-text">{{ reader ? page.title : `${index + 1}. ${page.title}` }}</span>
                </button>
            </div>
        </div>
    </aside>
</template>

<script setup>
import NavigationHeading from '@/components/NavigationHeading.vue';
import { useCourseNavigation } from '@/composables/useCourseNavigation';
import { computed } from 'vue';

const props = defineProps({
    dashboard: { type: Object, required: true },
    pageId: { type: [String, Number], default: null },
    complete: { type: Boolean, default: false },
    reader: { type: Boolean, default: false },
});
defineEmits(['back', 'select']);
const { collapsed } = useCourseNavigation();
const progress = computed(() => props.complete ? 100 : props.dashboard.progress_percent);
</script>

<style scoped>
.material-symbols-outlined { vertical-align: middle; }
.study-sidebar {
    width: 300px;
    background-color: #df4a7d;
    border-radius: 24px;
    box-shadow: 0 10px 30px rgba(223, 74, 125, 0.1);
    display: flex;
    flex-direction: column;
    flex-shrink: 0;
    overflow-y: auto;
    height: 100%;
}

.study-sidebar .sidebar-header {
    padding: 2rem 1.5rem 1rem 1.5rem;
}

.study-sidebar .nav-btn {
    display: flex;
    align-items: center;
    gap: 12px;
    background: transparent;
    border: none;
    padding: 0;
    color: #ffffff;
    cursor: pointer;
    transition: all 0.2s ease;
    width: 100%;
    text-align: left;
}

.study-sidebar .back-icon-circle {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: 2px solid rgba(255, 255, 255, 0.4);
    color: #ffffff;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
}

.study-sidebar .nav-text {
    font-weight: 700;
    font-size: 1rem;
}

.study-sidebar .nav-btn:hover .back-icon-circle {
    background-color: rgba(255, 255, 255, 0.2);
    color: rgba(255, 255, 255, 0.8);
}

.study-sidebar .nav-btn:hover .nav-text {
    color: #e6e6e6;
}

.study-sidebar .module-info {
    padding: 1rem 1.5rem 1.5rem 1.5rem;
    border-bottom: 1px solid var(--theme-border-fce4ec);
}

.study-sidebar .info-label {
    font-size: 0.7rem;
    font-weight: 800;
    color: #e6e6e6;
    letter-spacing: 0.05em;
    margin: 0 0 6px;
}

.study-sidebar .info-title {
    font-size: 1.1rem;
    font-weight: 800;
    color: #ffffff;
    margin: 0 0 1rem;
    line-height: 1.4;
}

.study-sidebar .progress-bar-wrap {
    height: 6px;
    background: var(--theme-bg-fce4ec);
    border-radius: 6px;
    overflow: hidden;
    margin-bottom: 8px;
}

.study-sidebar .progress-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--theme-bg-ffc6da), var(--surface));
    border-radius: 6px;
    transition: width 0.4s ease;
}

.study-sidebar .progress-pct {
    font-size: 0.7rem;
    font-weight: 800;
    color: #e6e6e6;
    text-align: right;
    margin: 0;
    letter-spacing: 0.05em;
}

.study-sidebar .lesson-nav {
    padding: 1.5rem 1rem;
    flex: 1;
}

.study-sidebar .nav-label {
    font-size: 0.7rem;
    font-weight: 800;
    color: #e6e6e6;
    letter-spacing: 0.05em;
    margin: 0 0.5rem 10px;
}

.study-sidebar .nav-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

/* Sidebar Lesson Items */

.study-sidebar .nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 1rem 1.25rem;
    background: transparent;
    border-radius: 12px;
    border: 1px solid transparent;
    cursor: pointer;
    text-align: left;
    transition: all 0.2s ease;
    color: #ffffff;
    font-family: inherit;
}

.study-sidebar .nav-item:hover:not(.active) {
    background: rgba(255, 255, 255, 0.1);
    transform: translateX(2px);
}

.study-sidebar .nav-item.active {
    background: rgba(255, 255, 255, 0.2);
    /* color: var(--theme-fg-1f2937); */
    border: 1px solid rgba(255, 255, 255, 0.4);
    box-shadow: 0 4px 12px rgba(223, 74, 125, 0.08);
}

.study-sidebar .nav-item.completed .nav-icon {
    color: var(--theme-fg-00ffaa);
}

.study-sidebar .nav-item.active .nav-icon {
    color: var(--theme-fg-ff006a);
}

.study-sidebar .nav-icon {
    font-size: 20px;
    flex-shrink: 0;
    color: var(--theme-fg-9ca3af);
}

.study-sidebar .nav-item-text {
    font-size: 0.9rem;
    font-weight: 700;
    line-height: 1.4;
}

/* Custom Scrollbar for Sidebar */

.study-sidebar::-webkit-scrollbar {
    width: 4px;
}

.study-sidebar::-webkit-scrollbar-thumb {
    background-color: var(--theme-bg-f1c3d3);
    border-radius: 4px;
}

.sidebar.study-sidebar::-webkit-scrollbar-track {
    background-color: transparent;
}

/* =====================================================
   Main Content
   ===================================================== */


.complete-sidebar {
    width: 300px;
    background-color: #df4a7d;
    border-radius: 24px;
    box-shadow: 0 10px 30px rgba(223, 74, 125, 0.2);
    border: none;
    display: flex;
    flex-direction: column;
    flex-shrink: 0;
    height: calc(100vh - 4rem);
    position: sticky;
    top: 2rem;
    overflow: hidden;
}

.complete-sidebar .sidebar-header {
    padding: 2rem 1.5rem 1rem 1.5rem;
}

/* Back to Modules */

.complete-sidebar .nav-btn {
    display: flex;
    align-items: center;
    gap: 12px;
    background: transparent;
    border: none;
    padding: 0;
    color: #ffffff;
    cursor: pointer;
    transition: all 0.2s ease;
    width: 100%;
    text-align: left;
}

.complete-sidebar .back-icon-circle {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: 2px solid rgba(255, 255, 255, 0.4);
    color: #ffffff;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
}

.complete-sidebar .nav-text {
    font-weight: 700;
    font-size: 1rem;
}

.complete-sidebar .nav-btn:hover .back-icon-circle {
    background-color: rgba(255, 255, 255, 0.2);
    border-color: rgba(255, 255, 255, 0.8);
}

.complete-sidebar .nav-btn:hover .nav-text {
    opacity: 0.8;
}

.complete-sidebar .module-info {
    padding: 1rem 1.5rem 1.5rem 1.5rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.complete-sidebar .info-label {
    font-size: 0.7rem;
    font-weight: 800;
    color: rgba(255, 255, 255, 0.8);
    letter-spacing: 0.05em;
    margin: 0 0 6px;
}

.complete-sidebar .info-title {
    font-size: 1.1rem;
    font-weight: 800;
    color: #ffffff;
    margin: 0 0 1rem;
    line-height: 1.4;
}

.complete-sidebar .progress-bar-wrap {
    height: 6px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 6px;
    overflow: hidden;
    margin-bottom: 8px;
}

.complete-sidebar .progress-bar-fill {
    height: 100%;
    background: var(--surface);
    border-radius: 6px;
}

.complete-sidebar .progress-pct {
    font-size: 0.7rem;
    font-weight: 800;
    color: #ffffff;
    text-align: right;
    margin: 0;
    letter-spacing: 0.05em;
}

.complete-sidebar .lesson-nav {
    padding: 1.5rem 1rem;
    flex: 1;
    overflow-y: auto;
}

.complete-sidebar .lesson-nav::-webkit-scrollbar {
    width: 4px;
}

.complete-sidebar .lesson-nav::-webkit-scrollbar-thumb {
    background-color: rgba(255, 255, 255, 0.3);
    border-radius: 4px;
}

.complete-sidebar .nav-label {
    font-size: 0.7rem;
    font-weight: 800;
    color: rgba(255, 255, 255, 0.8);
    letter-spacing: 0.05em;
    margin: 0 0.5rem 10px;
}

.complete-sidebar .nav-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

/* Sidebar Lesson Items */

.complete-sidebar .nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 1rem 1.25rem;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    border: 1px solid transparent;
    text-align: left;
    color: #ffffff;
    font-family: inherit;
}

.complete-sidebar .nav-icon {
    font-size: 20px;
    flex-shrink: 0;
    color: #ffffff;
}

.complete-sidebar .nav-item-text {
    font-size: 0.9rem;
    font-weight: 700;
    line-height: 1.4;
    opacity: 0.9;
}

/* =====================================================
   Main Content Area
   ===================================================== */


/* Match the course navigation; retain the completion layout. */
.reader-sidebar { width: 260px; min-width: 0; height: 100%; padding: 24px 0; overflow-y: auto; background: var(--surface); border-right: 1px solid var(--card-border); border-radius: 0; box-shadow: none; font-family: 'Kanit', sans-serif; }
.reader-sidebar .sidebar-header { order: 1; padding: 0; }
.reader-sidebar .nav-btn { transition: background-color 0.15s, color 0.15s; color: var(--text-muted); gap: 8px; min-height: 44px; padding: 10px 20px; }
.reader-sidebar .back-icon-circle { width: 18px; height: 18px; border: 0; color: inherit; flex-shrink: 0; }
.reader-sidebar .nav-text { font-size: 0.85rem; font-weight: 400; }
.reader-sidebar .nav-btn:hover { background: var(--gray-light); color: var(--primary-pink); }
.reader-sidebar .nav-btn:hover .back-icon-circle { background: transparent; color: inherit; }
.reader-sidebar .nav-btn:hover .nav-text { color: inherit; }
.reader-sidebar .module-info { order: 0; padding: 0 20px 12px; border: 0; }
.reader-sidebar .info-label, .reader-sidebar .nav-label, .reader-sidebar .progress-bar-wrap { display: none; }
.reader-sidebar .progress-pct { text-align: left; margin: 0; color: var(--text-muted); font-weight: 500; font-size: 0.75rem; }
.reader-sidebar .lesson-nav { order: 2; padding: 0; }
.reader-sidebar .nav-list { gap: 0; }
.reader-sidebar .nav-item { transition: background-color 0.15s, color 0.15s; width: 100%; min-height: 44px; padding: 10px 20px; gap: 8px; color: var(--text-muted); border: 0; border-radius: 0; box-shadow: none; }
.reader-sidebar .nav-item:hover:not(.active) { background: var(--gray-light); color: var(--primary-pink); transform: none; }
.reader-sidebar .nav-item.active { color: var(--white); background: var(--primary-pink); border: 0; box-shadow: none; }
.reader-sidebar .nav-item.completed .nav-icon { color: var(--text-green); }
.reader-sidebar .nav-item.active .nav-icon { color: var(--white); }
.reader-sidebar .nav-icon { font-size: 18px; color: inherit; }
.reader-sidebar .nav-item-text { font-size: 0.85rem; font-weight: 400; line-height: 1.5; }
.reader-sidebar :is(.nav-item, .nav-btn):focus-visible { outline: 2px solid var(--primary-pink); outline-offset: -2px; }
.reader-sidebar.sidebar-collapsed { width: 72px; padding: 16px 8px; }
.reader-sidebar.sidebar-collapsed .nav-list { align-items: center; gap: 8px; }
.reader-sidebar.sidebar-collapsed :is(.nav-item, .nav-btn) { width: 44px; height: 44px; padding: 0; justify-content: center; border-radius: 8px; }
.reader-sidebar.sidebar-collapsed .sidebar-header { margin: 0 auto 8px; }
</style>
