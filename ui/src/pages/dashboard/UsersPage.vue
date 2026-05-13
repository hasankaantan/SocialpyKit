<script setup lang="ts">
import axios from "axios"
import { MoreHorizontalIcon, PencilIcon, Trash2Icon } from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"
import { toast } from "vue-sonner"

import { usersApi } from "@/api"
import type { components } from "@/api/schema"
import UserEditDialog from "@/components/UserEditDialog.vue"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { useAuthStore } from "@/stores/auth"

type User = components["schemas"]["UserResponse"]

const store = useAuthStore()
const users = ref<User[]>([])
const loading = ref(true)
const editing = ref<User | null>(null)
const deleteTarget = ref<User | null>(null)
const deleting = ref(false)

const rowCount = computed(() => users.value.length)

async function load(): Promise<void> {
  loading.value = true
  try {
    users.value = [...(await usersApi.list())]
  } catch (err) {
    toast.error(explain(err))
  } finally {
    loading.value = false
  }
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString()
}

function onUserUpdated(updated: User): void {
  const index = users.value.findIndex((u) => u.id === updated.id)
  if (index !== -1) {
    users.value[index] = updated
  }
  editing.value = null
  toast.success(`Updated ${updated.email}`)
}

async function confirmDelete(): Promise<void> {
  if (deleteTarget.value === null) return
  const target = deleteTarget.value
  deleting.value = true
  try {
    await usersApi.deleteAsAdmin(target.id)
    users.value = users.value.filter((u) => u.id !== target.id)
    toast.success(`Deleted ${target.email}`)
    deleteTarget.value = null
  } catch (err) {
    toast.error(explain(err))
  } finally {
    deleting.value = false
  }
}

function explain(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const detail = (err.response?.data as { detail?: string } | undefined)?.detail
    if (typeof detail === "string") return detail
  }
  if (err instanceof Error) return err.message
  return "Request failed"
}

onMounted(load)
</script>

<template>
  <section class="space-y-6">
    <header>
      <h1 class="text-2xl font-semibold tracking-tight">Users</h1>
      <p class="mt-1 text-sm text-muted-foreground">
        {{
          loading
            ? "Loading users…"
            : `${rowCount} user${rowCount === 1 ? "" : "s"} on file.`
        }}
      </p>
    </header>

    <div class="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Email</TableHead>
            <TableHead>Role</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Created</TableHead>
            <TableHead class="w-12"></TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <template v-if="loading">
            <TableRow v-for="i in 4" :key="i">
              <TableCell colspan="5">
                <Skeleton class="h-6 w-full" />
              </TableCell>
            </TableRow>
          </template>
          <template v-else-if="rowCount === 0">
            <TableRow>
              <TableCell colspan="5" class="text-center text-muted-foreground">
                No users.
              </TableCell>
            </TableRow>
          </template>
          <template v-else>
            <TableRow v-for="user in users" :key="user.id">
              <TableCell class="font-medium">{{ user.email }}</TableCell>
              <TableCell>
                <Badge :variant="user.role === 'admin' ? 'default' : 'secondary'">
                  {{ user.role }}
                </Badge>
              </TableCell>
              <TableCell>
                <Badge :variant="user.is_active ? 'outline' : 'destructive'">
                  {{ user.is_active ? "active" : "disabled" }}
                </Badge>
              </TableCell>
              <TableCell class="text-sm text-muted-foreground">
                {{ formatDate(user.created_at) }}
              </TableCell>
              <TableCell>
                <DropdownMenu>
                  <DropdownMenuTrigger as-child>
                    <Button variant="ghost" size="icon" class="h-8 w-8">
                      <MoreHorizontalIcon class="h-4 w-4" />
                      <span class="sr-only">Open actions</span>
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" class="w-36">
                    <DropdownMenuItem class="gap-2" @click="editing = user">
                      <PencilIcon class="h-4 w-4" />
                      Edit
                    </DropdownMenuItem>
                    <DropdownMenuItem
                      :disabled="user.id === store.user?.id"
                      class="gap-2 text-destructive focus:text-destructive"
                      @click="deleteTarget = user"
                    >
                      <Trash2Icon class="h-4 w-4" />
                      Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </TableCell>
            </TableRow>
          </template>
        </TableBody>
      </Table>
    </div>

    <UserEditDialog
      v-if="editing"
      :user="editing"
      @close="editing = null"
      @updated="onUserUpdated"
    />

    <Dialog
      :open="deleteTarget !== null"
      @update:open="(open) => !open && (deleteTarget = null)"
    >
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Delete this user?</DialogTitle>
          <DialogDescription>
            {{ deleteTarget?.email }} will be removed permanently. There is no undo.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button variant="outline" @click="deleteTarget = null">Cancel</Button>
          <Button variant="destructive" :disabled="deleting" @click="confirmDelete">
            {{ deleting ? "Deleting…" : "Yes, delete" }}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </section>
</template>
