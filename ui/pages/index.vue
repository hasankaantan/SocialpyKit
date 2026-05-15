<script setup lang="ts">
import { Button } from "@/components/ui/button"

useSeoMeta({
  title: "SocialpyKit — Production-grade FastAPI starter",
  description:
    "Strict, type-safe FastAPI starter kit with Nuxt 3 frontend, JWT auth, RBAC, and 100% test coverage.",
  ogTitle: "SocialpyKit",
  ogDescription: "Production-grade FastAPI starter kit.",
  ogType: "website",
})
</script>

<template>
  <section class="mx-auto max-w-5xl px-6 py-24 text-center">
    <h1 class="text-5xl font-bold tracking-tight">
      The production-grade FastAPI starter kit
    </h1>
    <p class="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground">
      Strict typing. 100% coverage. JWT auth + RBAC. Async SQLAlchemy. Nuxt 3 frontend.
      Built to ship, not to demo.
    </p>
    <div class="mt-10 flex items-center justify-center gap-4">
      <Button as-child size="lg">
        <NuxtLink to="/register">Get started</NuxtLink>
      </Button>
      <Button as-child variant="outline" size="lg">
        <a href="https://github.com/hasankaantan/SocialpyKit">View on GitHub</a>
      </Button>
    </div>
  </section>
</template>
