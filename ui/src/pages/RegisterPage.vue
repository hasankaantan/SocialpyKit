<script setup lang="ts">
import RegisterForm from "@/components/RegisterForm.vue"
import { RouterLink } from "vue-router"
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-background p-4">
    <div class="w-full max-w-md">
      <RegisterForm />
      <p class="mt-4 text-center text-sm text-muted-foreground">
        Already have an account?
        <RouterLink to="/login" class="font-medium text-primary hover:underline">
          Sign in
        </RouterLink>
      </p>
    </div>
  </div>
</template>
