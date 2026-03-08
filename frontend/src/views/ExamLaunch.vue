<template>
  <div class="page">

    <!-- Page Card: gradient header + summary bar -->
    <div class="page-card">

      <div class="header">
        <div class="header-left">
          <button class="back-btn" @click="$router.back()">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M19 12H5M12 5l-7 7 7 7"/></svg>
          </button>
          <div class="header-text">
            <p class="breadcrumb">{{ template?.title ?? `Template #${templateId}` }}</p>
            <h1 class="page-title">Launch Exam Session</h1>
          </div>
        </div>
      </div>

      <!-- Loading template -->
      <div v-if="isLoadingTemplate" class="loading-state">
        Loading template...
      </div>

      <!-- Template summary bar (inside page-card) -->
      <template v-else>
        <div class="template-summary">
          <div class="summary-item">
            <span class="summary-label">Type</span>
            <span :class="['exam-type-badge', template?.exam_type]">{{ examTypeLabels[template?.exam_type] ?? template?.exam_type }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Questions</span>
            <span class="summary-value">{{ template?.question_count ?? '—' }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Total Points</span>
            <span class="summary-value">{{ template?.total_points ?? '—' }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Time Limit</span>
            <span class="summary-value">{{ template?.time_limit_minutes ? `${template.time_limit_minutes} min` : 'No limit' }}</span>
          </div>
        </div>
      </template>

    </div>

    <!-- Launch Form -->
    <div v-if="!isLoadingTemplate" class="form-card">

        <div class="section-header">
          <h2>Session Settings</h2>
          <p>These settings apply to this session only and do not modify the original template.</p>
        </div>

        <!-- Session title -->
        <div class="form-group">
          <label>Session Title <span class="required">*</span></label>
          <input
            v-model="form.title"
            type="text"
            class="input-field"
            placeholder="e.g. Microeconomics Midterm — Sec.1 March 2025"
          />
          <span class="hint">Students will see this name when opening the exam.</span>
        </div>

        <!-- Instructions -->
        <div class="form-group">
          <label>Instructions</label>
          <textarea
            v-model="form.instructions"
            rows="3"
            class="input-field"
            placeholder="e.g. Closed book. No calculators. You have 90 minutes."
          ></textarea>
        </div>

        <!-- Availability window -->
        <div class="form-row two-col">
          <div class="form-group">
            <label>Available From</label>
            <input v-model="form.available_from" type="datetime-local" class="input-field" />
            <span class="hint">Leave blank to open immediately.</span>
          </div>
          <div class="form-group">
            <label>Available Until</label>
            <input v-model="form.available_until" type="datetime-local" class="input-field" />
            <span class="hint">Leave blank for no deadline.</span>
          </div>
        </div>

        <!-- Time limit override + max attempts -->
        <div class="form-row two-col">
          <div class="form-group">
            <label>Time Limit Override (minutes)</label>
            <input
              v-model.number="form.time_limit_minutes"
              type="number"
              min="1"
              class="input-field"
              :placeholder="template?.time_limit_minutes ? `Default: ${template.time_limit_minutes} min` : 'No limit'"
            />
            <span class="hint">Overrides the template's time limit for this session.</span>
          </div>
          <div class="form-group">
            <label>Max Attempts per Student</label>
            <input
              v-model.number="form.max_attempts"
              type="number"
              min="1"
              class="input-field"
              placeholder="1"
            />
          </div>
        </div>

        <!-- Error -->
        <div v-if="error" class="error-banner">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>
          {{ error }}
        </div>

        <!-- Actions -->
        <div class="form-actions">
          <button class="btn-ghost" @click="$router.back()">Cancel</button>
          <button
            class="btn-primary"
            :disabled="!form.title || isLaunching"
            @click="launch"
          >
            <svg v-if="!isLaunching" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="5 3 19 12 5 21 5 3"/></svg>
            <span>{{ isLaunching ? 'Launching...' : 'Launch Session' }}</span>
          </button>
        </div>

    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import examService from '@/services/examService'

const route = useRoute()
const router = useRouter()

const templateId = route.params.templateId

const examTypeLabels = {
  midterm: 'Midterm',
  final: 'Final',
  summer: 'Summer',
  quiz: 'Quiz',
}

// --- State ---
const template = ref(null)
const isLoadingTemplate = ref(false)
const isLaunching = ref(false)
const error = ref(null)

// --- Form — ExamSessionCreate ---
const form = ref({
  // template_id: templateId,
  title: '', // required
  instructions: null,
  available_from: null,
  available_until: null,
  time_limit_minutes: null,
  max_attempts: 1,
})

async function loadTemplate() {
  isLoadingTemplate.value = true
  try {
    const res = await examService.getTemplate(templateId)
    template.value = res.data ?? res
    // Pre-fill session title from template title
    if (!form.value.title) {
      form.value.title = template.value.title ?? ''
    }
  } catch (err) {
    console.error('Failed to load template', err)
  } finally {
    isLoadingTemplate.value = false
  }
}

onMounted(() => {
  loadTemplate()
})

// --- Launch ---
async function launch() {
  isLaunching.value = true
  error.value = null
  try {
    // Build payload — only include non-null optional fields
    const payload = {
      template_id: Number(templateId),
      title: form.value.title,
    }
    
    if (form.value.instructions) {
        payload.instructions = form.value.instructions
    }
    if (form.value.available_from) {
        payload.available_from     = new Date(form.value.available_from).toISOString()
    }
    if (form.value.available_until) {
        payload.available_until    = new Date(form.value.available_until).toISOString()
    }
    if (form.value.time_limit_minutes) {
        payload.time_limit_minutes = form.value.time_limit_minutes
    }

    payload.max_attempts = form.value.max_attempts ?? 1

    const res = await examService.launchSession(payload)
    const session = res.data ?? res

    // Navigate to session results page (or back to dashboard)
    router.push({ name: 'TeacherExamDashboard', params: { courseId: route.params.courseId ?? template.value?.course_id } })

  } catch (err) {
    console.error('Failed to launch session', err)
    error.value = err?.response?.data?.detail ?? 'Launch failed. Please try again.'
  } finally {
    isLaunching.value = false
  }
}
</script>

<style scoped>
/* Page wrapper */
.page {
  min-height: 100vh;
  padding: 2rem;
  max-width: 860px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/* Page card + gradient header */
.page-card {
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(237, 64, 129, 0.22);
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  background: linear-gradient(135deg, var(--primary-pink) 0%, #f06292 100%);
  padding: 1.5rem 1.75rem;
  position: relative;
  overflow: hidden;
}

.header::before {
  content: '';
  position: absolute;
  right: -40px; top: -40px;
  width: 160px; height: 160px;
  border-radius: 50%;
  background: rgba(255,255,255,0.08);
  pointer-events: none;
}

.header::after {
  content: '';
  position: absolute;
  right: 60px; bottom: -50px;
  width: 110px; height: 110px;
  border-radius: 50%;
  background: rgba(255,255,255,0.06);
  pointer-events: none;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
  position: relative;
  z-index: 1;
}

.header-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px; height: 36px;
  border-radius: 50%;
  border: 1.5px solid rgba(255,255,255,0.4);
  background: rgba(255,255,255,0.15);
  color: var(--white);
  cursor: pointer;
  flex-shrink: 0;
  backdrop-filter: blur(4px);
  transition: all 0.18s ease;
}

.back-btn:hover {
  background: rgba(255,255,255,0.28);
  border-color: rgba(255,255,255,0.7);
}

.breadcrumb {
  font-size: 0.72rem;
  color: rgba(255,255,255,0.75);
  font-weight: 500;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--white);
  line-height: 1.15;
  letter-spacing: -0.01em;
}

/* Template summary bar  (inside page-card, white bg) */
.template-summary {
  display: flex;
  gap: 0;
  background: var(--white);
  border-top: 1px solid rgba(237, 64, 129, 0.12);
}

.summary-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 1rem 1.25rem;
  border-right: 1px solid var(--card-border);
}

.summary-item:last-child { border-right: none; }

.summary-label {
  font-size: 0.68rem;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.summary-value {
  font-size: 0.9375rem;
  font-weight: 700;
  color: var(--text-main);
}

/* Exam type badge */
.exam-type-badge {
  display: inline-flex;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 2px 10px;
  border-radius: 999px;
  white-space: nowrap;
  width: fit-content;
}

.exam-type-badge.midterm { background: #eff6ff; color: #2563eb; }
.exam-type-badge.final { background: var(--light-yellow); color: #92400e; }
.exam-type-badge.summer { background: var(--light-green); color: var(--forest-green); }
.exam-type-badge.quiz { background: #faf5ff; color: #7c3aed; }

/* Form card */
.form-card {
  background: var(--white);
  border: 1px solid var(--card-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  padding: 1.75rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.section-header {
  padding-bottom: 1rem;
  border-bottom: 2px solid var(--gray-light);
}

.section-header h2 {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text-main);
  margin-bottom: 0.2rem;
}

.section-header p {
  font-size: 0.78rem;
  color: var(--text-muted);
}

/* form-group: override global to remove bottom margin, use gap from parent */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin-bottom: 0;
}

.form-group label {
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0;
}

.required { color: var(--primary-pink); }

.hint {
  font-size: 0.72rem;
  color: var(--text-muted);
  opacity: 0.8;
}

/* Local input override (tighter than global) */
.input-field {
  padding: 0.6rem 0.875rem;
  font-size: 0.875rem;
  font-family: inherit;
  border: 1.5px solid var(--card-border);
  border-radius: var(--radius-md);
  background: var(--gray-light);
  color: var(--text-main);
  outline: none;
  transition: all 0.18s ease;
  width: 100%;
}

.input-field:focus {
  border-color: var(--primary-pink);
  background: var(--white);
  box-shadow: 0 0 0 3px rgba(237, 64, 129, 0.08);
}

textarea.input-field { resize: vertical; line-height: 1.5; }

/* 2-col row */
.form-row { display: flex; gap: 1rem; }
.two-col .form-group { flex: 1; min-width: 0; }

/* Error banner */
.error-banner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #fee2e2;
  border: 1px solid #fca5a5;
  border-radius: var(--radius-md);
  padding: 0.75rem 1rem;
  font-size: 0.84rem;
  font-weight: 500;
  color: #b91c1c;
}

/* Form actions */
.form-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 2px solid var(--gray-light);
  margin-top: 0.25rem;
}

/* Buttons  (mirror ExamDashboard) */
.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  background: var(--primary-pink);
  color: var(--white);
  border: none;
  border-radius: var(--radius-md);
  padding: 0.6rem 1.375rem;
  font-size: 0.875rem;
  font-family: inherit;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.15s ease, transform 0.15s ease;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-hover);
  transform: translateY(-1px);
}

.btn-primary:active { transform: scale(0.98); }

.btn-primary:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-ghost {
  background: transparent;
  color: var(--text-muted);
  border: 1.5px solid var(--card-border);
  border-radius: var(--radius-md);
  padding: 0.6rem 1.25rem;
  font-size: 0.875rem;
  font-family: inherit;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s ease;
}

.btn-ghost:hover {
  background: var(--gray-light);
  color: var(--text-main);
  border-color: var(--text-muted);
}

/* Loading state */
.loading-state {
  text-align: center;
  padding: 4rem;
  color: var(--text-muted);
  font-size: 0.875rem;
}

/* Responsive */
@media (max-width: 600px) {
  .page { padding: 1rem; }
  .form-row { flex-direction: column; }
  .template-summary { flex-wrap: wrap; }
  .summary-item { min-width: 45%; border-right: none; border-bottom: 1px solid var(--card-border); }
}
</style>