<script setup lang="ts">
import { Button } from "@/components/ui/button"
import { useAuthStore } from "@/stores/auth"

const store = useAuthStore()
</script>

<template>
  <div class="min-h-screen bg-background">
    <header
      class="sticky top-0 z-10 flex h-14 items-center justify-between border-b bg-background px-6"
    >
      <NuxtLink to="/" class="text-lg font-semibold">SocialpyKit</NuxtLink>
      <nav class="flex items-center gap-4 text-sm">
        <NuxtLink to="/pricing" class="text-muted-foreground hover:text-foreground">
          Pricing
        </NuxtLink>
        <template v-if="store.isAuthenticated">
          <Button as-child variant="default" size="sm">
            <NuxtLink to="/dashboard">Dashboard</NuxtLink>
          </Button>
        </template>
        <template v-else>
          <NuxtLink to="/login" class="text-muted-foreground hover:text-foreground">
            Sign in
          </NuxtLink>
          <Button as-child variant="default" size="sm">
            <NuxtLink to="/register">Get started</NuxtLink>
          </Button>
        </template>
      </nav>
    </header>

    <main>
      <slot />
    </main>

    <footer class="border-t px-6 py-8 text-sm text-muted-foreground">
      <div class="mx-auto flex max-w-5xl items-center justify-between">
        <span>&copy; SocialpyKit</span>
        <a
          href="https://github.com/hasankaantan/SocialpyKit"
          class="hover:text-foreground"
          >GitHub</a
        >
      </div>
    </footer>
  </div>
</template>
