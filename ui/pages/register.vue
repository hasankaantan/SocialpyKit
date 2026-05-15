<script setup lang="ts">
import RegisterForm from "@/components/RegisterForm.vue"

definePageMeta({
  layout: false,
  publicOnly: true,
})

useSeoMeta({
  title: "Create account — SocialpyKit",
  description: "Create a new SocialpyKit account.",
})
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-background p-4">
    <div class="w-full max-w-md">
      <RegisterForm />
      <p class="mt-4 text-center text-sm text-muted-foreground">
        Already have an account?
        <NuxtLink to="/login" class="font-medium text-primary hover:underline">
          Sign in
        </NuxtLink>
      </p>
    </div>
  </div>
</template>
