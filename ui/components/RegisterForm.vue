<script setup lang="ts">
import { toTypedSchema } from "@vee-validate/zod"
import { useForm } from "vee-validate"
import { ref } from "vue"
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
import { explainApiError } from "@/lib/api-error"
import { useAuthStore } from "@/stores/auth"

const PASSWORD_MIN_LENGTH = 8
const PASSWORD_MAX_LENGTH = 72

interface RegisterValues {
  email: string
  password: string
}

const store = useAuthStore()
const error = ref<string | null>(null)

const schema = toTypedSchema(
  z.object({
    email: z.string().email("Enter a valid email"),
    password: z
      .string()
      .min(PASSWORD_MIN_LENGTH, `At least ${PASSWORD_MIN_LENGTH} characters`)
      .max(PASSWORD_MAX_LENGTH, `At most ${PASSWORD_MAX_LENGTH} bytes`),
  }),
)

const form = useForm<RegisterValues>({
  validationSchema: schema,
  initialValues: { email: "", password: "" },
})

const onSubmit = form.handleSubmit(async (values) => {
  error.value = null
  try {
    await store.register(values.email, values.password)
    await navigateTo("/dashboard")
  } catch (err) {
    error.value = explainApiError(err, "Registration failed")
  }
})
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>Create an account</CardTitle>
      <CardDescription>Sign up to get started.</CardDescription>
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
                autocomplete="new-password"
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
          {{ form.isSubmitting.value ? "Creating account…" : "Create account" }}
        </Button>
      </form>
    </CardContent>
  </Card>
</template>
