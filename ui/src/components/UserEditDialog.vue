<script setup lang="ts">
import { toTypedSchema } from "@vee-validate/zod"
import axios from "axios"
import { useForm } from "vee-validate"
import { z } from "zod"

import { usersApi } from "@/api"
import type { components } from "@/api/schema"
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
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"

type User = components["schemas"]["UserResponse"]

interface FormValues {
  email: string
  role: "user" | "admin"
  is_active: boolean
}

const props = defineProps<{
  user: User
}>()

const emit = defineEmits<{
  close: []
  updated: [user: User]
}>()

const form = useForm<FormValues>({
  validationSchema: toTypedSchema(
    z.object({
      email: z.string().email("Enter a valid email"),
      role: z.enum(["user", "admin"]),
      is_active: z.boolean(),
    }),
  ),
  initialValues: {
    email: props.user.email,
    role: props.user.role === "admin" ? "admin" : "user",
    is_active: props.user.is_active,
  },
})

const onSubmit = form.handleSubmit(async (values) => {
  try {
    const updated = await usersApi.updateAsAdmin(props.user.id, {
      email: values.email !== props.user.email ? values.email : undefined,
      role: values.role,
      is_active: values.is_active,
    })
    emit("updated", updated)
  } catch (err) {
    form.setFieldError("email", explain(err))
  }
})

function explain(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const detail = (err.response?.data as { detail?: string } | undefined)?.detail
    if (typeof detail === "string") return detail
  }
  if (err instanceof Error) return err.message
  return "Update failed"
}
</script>

<template>
  <Dialog :open="true" @update:open="(open) => !open && emit('close')">
    <DialogContent>
      <DialogHeader>
        <DialogTitle>Edit user</DialogTitle>
        <DialogDescription> Change email, role, or active status. </DialogDescription>
      </DialogHeader>

      <form class="space-y-4" @submit="onSubmit">
        <FormField v-slot="{ componentField }" name="email">
          <FormItem>
            <FormLabel>Email</FormLabel>
            <FormControl>
              <Input type="email" v-bind="componentField" />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>

        <FormField v-slot="{ componentField }" name="role">
          <FormItem>
            <FormLabel>Role</FormLabel>
            <Select v-bind="componentField">
              <FormControl>
                <SelectTrigger>
                  <SelectValue placeholder="Select role" />
                </SelectTrigger>
              </FormControl>
              <SelectContent>
                <SelectItem value="user">user</SelectItem>
                <SelectItem value="admin">admin</SelectItem>
              </SelectContent>
            </Select>
            <FormMessage />
          </FormItem>
        </FormField>

        <FormField v-slot="{ value, handleChange }" name="is_active">
          <FormItem class="flex items-center justify-between rounded-lg border p-3">
            <div class="space-y-0.5">
              <FormLabel class="text-sm">Active</FormLabel>
              <p class="text-xs text-muted-foreground">
                Disabled users cannot sign in.
              </p>
            </div>
            <FormControl>
              <Switch :model-value="value" @update:model-value="handleChange" />
            </FormControl>
          </FormItem>
        </FormField>

        <DialogFooter>
          <Button type="button" variant="outline" @click="emit('close')">
            Cancel
          </Button>
          <Button type="submit" :disabled="form.isSubmitting.value">
            {{ form.isSubmitting.value ? "Saving…" : "Save" }}
          </Button>
        </DialogFooter>
      </form>
    </DialogContent>
  </Dialog>
</template>
