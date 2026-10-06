<template>
  <section ref="page" class="feature-page" :class="{ 'feature-page-fluid': fluid }" :style="{ '--feature-sticky-top': `${navbarOffset + headerHeight}px` }">
    <slot name="header" />
    <div :class="{ 'feature-workspace': $slots.navigation }">
      <slot name="navigation" />
      <div class="feature-body"><slot /></div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useNavbarOffset } from '@/composables/useNavbarOffset'
defineProps({ fluid: { type: Boolean, default: false } })
const page = ref(null)
const headerHeight = ref(0)
const navbarOffset = useNavbarOffset()
let observer
onMounted(() => {
  const header = page.value.querySelector('.editor-topbar:not(.editor-topbar-inline)')
  if (!header) return
  observer = new ResizeObserver(() => { headerHeight.value = header.getBoundingClientRect().height })
  observer.observe(header)
  headerHeight.value = header.getBoundingClientRect().height
})
onUnmounted(() => observer?.disconnect())
</script>

<style>
.feature-page {
  background: var(--surface);
  color: var(--text-main);
  min-height: calc(100dvh - 64px);
  font-family: inherit;
}
.feature-page.student-course-page { background: var(--gray-light); }
.feature-page.student-course-page .student-section-hero {
  position: static;
  width: 100%;
  margin: 0 0 20px;
  padding: 0 0 14px;
  border: 0;
  border-bottom: 1px solid var(--card-border);
  border-radius: 0;
  background: transparent;
  color: var(--text-main);
  box-shadow: none;
}
.feature-page.student-course-page .student-section-hero .topbar-title { color: var(--text-main); font-size: 1.5rem; }
.feature-page.student-course-page .student-section-hero .topbar-breadcrumb :is(.crumb-link, .crumb-current) { color: var(--text-muted); }
.feature-page.student-course-page .student-section-hero .topbar-breadcrumb .crumb-link:hover { color: var(--primary-pink); }
.feature-page.student-course-page .student-section-hero .crumb-sep { color: var(--text-muted); }
.feature-body {
  width: 100%;
  max-width: var(--feature-width);
  min-width: 0;
  margin: 0 auto;
  padding: var(--feature-gutter) var(--feature-gutter) 48px;
}
.feature-workspace { --course-navigation-width: 260px; display: grid; grid-template-columns: 260px minmax(0, 1fr); }
.feature-workspace:has(> .navigation-collapsed) { --course-navigation-width: 72px; grid-template-columns: 72px minmax(0, 1fr); }
.feature-workspace:has(> .navigation-collapsed) > .feature-body { max-width: none; }
.feature-page-fluid .feature-body { max-width: none; padding: 0; }
.feature-body > :is(.page-card, .card, .form-card, .score-hero, .stats-bar, .session-list, .exam-list, .error-banner) { margin-bottom: 24px; }
.feature-page .card-header h2 { font-size: 1rem; font-weight: 600; margin: 0; }
.feature-page .header-status { font-size: 0.75rem; color: var(--text-muted); margin: 0; }
.feature-page :is(.feature-body, .topbar-actions) :is(.card, .form-card, .ce-card, .action-card, .module-card, .session-card, .exam-card, .stat-card, .page-card, .settings-card, .questions-card, .section-card) {
  border: 1px solid var(--card-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  background: var(--surface);
}
.feature-page .page-card:has(> .filter-bar), .feature-page .page-card:has(> .template-summary) {
  overflow: visible;
}
.feature-page :is(.feature-body, .topbar-actions) :is(.btn-primary, .btn-create, .ce-btn-primary, .le-save-btn, .btn-header-save, .btn-create-exam, .submit-btn) {
  min-height: 40px;
  border-radius: 8px;
  background: var(--primary-pink);
  color: var(--white);
  box-shadow: none;
  font-family: inherit;
  font-size: 0.85rem;
  font-weight: 600;
}
.feature-page :is(.feature-body, .topbar-actions) :is(.btn-primary, .btn-create, .ce-btn-primary, .le-save-btn, .btn-header-save, .btn-create-exam, .submit-btn):hover:not(:disabled) {
  background: var(--primary-hover);
  transform: none;
  box-shadow: none;
}
.feature-page :is(.feature-body, .topbar-actions) :is(.btn-primary, .btn-create, .ce-btn-primary, .le-save-btn, .btn-header-save, .btn-create-exam, .submit-btn):disabled { opacity: 0.55; cursor: not-allowed; }
.feature-page .topbar-actions :is(button, .ce-btn, .btn-header-ghost) {
  min-height: 40px;
  padding: 8px 16px;
  border-radius: 8px;
  font-family: inherit;
  font-size: 0.85rem;
  font-weight: 600;
  box-shadow: none;
  transform: none;
}
.feature-page .topbar-actions :is(.ce-btn-ghost, .btn-header-ghost, .le-add-section-btn) {
  background: var(--surface);
  color: var(--text-main);
  border: 1px solid var(--card-border);
}
.feature-page .topbar-actions :is(.ce-btn-ghost, .btn-header-ghost, .le-add-section-btn):hover { background: var(--gray-light); }
@media (max-width: 768px) {
  .feature-body { padding: 20px 16px 32px; }
  .feature-page-fluid .feature-body { padding: 0; }
  .feature-workspace { grid-template-columns: minmax(0, 1fr); }
  .feature-workspace:has(> .navigation-collapsed) { --course-navigation-width: 72px; grid-template-columns: 72px minmax(0, 1fr); }
  .feature-page.student-course-page .student-section-hero { margin-bottom: 16px; padding-bottom: 12px; }
  .feature-page.student-course-page .student-section-hero .topbar-title { font-size: 1.3rem; }
}
</style>
