<template>
    <aside class="sidebar" :class="[complete ? 'complete-sidebar' : 'study-sidebar', { 'reader-sidebar': reader }]" aria-label="Lesson outline">
        <div class="sidebar-header">
            <button class="nav-btn" @click="$emit('back')">
                <div class="back-icon-circle">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <line x1="19" y1="12" x2="5" y2="12"></line>
                        <polyline points="12 19 5 12 12 5"></polyline>
                    </svg>
                </div>
                <span class="nav-text">{{ reader ? 'All modules' : (complete ? 'Back to Modules' : 'Back to Module') }}</span>
            </button>
        </div>
        <div class="module-info">
            <p class="info-label">{{ complete ? 'MODULE COMPLETE' : 'CURRENT MODULE' }}</p>
            <h3 class="info-title">{{ dashboard.module.title }}</h3>
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
                    :aria-current="!complete && page.id == pageId ? 'page' : undefined"
                    @click="!complete && $emit('select', page.id)">
                    <span class="material-symbols-outlined nav-icon" aria-hidden="true">
                        {{ complete ? 'check_circle' : (page.id == pageId ? 'radio_button_checked' : (page.status === 'completed' ? 'check_circle' : (reader ? 'radio_button_unchecked' : 'play_circle'))) }}
                    </span>
                    <span v-if="reader" class="material-symbols-outlined lesson-document-icon" aria-hidden="true">description</span>
                    <span class="nav-item-text">{{ reader ? page.title : `${index + 1}. ${page.title}` }}</span>
                </button>
            </div>
        </div>
    </aside>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
    dashboard: { type: Object, required: true },
    pageId: { type: [String, Number], default: null },
    complete: { type: Boolean, default: false },
    reader: { type: Boolean, default: false },
});
defineEmits(['back', 'select']);
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


/* Flat outline for the lesson reader; completion layout remains unchanged. */
.reader-sidebar {
    width: 260px;
    min-width: 0;
    height: 100%;
    overflow-y: auto;
    background: var(--surface);
    border-right: 1px solid var(--card-border);
    border-radius: 0;
    box-shadow: none;
}
.reader-sidebar .sidebar-header { order: 1; padding: 0 12px; }
.reader-sidebar .nav-btn { color: var(--primary-pink); gap: 8px; min-height: 28px; }
.reader-sidebar .back-icon-circle { width: 20px; height: 20px; border: 0; color: inherit; }
.reader-sidebar .nav-text { font-size: 0.8rem; font-weight: 500; }
.reader-sidebar .nav-btn:hover .back-icon-circle { background: transparent; color: inherit; }
.reader-sidebar .nav-btn:hover .nav-text { color: var(--primary-pink); }
.reader-sidebar .module-info { order: 0; padding: 16px 12px 0; border: 0; }
.reader-sidebar .info-label, .reader-sidebar .nav-label, .reader-sidebar .progress-bar-wrap { display: none; }
.reader-sidebar .info-label, .reader-sidebar .nav-label { color: var(--text-muted); font-size: 0.65rem; }
.reader-sidebar .info-title { color: var(--text-main); font-size: 1.5rem; line-height: 1.25; font-weight: 400; overflow-wrap: anywhere; }
.reader-sidebar .progress-bar-wrap { height: 4px; background: var(--theme-bg-f3f4f6); }
.reader-sidebar .progress-bar-fill { background: var(--primary-pink); }
.reader-sidebar .progress-pct { text-align: left; margin: 4px 0; color: var(--text-muted); font-weight: 500; font-size: 0.65rem; }
.reader-sidebar .lesson-nav { order: 2; padding: 8px 0; }
.reader-sidebar .nav-label { margin: 0 20px 12px; }
.reader-sidebar .nav-list { gap: 0; }
.reader-sidebar .nav-item {
    width: 100%;
    min-height: 34px;
    padding: 6px 12px;
    gap: 8px;
    color: var(--text-main);
    border: 0;
    border-radius: 0;
    box-shadow: none;
}
.reader-sidebar .nav-item:hover:not(.active) { background: var(--theme-bg-fff0f5); transform: none; }
.reader-sidebar .nav-item.active { color: white; background: var(--primary-pink); border: 0; box-shadow: none; }
.reader-sidebar .nav-item.completed .nav-icon { color: var(--text-green); }
.reader-sidebar .nav-item.active .nav-icon { color: white; }
.reader-sidebar .nav-icon { font-size: 14px; }
.reader-sidebar .lesson-document-icon { font-size: 16px; color: var(--primary-pink); }
.reader-sidebar .nav-item.active .lesson-document-icon { color: white; }
.reader-sidebar .nav-item-text { font-size: 0.8rem; font-weight: 400; line-height: 1.5; }
.reader-sidebar .nav-item:focus-visible { outline: 2px solid var(--primary-pink); outline-offset: -2px; }
</style>
