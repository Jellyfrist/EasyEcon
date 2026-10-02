<template>
    <fieldset class="session-fields" :disabled="disabled">
        <!-- Session title -->
        <div class="form-group">
          <label>Session Title <span class="required">*</span></label>
          <input
            v-model="form.title"
            type="text"
            class="input-field"
            :placeholder="defaultTitle || 'e.g. Microeconomics Midterm — Sec.1 March 2025'"
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
              :placeholder="defaultTimeLimit ? `Default: ${defaultTimeLimit} min` : 'No limit'"
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

    </fieldset>
</template>

<script setup>
defineProps({
    form: { type: Object, required: true },
    defaultTimeLimit: { type: Number, default: null },
    defaultTitle: { type: String, default: '' },
    disabled: { type: Boolean, default: false },
})
</script>

<style scoped>
.session-fields {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
    border: 0;
    padding: 0;
    margin: 0;
    min-width: 0;
}
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

@media (max-width: 600px) {
    .form-row { flex-direction: column; }
}
</style>
