<template>
  <div class="feature-toolbar">
    <div class="feature-toolbar-top">
      <h2>{{ title }}</h2>
      <slot name="search" />
    </div>
    <slot />
  </div>
</template>

<script setup>
defineProps({ title: { type: String, default: 'Filter' } })
</script>

<style>
.feature-toolbar-top { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 16px 20px; border-bottom: 1px solid var(--card-border); }
.feature-toolbar-top h2 { font-size: 0.85rem; font-weight: 600; color: var(--text-main); margin: 0; }
.feature-page .feature-toolbar .search-box { display: flex; align-items: center; gap: 8px; background: var(--gray-light); border: 1px solid var(--card-border); border-radius: 8px; color: var(--text-muted); padding: 8px 12px; }
.feature-page .feature-toolbar .search-box input { color: var(--text-main); font-family: inherit; background: transparent; min-width: 0; }
.feature-page .feature-toolbar .search-box input::placeholder { color: var(--text-muted); }
.feature-page .feature-toolbar .search-box svg { color: var(--text-muted); }
.feature-page .feature-toolbar .search-clear { color: var(--text-muted); background: transparent; }
@media (max-width: 600px) {
  .feature-toolbar-top { flex-wrap: wrap; padding: 16px; }
  .feature-page .feature-toolbar .search-box { flex: 1 1 100%; width: 100%; }
}
</style>
