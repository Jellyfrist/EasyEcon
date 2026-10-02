<template>
  <div class="lesson-html lesson-rendered" v-html="html"></div>
</template>

<script setup>
import '@/assets/lesson-content.css'
defineProps({ html: { type: String, default: '' } })
</script>
