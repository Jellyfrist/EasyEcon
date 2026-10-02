<template>
  <div class="lesson-html lesson-rendered" v-html="displayHtml"></div>
</template>

<script setup>
import '@/assets/lesson-content.css'
import { computed } from 'vue'

const props = defineProps({
  html: { type: String, default: '' },
  omitLeadingTitle: { type: String, default: '' },
})
const normalizeTitle = title => title.normalize('NFC').replace(/\s+/g, ' ').trim().toLocaleLowerCase()
const displayHtml = computed(() => {
  if (!props.omitLeadingTitle || !props.html) return props.html
  const template = document.createElement('template')
  template.innerHTML = props.html
  const first = [...template.content.childNodes].find(node => node.nodeType === 1 || node.textContent.trim())
  if (!first || !/^H[1-6]$/.test(first.nodeName) || normalizeTitle(first.textContent) !== normalizeTitle(props.omitLeadingTitle)) return props.html
  first.remove()
  return template.innerHTML
})
</script>
