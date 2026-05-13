<script setup lang="ts">
import LoginForm from "@/components/LoginForm.vue"
import { RouterLink } from "vue-router"
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-background p-4">
    <div class="w-full max-w-md">
      <LoginForm />
      <p class="mt-4 text-center text-sm text-muted-foreground">
        Don't have an account?
        <RouterLink to="/register" class="font-medium text-primary hover:underline">
          Create one
        </RouterLink>
      </p>
    </div>
  </div>
</template>
