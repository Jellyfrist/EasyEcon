<template>
    <div class="module-manager-page">
    
        <header class="top-navbar">
            <button @click="router.push(`/teacher/learning/${courseId}`)" class="back-btn">
                <span class="material-symbols-outlined">arrow_back</span>
                Back To Learning Overview
            </button>
        </header>
        <main class="main-container">
            <div class="page-header">
                <h1 class="page-title">Manage Course Structure (Modules)</h1>
                <p class="page-subtitle">Create main modules and manage lesson content for your course.</p>
            </div>
    
            <div class="create-card">
                <div class="card-header">
                    <span class="material-symbols-outlined icon-rose">add_box</span>
                    <h2>1. Create a New Module</h2>
                </div>
                <p class="card-desc">Create a module folder first to organise your lesson content inside.</p>
    
                <div class="create-form">
                    <input v-model="newModuleTitle" type="text" placeholder="Module name, e.g. Chapter 1: Introduction to Economics" class="input-module" @keyup.enter="createModule">
                    <button @click="createModule" :disabled="isCreating" class="btn-create">
                <span v-if="!isCreating" class="material-symbols-outlined">add_circle</span>
                <span v-else class="material-symbols-outlined spin">autorenew</span>
                Create Module
              </button>
                </div>
            </div>
    
            <div class="list-card">
                <div class="card-header">
                    <span class="material-symbols-outlined icon-emerald">view_list</span>
                    <h2>2. Select a Module to Manage Content</h2>
                </div>
                <p class="card-desc">Click a module to write content (Sections) or delete items inside it.</p>
    
                <div v-if="isLoading" class="state-box">
                    <div class="spinner"></div>
                    <p>Loading modules...</p>
                </div>
    
                <div v-else-if="modules.length === 0" class="empty-box">
                    <span class="material-symbols-outlined empty-icon">folder_off</span>
                    <h3>No modules in this course yet.</h3>
                    <p>Please create a module using the form above.</p>
                </div>
    
                <div v-else class="module-list">
                    <div v-for="(mod, index) in modules" :key="mod.id" class="module-card">
    
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

.module-manager-page {
    min-height: 100vh;
    background-color: #f8fafc;
    font-family: 'Sarabun', 'Inter', sans-serif;
    padding-bottom: 5rem;
}

.material-symbols-outlined {
    vertical-align: middle;
}

/* ================= Navbar ================= */

.top-navbar {
    background-color: white;
    border-bottom: 1px solid #e2e8f0;
    padding: 1rem 2rem;
    position: sticky;
    top: 0;
    z-index: 10;
}

.back-btn {
    display: flex;
    align-items: center;
    gap: 8px;
    background: none;
    border: none;
    color: #64748b;
    font-weight: 700;
    font-size: 0.95rem;
    cursor: pointer;
    transition: color 0.2s;
    padding: 0;
}

.back-btn:hover {
    color: #0f172a;
}

/* ================= Main Content ================= */

.main-container {
    max-width: 900px;
    margin: 0 auto;
    padding: 2.5rem 1.5rem;
}

.page-header {
    margin-bottom: 2.5rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid #e2e8f0;
}

.page-title {
    font-size: 2.2rem;
    font-weight: 800;
    color: #0f172a;
    margin: 0 0 0.5rem 0;
    letter-spacing: -0.5px;
}

.page-subtitle {
    color: #64748b;
    margin: 0;
    font-size: 1rem;
    font-weight: 500;
}

/* ================= Cards ================= */

.create-card,
.list-card {
    background-color: white;
    border-radius: 24px;
    padding: 2rem;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
    margin-bottom: 2rem;
}

.card-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 0.5rem;
}

.card-header h2 {
    font-size: 1.35rem;
    font-weight: 800;
    color: #0f172a;
    margin: 0;
}

.icon-rose {
    color: #f43f5e;
    font-size: 1.8rem;
}

.icon-emerald {
    color: #10b981;
    font-size: 1.8rem;
}

.card-desc {
    color: #64748b;
    font-size: 0.95rem;
    margin: 0 0 1.5rem 0;
}

/* ================= Create Form ================= */

.create-form {
    display: flex;
    gap: 1rem;
}

.input-module {
    flex: 1;
    padding: 1rem 1.25rem;
    border-radius: 16px;
    border: 2px solid #e2e8f0;
    font-size: 1rem;
    color: #334155;
    background-color: #f8fafc;
    outline: none;
    transition: all 0.2s;
}

.input-module:focus {
    background-color: white;
    border-color: #f43f5e;
    box-shadow: 0 0 0 4px rgba(244, 63, 94, 0.1);
}

.btn-create {
    display: flex;
    align-items: center;
    gap: 8px;
    background-color: #f43f5e;
    color: white;
    border: none;
    padding: 0 2rem;
    border-radius: 16px;
    font-weight: 700;
    font-size: 1rem;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(244, 63, 94, 0.2);
    transition: all 0.2s;
    white-space: nowrap;
}

.btn-create:hover:not(:disabled) {
    background-color: #e11d48;
    transform: translateY(-2px);
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

.spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #f1f5f9;
    border-top-color: #f43f5e;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 1rem;
}

@keyframes spin {
    100% {
        transform: rotate(360deg);
    }
}

.empty-box {
    text-align: center;
    padding: 4rem 2rem;
    background-color: #f8fafc;
    border-radius: 20px;
    border: 2px dashed #cbd5e1;
}

.empty-icon {
    font-size: 4rem;
    color: #cbd5e1;
    margin-bottom: 1rem;
}

.empty-box h3 {
    font-size: 1.25rem;
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
    gap: 1.5rem;
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
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.module-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem;
}

.module-info {
    display: flex;
    align-items: center;
    gap: 1.25rem;
}

.module-number {
    width: 48px;
    height: 48px;
    background-color: #f1f5f9;
    color: #64748b;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    font-weight: 800;
}

.module-name {
    font-size: 1.15rem;
    font-weight: 800;
    color: #1e293b;
    margin: 0 0 0.5rem 0;
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
    border-radius: 6px;
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
    padding: 10px 20px;
    border-radius: 12px;
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
    width: 42px;
    height: 42px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 12px;
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
    background-color: #fff1f2;
    color: #e11d48;
    border: 1px solid #ffe4e6;
    padding: 8px 16px;
    border-radius: 10px;
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
    border-radius: 12px;
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

@media (max-width: 768px) {
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