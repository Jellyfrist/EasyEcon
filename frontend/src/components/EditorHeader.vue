<template>
  <header ref="header" class="editor-topbar" :class="{ 'editor-topbar-inline': inline }" :style="{ top: navbarOffset + 'px' }">
    <div class="topbar-main">
      <router-link v-if="backTo" :to="backTo" class="editor-back" aria-label="Back">
        <span class="material-symbols-outlined">arrow_back</span>
      </router-link>
      <div class="topbar-left">
        <nav class="topbar-breadcrumb" aria-label="Breadcrumb">
          <template v-for="(crumb, index) in breadcrumbs" :key="index">
            <span v-if="index" class="crumb-sep" aria-hidden="true">/</span>
            <router-link :to="crumb.to" :class="index === breadcrumbs.length - 1 ? 'crumb-current' : 'crumb-link'"
              :aria-current="index === breadcrumbs.length - 1 ? 'page' : undefined">{{ crumb.label }}</router-link>
          </template>
        </nav>
        <h1 class="topbar-title">{{ title }}</h1>
        <slot name="status" />
      </div>
    </div>
    <div v-if="$slots.tools" class="topbar-tools"><slot name="tools" /></div>
    <div class="topbar-actions header-actions"><slot /></div>
  </header>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useNavbarOffset } from '@/composables/useNavbarOffset'

defineProps({ title: String, breadcrumbs: { type: Array, required: true }, backTo: [String, Object], inline: Boolean })
const emit = defineEmits(['resize'])
const header = ref(null)
const navbarOffset = useNavbarOffset()
let observer
onMounted(() => {
  observer = new ResizeObserver(() => emit('resize', header.value.getBoundingClientRect().height))
  observer.observe(header.value)
})
onUnmounted(() => observer?.disconnect())
</script>

<style scoped>
/* Shared editor navigation; retain its existing visual identity. */
.editor-topbar {
  display: flex; align-items: center; justify-content: space-between;
  gap: 1rem; padding: 16px var(--feature-gutter); background: var(--surface);
  border-bottom: 1px solid var(--theme-border-e8edf3); position: sticky; z-index: 100;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}
.topbar-main { display: flex; align-items: center; gap: 0.75rem; min-width: 0; }
.topbar-left { display: flex; flex-direction: column; gap: 0.2rem; min-width: 0; }
.topbar-breadcrumb { display: flex; align-items: center; flex-wrap: wrap; gap: 0.4rem; font-size: 0.75rem; }
.crumb-link { color: var(--theme-fg-94a3b8); text-decoration: none; font-weight: 500; transition: color 0.15s; }
.crumb-link:hover, .crumb-current:hover { color: var(--theme-fg-ed4081); }
.crumb-sep { color: #cbd5e1; font-size: 0.7rem; }
.crumb-current { color: var(--theme-fg-475569); font-weight: 600; text-decoration: none; }
.topbar-title { font-size: 1.25rem; font-weight: 600; color: var(--text-main); letter-spacing: -0.01em; margin: 0; overflow-wrap: anywhere; }
.topbar-actions { display: flex; gap: 0.75rem; align-items: center; flex-wrap: wrap; }
.editor-back { display: flex; align-items: center; justify-content: center; color: var(--text-muted); width: 36px; height: 36px; flex-shrink: 0; text-decoration: none; }
.editor-topbar :is(a, button):focus-visible { outline: 2px solid var(--primary-pink); outline-offset: 3px; }
.editor-topbar-inline { position: sticky; padding: 0; box-shadow: none; border: 0; margin-bottom: 28px; }
@media (max-width: 900px) {
  .editor-topbar { flex-wrap: wrap; padding: 0.85rem 1.25rem; gap: 0.75rem; }
  .topbar-main { flex: 1 1 100%; }
  .topbar-actions { gap: 0.5rem; }
}
</style>
