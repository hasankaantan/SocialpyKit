<script setup lang="ts">
import { RouterLink } from "vue-router"
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-background">
    <div class="text-center">
      <p class="text-6xl font-bold text-muted-foreground">404</p>
      <p class="mt-2 text-lg">Page not found</p>
      <RouterLink to="/" class="mt-4 inline-block text-primary hover:underline">
        Go home
      </RouterLink>
    </div>
  </div>
</template>
