import { ref, onMounted, onUnmounted } from 'vue'

// Headers sit below the existing sticky navbar, including when it wraps.
export function useNavbarOffset() {
  const navbarOffset = ref(0)
  let observer
  onMounted(() => {
    const navbar = document.querySelector('.navbar')
    if (!navbar) return
    observer = new ResizeObserver(() => {
      navbarOffset.value = navbar.getBoundingClientRect().height
    })
    observer.observe(navbar)
    navbarOffset.value = navbar.getBoundingClientRect().height
  })
  onUnmounted(() => observer?.disconnect())
  return navbarOffset
}
