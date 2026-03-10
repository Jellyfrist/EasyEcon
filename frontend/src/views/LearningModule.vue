<template>
    <div class="cd-root">
    
        <main class="cd-container">
    
            <div class="cd-hero">
                <div class="cd-hero-top">
                    <button @click="router.push(`/teacher/learning/${courseId}`)" class="back-btn">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M19 12H5M12 5l-7 7 7 7"/>
                    </svg>
                  </button>
                    <div class="cd-breadcrumb">
                        <span class="cd-label clickable" @click="router.push(`/teacher/learning/${courseId}`)">Learning Overview</span>
                        <span class="separator">›</span>
                        <span class="cd-label">Manage Modules</span>
                    </div>
                </div>
    
                <div class="cd-hero-inner">
                    <h1 class="cd-title">Manage Course Structure</h1>
                    <p class="cd-desc">Create main modules and manage lesson content for your course.</p>
                </div>
            </div>
    
            <div class="cd-body">
    
                <div class="action-card">
                    <div class="card-header">
                        <div class="icon-box icon-rose">
                            <span class="material-symbols-outlined">add_box</span>
                        </div>
                        <div class="header-text">
                            <h2>1. Create a New Module</h2>
                            <p class="card-desc">Create a module folder first to organise your lesson content inside.</p>
                        </div>
                    </div>
    
                    <div class="create-form">
                        <input v-model="newModuleTitle" type="text" placeholder="Module name, e.g. Chapter 1: Introduction to Economics" class="input-module" @keyup.enter="createModule">
                        <button @click="createModule" :disabled="isCreating" class="btn-create">
                              <span v-if="!isCreating" class="material-symbols-outlined">add_circle</span>
                              <span v-else class="material-symbols-outlined spin">autorenew</span>
                              Create Module
                          </button>
                    </div>
                </div>
    
                <div class="action-card">
                    <div class="card-header">
                        <div class="icon-box icon-emerald">
                            <span class="material-symbols-outlined">view_list</span>
                        </div>
                        <div class="header-text">
                            <h2>2. Select a Module to Manage Content</h2>
                            <p class="card-desc">Click a module to write content (Sections) or delete items inside it.</p>
                        </div>
                    </div>
    
                    <div v-if="isLoading" class="state-box">
                        <div class="cd-spinner"></div>
                        <p>Loading modules...</p>
                    </div>
    
                    <div v-else-if="modules.length === 0" class="empty-box">
                        <div class="empty-icon-wrapper">
                            <span class="material-symbols-outlined empty-icon">folder_off</span>
                        </div>
                        <h3>No modules in this course yet.</h3>
                        <p>Please create a module using the form above.</p>
                    </div>
    
                    <div v-else class="module-list">
                        <div v-for="(mod, index) in modules" :key="mod.id" class="module-card" :class="{'is-expanded': mod.isExpanded}">
    
                            <div class="module-item">
                                <div class="module-info">
                                    <div class="module-number">{{ index + 1 }}</div>
                                    <div class="module-text">
                                        <h3 class="module-name">{{ mod.title }}</h3>
                                        <div class="status-group">
                                            <span v-if="mod.learning_pages && mod.learning_pages.length > 0" class="badge badge-success">
                                                  <span class="material-symbols-outlined icon-micro">check_circle</span> Has content
                                            </span>
                                            <span v-else class="badge badge-warning">
                                                  <span class="material-symbols-outlined icon-micro">edit_document</span> No content yet
                                            </span>
                                        </div>
                                    </div>
                                </div>
    
                                <div class="module-actions">
                                    <button @click="toggleModuleLessons(mod)" class="btn-action" :class="mod.isExpanded ? 'btn-edit' : 'btn-add'">
                                          <span class="material-symbols-outlined icon-small">
                                              {{ mod.isExpanded ? 'expand_less' : 'list' }}
                                          </span>
                                          {{ mod.isExpanded ? 'Hide Lessons' : 'Manage Lessons' }}
                                      </button>
    
                                    <button v-if="mod.learning_pages && mod.learning_pages.length > 0" @click="deleteContent(mod)" class="btn-icon btn-clear" title="Delete content only (module name stays)">
                                          <span class="material-symbols-outlined">layers_clear</span>
                                      </button>
    
                                    <button @click="deleteModule(mod.id)" class="btn-icon btn-delete" title="Delete this module">
                                          <span class="material-symbols-outlined">delete</span>
                                      </button>
                                </div>
                            </div>
    
                            <div v-show="mod.isExpanded" class="lesson-dropdown">
                                <div class="add-lesson-bar">
                                    <button @click="createNewLesson(mod.id)" class="btn-add-lesson">
                                          <span class="material-symbols-outlined icon-small">add</span> New Lesson
                                      </button>
                                </div>
    
                                <div v-if="mod.learning_pages && mod.learning_pages.length > 0" class="lesson-items-container">
                                    <div v-for="(page, pIndex) in mod.learning_pages" :key="page.id" class="lesson-sub-item">
                                        <div class="lesson-sub-info">
                                            <div class="lesson-sub-number">{{ pIndex + 1 }}</div>
                                            <div>
                                                <h4 class="lesson-sub-title">{{ page.title || 'Untitled Lesson' }}</h4>
                                                <span class="badge" :class="page.is_published ? 'badge-success' : 'badge-warning'" style="font-size: 0.65rem;">
                                                      {{ page.is_published ? 'Published' : 'Draft' }}
                                                  </span>
                                            </div>
                                        </div>
                                        <button @click="editLesson(page.id, mod.id)" class="btn-edit-lesson">
                                              <span class="material-symbols-outlined icon-small">edit</span> Edit
                                          </button>
                                    </div>
                                </div>
    
                                <div v-else class="empty-lessons-msg">
                                    <span class="material-symbols-outlined">info</span> No lessons added yet.
                                </div>
                            </div>
    
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import learningService from '@/services/learningService';

