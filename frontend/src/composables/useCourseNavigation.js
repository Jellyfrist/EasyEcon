import { ref } from 'vue'

const collapsed = ref(false)

export function useCourseNavigation() {
  return { collapsed }
}
