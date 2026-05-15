<script setup lang="ts">
import LoginForm from "@/components/LoginForm.vue"

definePageMeta({
  layout: false,
  publicOnly: true,
})

useSeoMeta({
  title: "Sign in — SocialpyKit",
  description: "Sign in to your SocialpyKit account.",
})
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-background p-4">
    <div class="w-full max-w-md">
      <LoginForm />
      <p class="mt-4 text-center text-sm text-muted-foreground">
        Don't have an account?
        <NuxtLink to="/register" class="font-medium text-primary hover:underline">
          Create one
        </NuxtLink>
      </p>
    </div>
  </div>
</template>
