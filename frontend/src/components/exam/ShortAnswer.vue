<template>
  <div class="options-section short-answer">

    <label class="label-sm">
      Correct Answer
    </label>

    <input
      class="input-field"
      type="text"
      :value="question.correct_answer"
      placeholder="Expected answer..."
      @input="$emit('update-question','correct_answer',$event.target.value)"
    />

    <p class="hint-text">
      Student answer must match this value
    </p>

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