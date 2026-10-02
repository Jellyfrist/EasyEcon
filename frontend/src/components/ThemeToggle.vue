<template>
  <button class="theme-toggle" type="button" :aria-label="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
    :title="isDark ? 'Light mode' : 'Dark mode'" :aria-pressed="isDark" @click="toggleTheme">
    <span class="material-symbols-outlined" aria-hidden="true">{{ isDark ? 'light_mode' : 'dark_mode' }}</span>
  </button>
</template>

<script setup>
import { useTheme } from '@/composables/useTheme'
const { isDark, toggleTheme } = useTheme()
</script>

<style scoped>
.theme-toggle { display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0; width: 44px; height: 44px; border:1px solid var(--card-border); border-radius: 50%; background:var(--surface); color:var(--text-main); cursor: pointer; }
.theme-toggle:hover { background:var(--gray-light); }
.theme-toggle:focus-visible { outline:2px solid var(--primary-pink); outline-offset: 3px; }
.theme-toggle .material-symbols-outlined { font-size: 20px; }
</style>
