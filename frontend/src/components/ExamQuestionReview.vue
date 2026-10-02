<template>
    <section class="review-section">
          <div v-if="wrongTopics.length" class="card">
            <h2 class="card-title">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><path d="M12 9v4M12 17h.01"/></svg>
              Questions to Review
            </h2>

            <div class="weakness-groups">
              <div v-for="topic in wrongTopics" :key="topic.topic_tag" class="weakness-group">
                <div class="group-header">
                  <span class="group-topic">{{ topic.topic_tag }}</span>
                  <span class="group-count">
                    {{ topic.wrong_count }} of {{ topic.total_questions }} wrong · {{ Number(topic.score_pct || 0).toFixed(0) }}%
                  </span>
                </div>

                <p v-if="topic.message" class="weakness-q-text">{{ topic.message }}</p>

                <div class="weakness-items">
                  <div v-for="q in topic.questions" :key="q.question_id" class="weakness-item">
                    <div class="weakness-item-top">
                      <span :class="['q-type-badge', q.type ?? 'multiple_choice']">
                        {{ typeLabel(q.type) }}
                      </span>
                      <p class="weakness-q-text">{{ q.text || 'No question text available.' }}</p>
                      <img v-for="(url, imageIndex) in q.image_urls || []" :key="imageIndex"
                        :src="url" alt="Question image" class="review-question-image" />
                    </div>

                    <div class="answer-row">
                      <span class="answer-label">Your Answer:</span>
                      <span class="answer-val your">
                        {{ q.answered ? formatAnswer(q.your_answer) : 'Left blank' }}
                      </span>
                    </div>

                    <div v-if="q.correct_answer != null" class="answer-row">
                      <span class="answer-label">Correct Answer:</span>
                      <span class="answer-val">{{ formatAnswer(q.correct_answer) }}</span>
                    </div>

                    <!-- teacher-written explanation, only sent when the exam reveals answers -->
                    <div v-if="q.explanation" class="explanation-box">
                      <span class="explanation-label">
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>
                      Explanation
                    </span>
                      <p class="explanation-text">{{ q.explanation }}</p>
                    </div>
                    <p v-else-if="!answersRevealed" class="explanation-hidden">
                      The teacher has not released answers and explanations for this exam.
                    </p>
                  </div>
                </div>

                <div v-if="topic.lessons?.length" class="action-row">
                  <router-link
                    v-for="lesson in topic.lessons"
                    :key="lesson.page_id"
                    :to="lesson.study_url"
                    class="review-link"
                  >
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>
                    Review Lesson: {{ lesson.title }}
                  </router-link>
                </div>
                <p v-else class="no-lesson">No lesson is linked to this topic yet.</p>
              </div>
            </div>
          </div>

          <div v-else-if="!error" class="perfect-card">
            <div class="perfect-icon">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/><path d="M18 2H6v7a6 6 0 0 0 12 0V2z"/></svg>
            </div>
            <p class="perfect-text">No weak areas found. Great performance!</p>
          </div>
    

    </section>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({
    wrongTopics: { type: Array, default: () => [] },
    error: { type: String, default: '' },
})
const answersRevealed = computed(() =>
    props.wrongTopics.some(t => (t.questions || []).some(q => q.explanation))
)
const TYPE_LABELS = { multiple_choice: 'MCQ', true_false: 'T/F', short_answer: 'Short', fill_in_the_blank: 'Fill' }
function typeLabel(type) { return TYPE_LABELS[type] ?? 'Q' }
function formatAnswer(value) {
    if (Array.isArray(value)) return value.join(', ')
    if (value === null || value === undefined || value === '') return '—'
    return String(value)
}
</script>

<style scoped>
/* ── Card ── */

.card {
    background: var(--surface);
    border: 1.5px solid var(--card-border);
    border-radius: var(--radius-lg);
    padding: 1.375rem 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    box-shadow: var(--shadow-sm);
}

.card-title {
    font-size: 0.875rem;
    font-weight: 700;
    color: var(--text-main);
    display: flex;
    align-items: center;
    gap: 0.45rem;
}

