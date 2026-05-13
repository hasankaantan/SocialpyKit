<script setup lang="ts">
import { toTypedSchema } from "@vee-validate/zod"
import axios from "axios"
import { useForm } from "vee-validate"
import { ref } from "vue"
import { useRoute, useRouter } from "vue-router"
import { z } from "zod"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { useAuthStore } from "@/stores/auth"

const router = useRouter()
const route = useRoute()
const store = useAuthStore()
const error = ref<string | null>(null)

interface LoginValues {
  email: string
  password: string
}

const schema = toTypedSchema(
  z.object({
    email: z.string().email("Enter a valid email"),
    password: z.string().min(1, "Password is required"),
  }),
)

const form = useForm<LoginValues>({
  validationSchema: schema,
  initialValues: { email: "", password: "" },
})

const onSubmit = form.handleSubmit(async (values) => {
  error.value = null
  try {
    await store.login(values.email, values.password)
    const redirect =
      typeof route.query.redirect === "string" ? route.query.redirect : "/dashboard"
    await router.push(redirect)
  } catch (err) {
    error.value = explain(err)
  }
})

function explain(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const detail = (err.response?.data as { detail?: string } | undefined)?.detail
    if (typeof detail === "string") return detail
  }
  if (err instanceof Error) return err.message
  return "Login failed"
}
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>Sign in</CardTitle>
      <CardDescription>Welcome back to SocialpyKit.</CardDescription>
    </CardHeader>
    <CardContent>
      <form class="space-y-4" @submit="onSubmit">
        <FormField v-slot="{ componentField }" name="email">
          <FormItem>
            <FormLabel>Email</FormLabel>
            <FormControl>
              <Input type="email" autocomplete="email" v-bind="componentField" />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>

        <FormField v-slot="{ componentField }" name="password">
          <FormItem>
            <FormLabel>Password</FormLabel>
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

        <p v-if="error" class="text-sm text-destructive" role="alert">
          {{ error }}
        </p>

        <Button type="submit" class="w-full" :disabled="form.isSubmitting.value">
          {{ form.isSubmitting.value ? "Signing in…" : "Sign in" }}
        </Button>
      </form>
    </CardContent>
  </Card>
</template>
