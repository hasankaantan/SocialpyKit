<script setup lang="ts">
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

useSeoMeta({
  title: "Pricing — SocialpyKit",
  description: "Simple pricing for SocialpyKit.",
})

const tiers = [
  {
    name: "Self-hosted",
    price: "$0",
    features: ["MIT license", "Full source", "Bring your own infra"],
  },
  {
    name: "Pro support",
    price: "Contact",
    features: ["Priority issues", "Migration help", "Custom modules"],
  },
] as const
</script>

<template>
  <section class="mx-auto max-w-5xl px-6 py-24">
    <h1 class="text-center text-4xl font-bold tracking-tight">Pricing</h1>
    <div class="mt-12 grid gap-6 md:grid-cols-2">
      <Card v-for="tier in tiers" :key="tier.name">
        <CardHeader>
          <CardTitle>{{ tier.name }}</CardTitle>
        </CardHeader>
        <CardContent>
          <p class="text-3xl font-bold">{{ tier.price }}</p>
          <ul class="mt-6 space-y-2 text-sm text-muted-foreground">
            <li v-for="feature in tier.features" :key="feature">{{ feature }}</li>
          </ul>
          <Button as-child class="mt-6 w-full">
            <NuxtLink to="/register">Start</NuxtLink>
          </Button>
        </CardContent>
      </Card>
    </div>
  </section>
</template>
