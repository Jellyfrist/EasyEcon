<template>
  <div class="page">

    <!-- Header -->
    <div class="header">
      <div class="header-left">
        <button class="back-btn" @click="$router.back()">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 5l-7 7 7 7"/></svg>
        </button>
        <div>
          <p class="breadcrumb">{{ template?.title ?? `Template #${templateId}` }}</p>
          <h1 class="page-title">Launch Exam Session</h1>
        </div>
      </div>
    </div>

    <!-- Loading template -->
    <div v-if="isLoadingTemplate" class="loading-state">
      Loading template...
    </div>

    <template v-else>

      <!-- Template summary -->
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

      <!-- Launch Form -->
      <div class="form-card">

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
        <div v-if="error" class="error-banner">⚠️ {{ error }}</div>

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
    </template>

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
      template_id: Number(templateId),   // required
      title: form.value.title,           // required
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
* { box-sizing: border-box; margin: 0; padding: 0; }

.page {
  font-family: 'Sarabun', sans-serif;
  min-height: 100vh;
  padding: 32px;
  max-width: 760px;
  margin: 0 auto;
}

/* Header */
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 28px;
}
.header-left { display: flex; align-items: center; gap: 14px; }
.back-btn {
  width: 38px; height: 38px;
  border: 1.5px solid #dde1ea; background: #fff;
  border-radius: 10px; display: flex; align-items: center; justify-content: center;
  cursor: pointer; color: #555; transition: all 0.15s;
}
.back-btn:hover { background: #f0f1f5; }
.breadcrumb { font-size: 12px; color: #9399aa; margin-bottom: 2px; }
.page-title { font-family: 'IBM Plex Sans Thai', sans-serif; font-size: 22px; font-weight: 700; color: #1a1d2e; }

/* Template Summary */
.template-summary {
  display: flex; gap: 12px; flex-wrap: wrap;
  background: #fff; border: 1px solid #e8eaf2;
  border-radius: 14px; padding: 18px 22px;
  margin-bottom: 20px;
}
.summary-item { display: flex; flex-direction: column; gap: 4px; min-width: 90px; }
.summary-label { font-size: 11px; font-weight: 600; color: #9399aa; text-transform: uppercase; letter-spacing: 0.05em; }
.summary-value { font-size: 15px; font-weight: 600; color: #1a1d2e; }

.exam-type-badge {
  display: inline-block;
  font-size: 11px; font-weight: 600; padding: 3px 10px;
  border-radius: 999px; white-space: nowrap; width: fit-content;
}
.exam-type-badge.midterm { background: #eff6ff; color: #2563eb; }
.exam-type-badge.final   { background: #fef3c7; color: #d97706; }
.exam-type-badge.summer  { background: #f0fdf4; color: #16a34a; }
.exam-type-badge.quiz    { background: #faf5ff; color: #7c3aed; }

/* Form Card */
.form-card {
  background: #fff; border: 1px solid #e8eaf2;
  border-radius: 14px; padding: 28px;
  display: flex; flex-direction: column; gap: 22px;
}
.section-header h2 { font-size: 16px; font-weight: 700; color: #1a1d2e; margin-bottom: 4px; }
.section-header p  { font-size: 13px; color: #7c82a0; }

.form-row { display: flex; gap: 16px; }
.two-col .form-group { flex: 1; min-width: 0; }
.form-group { display: flex; flex-direction: column; gap: 6px; }

label { font-size: 13px; font-weight: 600; color: #3a3d52; }
.required { color: #dc2626; }
.hint { font-size: 12px; color: #9399aa; }

.input-field {
  border: 1.5px solid #e2e5ef; border-radius: 9px;
  padding: 9px 13px; font-size: 14px;
  font-family: 'Sarabun', sans-serif; color: #1a1d2e;
  outline: none; transition: border-color 0.15s; background: #fdfdff; width: 100%;
}
.input-field:focus { border-color: #1a1d2e; }
textarea.input-field { resize: vertical; }

.error-banner {
  background: #fef2f2; border: 1px solid #fca5a5;
  border-radius: 9px; padding: 12px 16px;
  font-size: 13.5px; color: #dc2626;
}

.form-actions {
  display: flex; justify-content: flex-end; gap: 10px;
  padding-top: 4px; border-top: 1px solid #f0f1f5;
}

/* Buttons */
.btn-primary {
  background: #1a1d2e; color: #fff;
  border: none; border-radius: 10px;
  padding: 10px 22px; font-size: 14px;
  font-family: 'Sarabun', sans-serif; font-weight: 500;
  cursor: pointer; display: flex; align-items: center; gap: 7px;
  transition: background 0.15s;
}
.btn-primary:hover:not(:disabled) { background: #2d3251; }
.btn-primary:disabled { opacity: 0.4; cursor: not-allowed; }

.btn-ghost {
  background: transparent; color: #555;
  border: 1.5px solid #e2e5ef; border-radius: 10px;
  padding: 10px 20px; font-size: 14px;
  font-family: 'Sarabun', sans-serif;
  cursor: pointer; transition: background 0.15s;
}
.btn-ghost:hover { background: #f7f8fc; }

.loading-state {
  text-align: center; padding: 60px;
  color: #7c82a0; font-size: 14px;
}

@media (max-width: 600px) {
  .page { padding: 20px 16px; }
  .form-row { flex-direction: column; }
  .template-summary { gap: 16px; }
}
</style>