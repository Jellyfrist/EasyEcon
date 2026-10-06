<template>
    <div class="layout-wrapper" :class="{ 'reader-navigation-collapsed': collapsed }" :style="{ '--navbar-offset': `${navbarOffset}px` }">
        <button class="outline-toggle" :aria-expanded="showOutline" aria-controls="lesson-outline" @click="showOutline = !showOutline">
            <span class="material-symbols-outlined" aria-hidden="true">menu_book</span> Lessons
            <span class="material-symbols-outlined" aria-hidden="true">{{ showOutline ? 'close' : 'expand_more' }}</span>
        </button>

        <LearningLessonSidebar v-if="dashboardData" id="lesson-outline" reader :class="{ 'outline-open': showOutline }"
            :dashboard="dashboardData" :page-id="pageId"
            @back="router.push({ name: 'ModulesList', params: { courseId } })"
            @select="goToLesson" />

        <main class="main-content" id="main-scroll">

            <div v-if="pageData" class="study-container">

                    <article class="content-article">
                        <h1 class="lesson-title">{{ pageData.title }}</h1>

                        <div v-for="(block, blockIndex) in pageData.content_blocks" :key="block.id" class="content-block">

                            <div v-if="block.type === 'rich_text_section'" class="rich-text">
                                <LessonRichText :html="block.data.html" :omit-leading-title="blockIndex === 0 ? pageData.title : ''" class="html-content" />
                            </div>

                        </div>
                        <button v-if="!isLastPage" class="up-next" @click="handleNext">
                            <span class="material-symbols-outlined" aria-hidden="true">arrow_forward</span>
                            <span><small>UP NEXT</small><strong>{{ dashboardData?.pages[currentIndex + 1]?.title }}</strong></span>
                            <span class="material-symbols-outlined" aria-hidden="true">chevron_right</span>
                        </button>
                    </article>

            </div>

            <div v-else-if="dashboardData && dashboardData.pages.length === 0" class="loading-state">
                <span class="material-symbols-outlined" aria-hidden="true">menu_book</span>
                <p>No published lessons in this module yet.</p>
                <router-link :to="{ name: 'ModulesList', params: { courseId } }">Back to modules</router-link>
            </div>
            <div v-else class="loading-state">
                <div class="spinner"></div>
                <p>Preparing lesson...</p>
            </div>

        </main>
        <footer v-if="pageData" class="bottom-nav" aria-label="Lesson navigation">
            <button class="prev-btn" :class="{ invisible: currentIndex === 0 }" @click="goPrevLesson">
                <span class="material-symbols-outlined" aria-hidden="true">chevron_left</span> Previous
            </button>
            <span class="lesson-position">{{ currentIndex + 1 }} / {{ dashboardData?.pages.length || 0 }}</span>
            <button @click="handleNext" class="next-btn">
                {{ isLastPage ? 'Finish Module' : 'Next Lesson' }}
                <span class="material-symbols-outlined" aria-hidden="true">chevron_right</span>
            </button>
        </footer>
    </div>
</template>

<script setup>
import { useCourseNavigation } from '@/composables/useCourseNavigation';
import { useNavbarOffset } from '@/composables/useNavbarOffset';
import LessonRichText from '@/components/LessonRichText.vue';
import LearningLessonSidebar from '@/components/LearningLessonSidebar.vue';
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import learningService from '@/services/learningService';
import { useLearningStore } from '@/store/learningStore';

const route = useRoute();
const router = useRouter();
const learningStore = useLearningStore();
const navbarOffset = useNavbarOffset();
const { collapsed } = useCourseNavigation();
const showOutline = ref(false);

const courseId = computed(() => route.params.courseId);
const moduleId = computed(() => route.params.moduleId);
const pageId = computed(() => route.params.pageId);

const pageData = ref(null);
const dashboardData = ref(null);
const timeSpent = ref(0);
let timer = null;

const currentIndex = computed(() => {
    if (!dashboardData.value || !dashboardData.value.pages) return 0;
    return dashboardData.value.pages.findIndex(p => p.id == pageId.value);
});

const isLastPage = computed(() => {
    if (!dashboardData.value || !dashboardData.value.pages) return true;
    return currentIndex.value >= dashboardData.value.pages.length - 1;
});

const loadSidebarData = async () => {
    try {
        const res = await learningStore.fetchModuleDashboard(moduleId.value);
        if (res && res.chapterInfo) {
            dashboardData.value = {
                module: { title: res.chapterInfo.title },
                progress_percent: res.chapterInfo.progressPercent,
                pages: res.lessons
            };
        }
    } catch (error) {
        console.error("Sidebar Load Error:", error);
    }
};

const loadLesson = async (pId) => {
    pageData.value = null;

    try {
        const res = await learningService.studyPage(pId);
        pageData.value = res.data;

        timeSpent.value = 0;
        if (timer) clearInterval(timer);
        timer = setInterval(() => { timeSpent.value += 1; }, 1000);

        const mainScroll = document.getElementById('main-scroll');
        if (mainScroll) mainScroll.scrollTop = 0;

    } catch (err) {
        console.error("Failed to load lesson data", err);
    }
};

const openModule = async () => {
    pageData.value = null;
    if (timer) clearInterval(timer);
    await loadSidebarData();
    if (pageId.value) {
        await loadLesson(pageId.value);
    } else {
        const firstPage = dashboardData.value?.pages.find(page => page.status !== 'locked');
        if (firstPage) {
            router.replace({ name: 'LearningChapter', params: {
                courseId: courseId.value, moduleId: moduleId.value, pageId: firstPage.id,
            } });
        }
    }
};

onMounted(openModule);

