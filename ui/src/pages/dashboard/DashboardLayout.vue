<script setup lang="ts">
import { HomeIcon, LogOutIcon, UserIcon, UsersIcon } from "lucide-vue-next"
import { computed } from "vue"
import { RouterLink, RouterView, useRouter } from "vue-router"

import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useAuthStore } from "@/stores/auth"

const router = useRouter()
const store = useAuthStore()

const isAdmin = computed(() => store.user?.role === "admin")

const initials = computed(() => {
  const email = store.user?.email ?? ""
  return email.slice(0, 2).toUpperCase()
})

async function onLogout(): Promise<void> {
  store.logout()
  await router.push("/login")
}
</script>

<template>
  <div class="min-h-screen bg-background">
    <header
      class="sticky top-0 z-10 flex h-14 items-center justify-between border-b bg-background px-6"
    >
      <RouterLink to="/dashboard" class="text-lg font-semibold">
        SocialpyKit
      </RouterLink>

      <DropdownMenu>
        <DropdownMenuTrigger as-child>
          <Button variant="ghost" class="flex items-center gap-2 px-2">
            <Avatar class="h-8 w-8">
              <AvatarFallback>{{ initials }}</AvatarFallback>
            </Avatar>
            <span class="hidden text-sm sm:inline">{{ store.user?.email }}</span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" class="w-56">
          <DropdownMenuLabel class="font-normal">
            <div class="flex flex-col">
              <span class="text-sm font-medium">{{ store.user?.email }}</span>
              <span class="text-xs text-muted-foreground">
                {{ isAdmin ? "Administrator" : "Member" }}
              </span>
            </div>
          </DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem @click="onLogout">
            <LogOutIcon class="mr-2 h-4 w-4" />
            Sign out
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </header>

    <div class="flex">
      <aside class="hidden w-56 shrink-0 border-r p-4 md:block">
        <nav class="flex flex-col gap-1 text-sm">
          <RouterLink
            to="/dashboard"
            exact-active-class="bg-accent text-accent-foreground"
            class="flex items-center rounded-md px-3 py-2 transition hover:bg-accent/60"
          >
            <HomeIcon class="mr-2 h-4 w-4" />
            Dashboard
          </RouterLink>
          <RouterLink
            to="/dashboard/profile"
            active-class="bg-accent text-accent-foreground"
            class="flex items-center rounded-md px-3 py-2 transition hover:bg-accent/60"
          >
            <UserIcon class="mr-2 h-4 w-4" />
            Profile
          </RouterLink>
          <RouterLink
            v-if="isAdmin"
            to="/dashboard/users"
            active-class="bg-accent text-accent-foreground"
            class="flex items-center rounded-md px-3 py-2 transition hover:bg-accent/60"
          >
            <UsersIcon class="mr-2 h-4 w-4" />
            Users
          </RouterLink>
        </nav>
      </aside>

      <main class="flex-1 p-6">
        <RouterView />
      </main>
    </div>
  </div>
</template>