/* ── Weakness Groups ── */

.weakness-groups {
    display: flex;
    flex-direction: column;
    gap: 1.125rem;
}

.weakness-group {
    display: flex;
    flex-direction: column;
    gap: 0.625rem;
}

.group-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 0.5rem;
    border-bottom: 1.5px solid var(--gray-light);
}

.group-topic {
    font-size: 0.84rem;
    font-weight: 700;
    color: var(--text-main);
}

.group-count {
    font-size: 0.75rem;
    color: var(--text-muted);
}

.weakness-items {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.weakness-item {
    background: var(--theme-bg-fff7ed);
    border: 1px solid var(--theme-border-fed7aa);
    border-radius: var(--radius-md);
    padding: 0.875rem 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.weakness-item-top {
    display: flex;
    align-items: flex-start;
    gap: 0.625rem;
}

.q-type-badge {
    font-size: 0.625rem;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 999px;
    white-space: nowrap;
    flex-shrink: 0;
    margin-top: 2px;
}

.q-type-badge.multiple_choice {
    background: var(--theme-bg-eff6ff);
    color: var(--theme-fg-2563eb);
}

.q-type-badge.true_false {
    background: var(--light-green);
    color: var(--text-green);
}

.q-type-badge.short_answer {
    background: var(--light-yellow);
    color: var(--theme-fg-b45309);
}

.weakness-q-text {
    font-size: 0.84rem;
    color: var(--text-main);
    line-height: 1.55;
    white-space: pre-wrap;
}

.answer-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.answer-label {
    font-size: 0.75rem;
    color: var(--text-muted);
    flex-shrink: 0;
}

.answer-val {
    font-size: 0.8125rem;
    font-weight: 600;
    color: var(--text-green);
}

/* ── Explanation ── */

.explanation-box {
    background: var(--light-yellow);
    border-left: 3px solid var(--primary-pink);
    padding: 0.75rem 0.875rem;
    border-radius: 0 var(--radius-md) var(--radius-md) 0;
}

.explanation-label {
    font-size: 0.75rem;
    font-weight: 700;
    color: var(--primary-pink);
    margin-bottom: 5px;
    display: flex;
    align-items: center;
    gap: 0.3rem;
}

.explanation-text {
    font-size: 0.8125rem;
    color: var(--text-main);
    line-height: 1.6;
    white-space: pre-wrap;
}


/* ── Review Link ── */

.action-row {
    padding-top: 0.75rem;
    border-top: 1px dashed var(--card-border);
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.answer-val.your { color: var(--theme-fg-b91c1c); }

.explanation-hidden {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-style: italic;
}

.no-lesson {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-style: italic;
  margin-top: 0.5rem;
}

.review-link {
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
    font-size: 0.8125rem;
    font-weight: 600;
    color: var(--primary-pink);
    text-decoration: none;
    background: var(--light-pink);
    padding: 0.375rem 0.75rem;
    border-radius: var(--radius-md);
    transition: background 0.15s ease, opacity 0.15s ease;
    width: fit-content;
}

.review-link:hover {
    background: var(--theme-bg-ffb3cc);
}

.page-ref-text {
    color: var(--primary-hover);
    font-weight: 700;
}

/* ── Perfect Card ── */

.perfect-card {
    background: var(--theme-bg-f0fdf4);
    border: 1.5px solid var(--theme-border-bbf7d0);
    border-radius: var(--radius-lg);
    padding: 2.25rem;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.75rem;
    box-shadow: var(--shadow-sm);
}

.perfect-icon {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: var(--light-green);
    color: var(--text-green);
    display: flex;
    align-items: center;
    justify-content: center;
}

.perfect-text {
    font-size: 0.9375rem;
    font-weight: 600;
    color: var(--text-green);
}


.review-section { display: flex; flex-direction: column; gap: 1.25rem; }
.review-question-image { display: block; max-width: 100%; max-height: 360px; object-fit: contain; margin: 8px 0; }
@media (max-width: 600px) {
    .weakness-item-top, .answer-row { flex-wrap: wrap; }
}
</style>