onUnmounted(() => {
    if (timer) clearInterval(timer);
});

watch([moduleId, pageId], openModule);

const goToLesson = (pId) => {
    showOutline.value = false;
    if (pId == pageId.value) return;
    router.push({
        name: 'LearningChapter',
        params: {
            courseId: courseId.value,
            moduleId: moduleId.value,
            pageId: pId
        }
    });
};

const goPrevLesson = () => {
    if (currentIndex.value > 0) {
        const prevId = dashboardData.value.pages[currentIndex.value - 1].id;
        goToLesson(prevId);
    }
};

const handleNext = async () => {
    try {
        try {
            await learningStore.completePage(pageId.value);
        } catch (apiErr) {}

        if (!isLastPage.value) {
            const nextId = dashboardData.value.pages[currentIndex.value + 1].id;
            goToLesson(nextId);
        } else {
            router.push(`/student/courses/${courseId.value}/modules/${moduleId.value}?completed=true&time=${timeSpent.value}`);
        }
    } catch (err) {
        console.error(err);
    }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&family=Sarabun:wght@400;500;600;700;800&display=swap');
/* =====================================================
   Layout Wrapper
   ===================================================== */

.layout-wrapper {
    position: fixed;
    inset: var(--navbar-offset, 64px) 0 0;
    display: grid;
    grid-template-columns: 260px minmax(0, 1fr);
    grid-template-rows: minmax(0, 1fr) 44px;
    background: var(--surface);
    font-family: 'DM Sans', 'Sarabun', sans-serif;
    overflow: hidden;
}
.layout-wrapper.reader-navigation-collapsed { grid-template-columns: 72px minmax(0, 1fr); }
.material-symbols-outlined { vertical-align: middle; }
.outline-toggle { display: none; }
.main-content {
    grid-column: 2;
    grid-row: 1;
    min-width: 0;
    overflow-y: auto;
    scroll-behavior: smooth;
}
.study-container {
    width: min(100%, 800px);
    margin: 0 auto;
    padding: 24px 40px 48px;
}

.content-block { margin-bottom: 32px; }
.up-next { display: flex; align-items: center; gap: 16px; width: 100%; max-width: 560px; margin: 32px auto 0; padding: 20px 24px; border: 0; border-radius: var(--radius-lg); background: var(--contrast-surface); color: var(--white); text-align: left; font: inherit; cursor: pointer; }
.up-next > span:first-child { padding: 12px; border-radius: 8px; background: var(--primary-pink); }
.up-next > span:last-child { margin-left: auto; }
.up-next small { display: block; color: var(--primary-yellow); font-size: 0.65rem; letter-spacing: 0.08em; }
.up-next strong { font-size: 0.95rem; font-weight: 500; }
.up-next:focus-visible { outline: 2px solid var(--primary-pink); outline-offset: 3px; }
.lesson-title { font-size: 1.8rem; font-weight: 400; line-height: 1.4; margin: 0 0 24px; overflow-wrap: anywhere; }

/* =====================================================
   Bottom Navigation
   ===================================================== */

.bottom-nav {
    grid-column: 1 / -1;
    grid-row: 2;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding: 4px 12px;
    border-top: 1px solid var(--card-border);
    background: var(--surface);
    z-index: 2;
}
.invisible { visibility: hidden; }
.prev-btn, .next-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    min-height: 32px;
    padding: 4px 10px;
    border: 0;
    border-radius: 3px;
    font-family: inherit;
    font-size: 0.75rem;
    cursor: pointer;
}
.prev-btn { background: var(--surface); color: var(--primary-pink); }
.prev-btn:hover { background: var(--theme-bg-fff0f5); }
.next-btn { background: var(--primary-pink); color: white; }
.next-btn:hover { background: #c83264; }
.lesson-position { font-size: 0.8rem; color: var(--text-muted); }
.prev-btn:focus-visible, .next-btn:focus-visible, .outline-toggle:focus-visible {
    outline: 2px solid var(--primary-pink);
    outline-offset: 2px;
}

/* loading */

.loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    gap: 1rem;
    color: var(--theme-fg-9ca3af);
    font-weight: 600;
}

.spinner {
    width: 44px;
    height: 44px;
    border: 4px solid var(--theme-border-fce4ec);
    border-top-color: #df4a7d;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
}

@keyframes spin {
    100% {
        transform: rotate(360deg);
    }
}

/* responsive */
@media (max-width: 768px) {
    .layout-wrapper, .layout-wrapper.reader-navigation-collapsed {
        grid-template-columns: minmax(0, 1fr);
        grid-template-rows: 48px minmax(0, 1fr) 44px;
    }
    .outline-toggle {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 0 20px;
        border: 0;
        border-bottom: 1px solid var(--card-border);
        background: var(--surface);
        color: var(--primary-pink);
        font: inherit;
        cursor: pointer;
    }
    .outline-toggle span:last-child { margin-left: auto; }
    .layout-wrapper > .sidebar {
        display: none;
        position: absolute;
        top: 48px;
        bottom: 44px;
        left: 0;
        width: min(320px, 90%);
        height: auto;
        z-index: 3;
        box-shadow: 8px 0 24px rgba(0, 0, 0, 0.08);
    }
    .layout-wrapper > .sidebar.outline-open { display: flex; }
    .layout-wrapper > .sidebar.sidebar-collapsed { width: 72px; }
    .main-content { grid-column: 1; grid-row: 2; }
    .bottom-nav { grid-row: 3; padding-inline: 12px; }
    .study-container { padding: 24px 20px 40px; }

}
@media (prefers-reduced-motion: reduce) {
    .main-content { scroll-behavior: auto; }
}
</style>
