<script setup lang="ts">
import {
  ActivityIcon,
  AlertCircleIcon,
  ArrowRightIcon,
  CheckCircleIcon,
  Loader2Icon,
} from "lucide-vue-next"
import { onMounted, ref } from "vue"
import { RouterLink } from "vue-router"

import { healthApi } from "@/api"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { useAuthStore } from "@/stores/auth"

const store = useAuthStore()
const healthState = ref<"loading" | "ok" | "down">("loading")

onMounted(async () => {
  try {
    await healthApi.check()
    healthState.value = "ok"
  } catch {
    healthState.value = "down"
  }
})
</script>

<template>
  <section class="space-y-6">
    <header class="space-y-1">
      <h1 class="text-2xl font-semibold tracking-tight">
        Welcome back, {{ store.user?.email }}
      </h1>
      <p class="text-sm text-muted-foreground">
        SocialpyKit dashboard — manage your account or, if you're an admin, the whole
        user base.
      </p>
    </header>

    <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      <Card>
        <CardHeader class="pb-3">
          <CardTitle class="flex items-center gap-2 text-sm font-medium">
            <ActivityIcon class="h-4 w-4" />
            API health
          </CardTitle>
          <CardDescription>
            Live status of the FastAPI backend and its database.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div
            v-if="healthState === 'loading'"
            class="flex items-center gap-2 text-sm text-muted-foreground"
          >
            <Loader2Icon class="h-4 w-4 animate-spin" />
            Checking…
          </div>
          <div
            v-else-if="healthState === 'ok'"
            class="flex items-center gap-2 text-sm font-medium text-emerald-600 dark:text-emerald-500"
          >
            <CheckCircleIcon class="h-4 w-4" />
            All systems operational
          </div>
          <div
            v-else
            class="flex items-center gap-2 text-sm font-medium text-destructive"
          >
            <AlertCircleIcon class="h-4 w-4" />
            API unreachable
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader class="pb-3">
          <CardTitle class="text-sm font-medium">Profile</CardTitle>
          <CardDescription>Update your email or password.</CardDescription>
        </CardHeader>
        <CardContent>
          <Button as-child variant="outline" size="sm">
            <RouterLink to="/dashboard/profile">
              Open profile
              <ArrowRightIcon class="ml-2 h-4 w-4" />
            </RouterLink>
          </Button>
        </CardContent>
      </Card>

      <Card v-if="store.user?.role === 'admin'">
        <CardHeader class="pb-3">
          <CardTitle class="text-sm font-medium">Users</CardTitle>
          <CardDescription>Admin-only view of every user.</CardDescription>
        </CardHeader>
        <CardContent>
          <Button as-child variant="outline" size="sm">
            <RouterLink to="/dashboard/users">
              Manage users
              <ArrowRightIcon class="ml-2 h-4 w-4" />
            </RouterLink>
          </Button>
        </CardContent>
      </Card>
    </div>
  </section>
</template>
