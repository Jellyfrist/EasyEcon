<template>
  <div class="options-section truefalse">

    <div class="option-row">

      <input
        type="radio"
        :name="`q_${question._lid}`"
        value="true"
        :checked="question.correct_answer === 'true'"
        @change="$emit('update-question','correct_answer','true')"
      />

      <span class="option-key">True</span>

    </div>

    <div class="option-row">

      <input
        type="radio"
        :name="`q_${question._lid}`"
        value="false"
        :checked="question.correct_answer === 'false'"
        @change="$emit('update-question','correct_answer','false')"
      />

      <span class="option-key">False</span>

    </div>

  </div>
</template>

<script setup>
defineProps({
  question: Object
})

defineEmits([
  'update-question'
])
</script>