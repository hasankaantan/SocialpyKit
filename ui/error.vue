<script setup lang="ts">
import type { NuxtError } from "#app"

defineProps<{ error: NuxtError }>()

function handleError(): Promise<void> {
  return clearError({ redirect: "/" })
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-background p-4">
    <div class="text-center">
      <h1 class="text-4xl font-bold tracking-tight">
        {{ error.statusCode === 404 ? "Page not found" : "Something went wrong" }}
      </h1>
      <p class="mt-2 text-muted-foreground">
        {{ error.statusMessage ?? error.message }}
      </p>
      <button
        class="mt-6 inline-flex items-center rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90"
        type="button"
        @click="handleError"
      >
        Go home
      </button>
    </div>
  </div>
</template>
