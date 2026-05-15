import { useAuthStore } from "~/stores/auth"

export default defineNuxtRouteMiddleware(() => {
  const store = useAuthStore()
  if (store.user?.role !== "admin") {
    return navigateTo("/dashboard")
  }
})
