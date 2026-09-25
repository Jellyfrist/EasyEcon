<template>
  <div class="options-section">

    <div
      v-for="opt in question.options"
      :key="opt.key"
      class="option-row"
    >

      <input
        type="radio"
        :name="`q_${question._lid}`"
        :value="opt.key"
        :checked="question.correct_answer === opt.key"
        @change="$emit('update-question','correct_answer',opt.key)"
      />

      <span class="option-key">
        {{ opt.key }}
      </span>

      <input
        class="input-field"
        :value="opt.text"
        type="text"
        :placeholder="`Option ${opt.key}`"
        @input="$emit('update-option',opt.key,$event.target.value)"
      />

    </div>

    <p class="hint-text">
      Select the correct answer
    </p>

  </div>
</template>

<script setup>
defineProps({
  question: Object
})

defineEmits([
  'update-option',
  'update-question'
])
</script>