const route = useRoute();
const router = useRouter();
const courseId = route.params.courseId;

const modules = ref([]);
const newModuleTitle = ref('');
const isLoading = ref(true);
const isCreating = ref(false);

onMounted(() => {
    if (!courseId) {
        alert("Course ID not found. Please enter through the course dashboard.");
        return;
    }
    loadModules();
});

const loadModules = async () => {
    isLoading.value = true;
    try {
        const res = await learningService.listModules(courseId);
        const fetchedModules = res.data || [];

        for (let mod of fetchedModules) {
            try {
                const pagesRes = await learningService.listPages(mod.id);
                mod.learning_pages = pagesRes.data || [];
                mod.isExpanded = false;
            } catch (err) {
                mod.learning_pages = [];
                mod.isExpanded = false;
            }
        }
        modules.value = fetchedModules;
    } catch (error) {
        console.error("Error loading modules:", error);
    } finally {
        isLoading.value = false;
    }
};

const toggleModuleLessons = (mod) => {
    mod.isExpanded = !mod.isExpanded;
};

const createNewLesson = (moduleId) => {
    router.push(`/learning/${courseId}/${moduleId}/edit`);
};

const editLesson = (pageId, moduleId) => {
    router.push(`/learning/${courseId}/${moduleId}/edit/${pageId}`);
};

const createModule = async () => {
    if (!newModuleTitle.value.trim()) {
        alert('Please enter a module name.');
        return;
    }

    isCreating.value = true;
    try {
        await learningService.createModule({
            course_id: parseInt(courseId, 10),
            title: newModuleTitle.value,
            order_index: modules.value.length
        });

        newModuleTitle.value = '';
        await loadModules();
    } catch (error) {
        console.error("Create Module Error:", error);
        alert('เกิดข้อผิดพลาดในการCreate Module');
    } finally {
        isCreating.value = false;
    }
};

const deleteModule = async (moduleId) => {
    if (confirm("Delete this module?\nAll content inside will be permanently removed.")) {
        try {
            await learningService.deleteModule(moduleId);
            await loadModules();
        } catch (error) {
            alert("Failed to delete module.");
        }
    }
};

const deleteContent = async (mod) => {
    if (!mod.learning_pages || mod.learning_pages.length === 0) return;
    const pageId = mod.learning_pages[0].id;

    if (confirm(`Delete content for module "${mod.title}" ?\n(Lesson content and quizzes will be deleted, but the module name will remain so you can start fresh.)`)) {
        try {
            await learningService.deletePage(pageId);
            alert('Content cleared. This module is now empty and ready for new content.');
            await loadModules();
        } catch (error) {
            console.error("Delete Content Error:", error);
            alert("An error occurred. Could not delete content.");
        }
    }
};
</script>

<style scoped>
/* ================= Base Styles ================= */

