<script setup lang="ts">
import axios from "axios"
import { ref } from "vue"

import { useAuthStore } from "../stores/auth"

const PASSWORD_MIN_LENGTH = 8

const store = useAuthStore()
const email = ref("")
const password = ref("")
const error = ref<string | null>(null)
const submitting = ref(false)

async function onSubmit(): Promise<void> {
  error.value = null
  submitting.value = true
  try {
    await store.register(email.value, password.value)
  } catch (err) {
    error.value = explain(err)
  } finally {
    submitting.value = false
  }
}

function explain(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const detail = (err.response?.data as { detail?: string } | undefined)?.detail
    if (typeof detail === "string") return detail
  }
  if (err instanceof Error) return err.message
  return "Registration failed"
}
</script>

<template>
  <form class="auth-form" @submit.prevent="onSubmit">
    <h2>Create an account</h2>

    <label>
      Email
      <input
        v-model="email"
        type="email"
        autocomplete="email"
        required
        :disabled="submitting"
      />
    </label>

    <label>
      Password
      <input
        v-model="password"
        type="password"
        autocomplete="new-password"
        :minlength="PASSWORD_MIN_LENGTH"
        required
        :disabled="submitting"
      />
    </label>

    <button type="submit" :disabled="submitting">
      <span v-if="submitting">Creating account…</span>
      <span v-else>Create account</span>
    </button>

    <p v-if="error" class="auth-form__error" role="alert">{{ error }}</p>
  </form>
</template>

<style scoped>
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-width: 320px;
}

.auth-form label {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.875rem;
}

.auth-form input {
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.auth-form button {
  padding: 0.6rem;
  background: #1f883d;
  color: white;
  border: 0;
  border-radius: 4px;
  cursor: pointer;
}

.auth-form button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.auth-form__error {
  color: #d1242f;
  margin: 0;
  font-size: 0.875rem;
}
</style>
