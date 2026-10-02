import { computed, ref } from 'vue'

const theme = ref(document.documentElement.dataset.theme || 'light')

export function useTheme() {
  const isDark = computed(() => theme.value === 'dark')
  function toggleTheme() {
    theme.value = isDark.value ? 'light' : 'dark'
    document.documentElement.dataset.theme = theme.value
    try { localStorage.setItem('easy-econ-theme', theme.value) } catch { /* Keep the selected theme in memory. */ }
  }
  return { isDark, toggleTheme }
}
