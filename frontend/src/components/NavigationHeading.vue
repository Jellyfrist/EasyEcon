<template>
  <div class="navigation-heading" :class="{ 'heading-collapsed': collapsed }">
    <h2 v-show="!collapsed">{{ title }}</h2>
    <button type="button" class="navigation-toggle" :aria-expanded="!collapsed"
      :aria-label="collapsed ? 'Open navigation' : 'Close navigation'"
      :title="collapsed ? 'Open navigation' : 'Close navigation'" @click="$emit('toggle')">
      <span class="material-symbols-outlined" aria-hidden="true">{{ collapsed ? 'menu' : 'chevron_left' }}</span>
    </button>
  </div>
</template>

<script setup>
defineProps({ title: String, collapsed: Boolean })
defineEmits(['toggle'])
</script>

<style scoped>
.navigation-heading { display: flex; align-items: center; gap: 4px; padding: 0 8px 20px 20px; }
h2 { font-size: 1.05rem; line-height: 1.5; font-weight: 600; flex: 1; min-width: 0; margin: 0; padding: 0; overflow-wrap: anywhere; }
.navigation-toggle { display: flex; align-items: center; justify-content: center; flex-shrink: 0; width: 44px; height: 44px; margin: 0; border: 0; border-radius: 8px; background: var(--surface); color: var(--text-muted); cursor: pointer; }
.navigation-toggle:hover { background: var(--gray-light); color: var(--primary-pink); }
.navigation-toggle:focus-visible { outline: 2px solid var(--primary-pink); outline-offset: -2px; }
.material-symbols-outlined { font-size: 18px; }
.heading-collapsed { justify-content: center; padding: 0 0 16px; }
@media (max-width: 768px) {
  .navigation-heading:not(.heading-collapsed) { padding-bottom: 12px; }
  h2 { font-size: 0.95rem; }
}
</style>
