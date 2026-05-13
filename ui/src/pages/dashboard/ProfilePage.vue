<script setup lang="ts">
import { toTypedSchema } from "@vee-validate/zod"
import axios from "axios"
import { Trash2Icon } from "lucide-vue-next"
import { useForm } from "vee-validate"
import { ref } from "vue"
import { toast } from "vue-sonner"
import { useRouter } from "vue-router"
import { z } from "zod"

import { usersApi } from "@/api"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { useAuthStore } from "@/stores/auth"

const PASSWORD_MIN_LENGTH = 8
const PASSWORD_MAX_LENGTH = 72

interface EmailValues {
  email: string
}

interface PasswordValues {
  current_password: string
  new_password: string
}

const store = useAuthStore()
const router = useRouter()
const deleting = ref(false)
const deleteError = ref<string | null>(null)

// --- email form ---
const emailForm = useForm<EmailValues>({
  validationSchema: toTypedSchema(
    z.object({
      email: z.string().email("Enter a valid email"),
    }),
  ),
  initialValues: { email: store.user?.email ?? "" },
})

const onSubmitEmail = emailForm.handleSubmit(async (values) => {
  try {
    const updated = await usersApi.updateSelf({ email: values.email })
    store.user = updated
    toast.success("Email updated")
  } catch (err) {
    toast.error(explain(err))
  }
})

// --- password form ---
const passwordForm = useForm<PasswordValues>({
  validationSchema: toTypedSchema(
    z.object({
      current_password: z.string().min(1, "Current password is required"),
      new_password: z
        .string()
        .min(PASSWORD_MIN_LENGTH, `At least ${PASSWORD_MIN_LENGTH} characters`)
        .max(PASSWORD_MAX_LENGTH, `At most ${PASSWORD_MAX_LENGTH} bytes`),
    }),
  ),
  initialValues: { current_password: "", new_password: "" },
})

const onSubmitPassword = passwordForm.handleSubmit(async (values) => {
  try {
    await usersApi.updateSelf({
      current_password: values.current_password,
      new_password: values.new_password,
    })
    passwordForm.resetForm()
    toast.success("Password updated")
  } catch (err) {
    toast.error(explain(err))
  }
})

// --- delete ---
async function onDelete(): Promise<void> {
  deleteError.value = null
  deleting.value = true
  try {
    await usersApi.deleteSelf()
    store.logout()
    await router.push("/login")
    toast.success("Account deleted")
  } catch (err) {
    deleteError.value = explain(err)
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
</script>

<template>
  <section class="max-w-2xl space-y-6">
    <header>
      <h1 class="text-2xl font-semibold tracking-tight">Profile</h1>
      <p class="mt-1 text-sm text-muted-foreground">
        Manage your account email, password, and presence.
      </p>
    </header>

    <Card>
      <form @submit="onSubmitEmail">
        <CardHeader>
          <CardTitle>Email</CardTitle>
          <CardDescription>The address you use to sign in.</CardDescription>
        </CardHeader>
        <CardContent>
          <FormField v-slot="{ componentField }" name="email">
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input type="email" autocomplete="email" v-bind="componentField" />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>
        </CardContent>
        <CardFooter class="flex justify-end">
          <Button type="submit" :disabled="emailForm.isSubmitting.value">
            {{ emailForm.isSubmitting.value ? "Saving…" : "Save email" }}
          </Button>
        </CardFooter>
      </form>
    </Card>

    <Card>
      <form @submit="onSubmitPassword">
        <CardHeader>
          <CardTitle>Password</CardTitle>
          <CardDescription>
            Changing your password requires the current one.
          </CardDescription>
        </CardHeader>
        <CardContent class="space-y-4">
          <FormField v-slot="{ componentField }" name="current_password">
            <FormItem>
              <FormLabel>Current password</FormLabel>
              <FormControl>
                <Input
                  type="password"
                  autocomplete="current-password"
                  v-bind="componentField"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>
          <FormField v-slot="{ componentField }" name="new_password">
            <FormItem>
              <FormLabel>New password</FormLabel>
              <FormControl>
                <Input
                  type="password"
                  autocomplete="new-password"
                  v-bind="componentField"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>
        </CardContent>
        <CardFooter class="flex justify-end">
          <Button type="submit" :disabled="passwordForm.isSubmitting.value">
            {{ passwordForm.isSubmitting.value ? "Saving…" : "Save password" }}
          </Button>
        </CardFooter>
      </form>
    </Card>

    <Card class="border-destructive/40">
      <CardHeader>
        <CardTitle class="text-destructive">Danger zone</CardTitle>
        <CardDescription>
          Deleting your account is permanent and cannot be undone.
        </CardDescription>
      </CardHeader>
      <CardFooter class="flex justify-end">
        <Dialog>
          <DialogTrigger as-child>
            <Button variant="destructive">
              <Trash2Icon class="mr-2 h-4 w-4" />
              Delete account
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Delete this account?</DialogTitle>
              <DialogDescription>
                Your data and tokens will be removed immediately. There is no undo.
              </DialogDescription>
            </DialogHeader>
            <p v-if="deleteError" class="text-sm text-destructive" role="alert">
              {{ deleteError }}
            </p>
            <DialogFooter>
              <Button variant="destructive" :disabled="deleting" @click="onDelete">
                {{ deleting ? "Deleting…" : "Yes, delete it" }}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </CardFooter>
    </Card>
  </section>
</template>