.cd-root {
    width: 100%;
    min-height: 100vh;
    background: linear-gradient(90deg, #fffcec, #e8dfbf, #ffc7db, #fff8d0);
    font-family: 'DM Sans', 'Sarabun', 'Inter', sans-serif;
    padding: 2rem;
    box-sizing: border-box;
}

.cd-container {
    max-width: 1100px;
    margin: 0 auto;
}

.material-symbols-outlined {
    vertical-align: middle;
}

/* ================= Hero Banner ================= */

.cd-hero {
    background: linear-gradient(135deg, #df4a7d 0%, #c83264 100%);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    color: #fff;
    margin-bottom: 2rem;
    box-shadow: 0 10px 25px rgba(223, 74, 125, 0.15);
}

.cd-hero-top {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.back-btn {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: 2px solid rgba(255, 255, 255, 0.4);
    background: transparent;
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s ease;
    padding: 0;
    flex-shrink: 0;
}

.back-btn:hover {
    background: rgba(255, 255, 255, 0.3);
    border-color: rgba(255, 255, 255, 0.6);
}

.cd-breadcrumb {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.85rem;
    font-weight: 600;
    opacity: 0.9;
}

.cd-label.clickable {
    cursor: pointer;
    transition: opacity 0.2s;
}

.cd-label.clickable:hover {
    opacity: 0.7;
    text-decoration: underline;
}

.separator {
    font-size: 1.2rem;
}

.cd-title {
    font-size: 2.2rem;
    font-weight: 800;
    margin: 0 0 0.5rem;
    letter-spacing: -0.01em;
}

.cd-desc {
    font-size: 0.95rem;
    opacity: 0.9;
    margin: 0;
    max-width: 600px;
    line-height: 1.6;
}

/* ================= Cards ================= */

.action-card {
    background-color: white;
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.04);
    margin-bottom: 1.5rem;
}

.card-header {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.icon-box {
    width: 48px;
    height: 48px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.icon-rose {
    background: #ffe4e6;
    color: #e11d48;
}

.icon-emerald {
    background: #d1fae5;
    color: #059669;
}

.icon-box .material-symbols-outlined {
    font-size: 24px;
}

.header-text h2 {
    font-size: 1.35rem;
    font-weight: 800;
    color: #1e293b;
    margin: 0 0 0.3rem 0;
}

.card-desc {
    color: #64748b;
    font-size: 0.95rem;
    margin: 0;
}

/* ================= Create Form ================= */

.create-form {
    display: flex;
    gap: 1rem;
    margin-left: 4rem;
    /* Indent to align with text */
}

.input-module {
    flex: 1;
    padding: 1rem 1.25rem;
    border-radius: 12px;
    border: 2px solid #e2e8f0;
    font-size: 1rem;
    color: #334155;
    background-color: #f8fafc;
    outline: none;
    transition: all 0.2s;
    font-family: inherit;
}

.input-module:focus {
    background-color: white;
    border-color: #df4a7d;
    box-shadow: 0 0 0 4px rgba(223, 74, 125, 0.1);
}

.btn-create {
    display: flex;
    align-items: center;
    gap: 8px;
    background: linear-gradient(135deg, #df4a7d 0%, #c83264 100%);
    color: white;
    border: none;
    padding: 0 2rem;
    border-radius: 12px;
    font-weight: 700;
    font-size: 1rem;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(223, 74, 125, 0.2);
    transition: all 0.2s;
    white-space: nowrap;
}

.btn-create:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(223, 74, 125, 0.3);
}

.btn-create:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.spin {
    animation: spin 1s linear infinite;
}

/* ================= States ================= */

.state-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 4rem 0;
    color: #64748b;
    font-weight: 600;
}

.cd-spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #fce4ec;
    border-top-color: #df4a7d;
    border-radius: 50%;
    animation: cd-spin 0.8s linear infinite;
    margin-bottom: 1rem;
}

@keyframes cd-spin {
    to {
        transform: rotate(360deg);
    }
}

.empty-box {
    text-align: center;
    padding: 3rem 2rem;
    background-color: #f8fafc;
    border-radius: 16px;
    border: 2px dashed #cbd5e1;
    margin-left: 4rem;
}

.empty-icon-wrapper {
    width: 64px;
    height: 64px;
    background: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 1rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.empty-icon {
    font-size: 2rem;
    color: #94a3b8;
}

.empty-box h3 {
    font-size: 1.15rem;
    font-weight: 800;
    color: #475569;
    margin: 0 0 0.5rem 0;
}

.empty-box p {
    color: #94a3b8;
    font-size: 0.95rem;
    margin: 0;
}

/* ================= Module List ================= */

.module-list {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
    margin-left: 4rem;
    animation: slideUp 0.4s ease-out;
}

@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateY(15px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.module-card {
    border-radius: 16px;
    border: 1px solid #e2e8f0;
    background-color: white;
    transition: all 0.2s;
    overflow: hidden;
}

.module-card:hover {
    border-color: #cbd5e1;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.module-card.is-expanded {
    border-color: #df4a7d;
    box-shadow: 0 4px 20px rgba(223, 74, 125, 0.08);
}

.module-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.25rem 1.5rem;
}

.module-info {
    display: flex;
    align-items: center;
    gap: 1.25rem;
}

.module-number {
    width: 44px;
    height: 44px;
    background-color: #fce4ec;
    color: #c83264;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    font-weight: 800;
}

.module-name {
    font-size: 1.15rem;
    font-weight: 800;
    color: #1e293b;
    margin: 0 0 0.4rem 0;
}

.status-group {
    display: flex;
    gap: 8px;
}

.badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    border-radius: 8px;
    font-size: 0.75rem;
    font-weight: 700;
}

.badge-success {
    background-color: #ecfdf5;
    color: #059669;
    border: 1px solid #d1fae5;
}

.badge-warning {
    background-color: #fff7ed;
    color: #ea580c;
    border: 1px solid #ffedd5;
}

.icon-micro {
    font-size: 14px;
}

/* ================= Actions ================= */

.module-actions {
    display: flex;
    gap: 8px;
}

.btn-action {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 16px;
    border-radius: 10px;
    font-weight: 700;
    font-size: 0.9rem;
    cursor: pointer;
    border: 2px solid transparent;
    transition: all 0.2s;
}

.btn-add {
    background-color: #10b981;
    color: white;
}

.btn-add:hover {
    background-color: #059669;
}

.btn-edit {
    background-color: #f1f5f9;
    color: #475569;
    border-color: #e2e8f0;
}

.btn-edit:hover {
    background-color: #e2e8f0;
    color: #1e293b;
}

.btn-icon {
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 10px;
    background-color: white;
    border: 1px solid #e2e8f0;
    cursor: pointer;
    transition: all 0.2s;
    color: #94a3b8;
}

.btn-clear:hover {
    background-color: #fff7ed;
    border-color: #fed7aa;
    color: #f97316;
}

.btn-delete:hover {
    background-color: #fef2f2;
    border-color: #fecaca;
    color: #ef4444;
}

/* ================= Lesson Dropdown ================= */

.lesson-dropdown {
    background-color: #f8fafc;
    border-top: 1px solid #e2e8f0;
    padding: 1.5rem;
    animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}

.add-lesson-bar {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 1rem;
}

.btn-add-lesson {
    display: flex;
    align-items: center;
    gap: 6px;
    background-color: #ffe4e6;
    color: #e11d48;
    border: 1px solid #fecdd3;
    padding: 8px 16px;
    border-radius: 8px;
    font-weight: 700;
    font-size: 0.85rem;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-add-lesson:hover {
    background-color: #e11d48;
    color: white;
    border-color: #e11d48;
}

.lesson-items-container {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.lesson-sub-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    background-color: white;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    transition: all 0.2s;
}

.lesson-sub-item:hover {
    border-color: #cbd5e1;
    transform: translateX(4px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
}

.lesson-sub-info {
    display: flex;
    align-items: center;
    gap: 12px;
}

.lesson-sub-number {
    width: 28px;
    height: 28px;
    background-color: #f1f5f9;
    color: #64748b;
    font-weight: 700;
    font-size: 0.85rem;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.lesson-sub-title {
    margin: 0 0 4px 0;
    font-size: 1rem;
    font-weight: 700;
    color: #334155;
}

.btn-edit-lesson {
    display: flex;
    align-items: center;
    gap: 4px;
    background-color: transparent;
    color: #94a3b8;
    border: 1px solid transparent;
    padding: 6px 12px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.85rem;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-edit-lesson:hover {
    background-color: #f1f5f9;
    color: #0f172a;
    border-color: #e2e8f0;
}

.empty-lessons-msg {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #94a3b8;
    font-size: 0.9rem;
    font-weight: 500;
    font-style: italic;
    justify-content: center;
    padding: 1rem 0;
}

/* ================= Responsive ================= */

@media (max-width: 860px) {
    .create-form,
    .module-list,
    .empty-box {
        margin-left: 0;
        margin-top: 1rem;
    }
    .card-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5rem;
    }
}

@media (max-width: 640px) {
    .cd-root {
        padding: 1rem;
    }
    .cd-hero {
        padding: 1.5rem;
    }
    .create-form {
        flex-direction: column;
    }
    .btn-create {
        padding: 1rem;
        justify-content: center;
    }
    .module-item {
        flex-direction: column;
        align-items: stretch;
        gap: 1.5rem;
    }
    .module-actions {
        width: 100%;
        display: grid;
        grid-template-columns: 1fr auto auto;
    }
    .btn-action {
        justify-content: center;
    }
    .lesson-sub-item {
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;
    }
    .btn-edit-lesson {
        width: 100%;
        justify-content: center;
        background-color: #f1f5f9;
    }
}
</style>