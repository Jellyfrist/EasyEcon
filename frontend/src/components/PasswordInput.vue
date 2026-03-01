<template>
    <div class="form-group">
        <div v-if="showLabel" class="label-row">
            <label>{{ label }}</label>
            <slot name="label-extra"></slot>
        </div>
        <div class="password-wrapper">
            <input :value="modelValue" @input="$emit('update:modelValue', $event.target.value)" :type="showPassword ? 'text' : 'password'" :placeholder="placeholder" :required="required" />
            <button type="button" @click="showPassword = !showPassword" class="toggle-btn" :aria-label="showPassword ? 'Hide password' : 'Show password'">
                    <span class="material-symbols-outlined">
                        {{ showPassword ? 'visibility_off' : 'visibility' }}
                    </span>
                </button>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';

defineProps({
    modelValue: {
        type: String,
        default: ''
    },
    label: {
        type: String,
        default: 'Password'
    },
    placeholder: {
        type: String,
        default: '••••••••'
    },
    required: {
        type: Boolean,
        default: true
    },
    showLabel: {
        type: Boolean,
        default: true
    }
});

defineEmits(['update:modelValue']);

const showPassword = ref(false);
</script>

<style scoped>
.form-group {
    margin-bottom: 18px;
}

.label-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
}

.form-group label {
    display: block;
    font-weight: 600;
    font-size: 14px;
    color: #374151;
}

.password-wrapper {
    position: relative;
}

input {
    width: 100%;
    padding: 12px 16px;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    background: #f9fafb;
    font-size: 16px;
    box-sizing: border-box;
}

input:focus {
    outline: none;
    border-color: #0a703c;
    background: white;
    box-shadow: 0 0 0 4px rgba(10, 112, 60, 0.1);
}

.toggle-btn {
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    color: #9ca3af;
    cursor: pointer;
    padding: 4px;
    display: flex;
    align-items: center;
}

.toggle-btn:hover {
    color: #6b7280;
}
</style>