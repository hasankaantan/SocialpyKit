import { useAuthStore } from "~/stores/auth"

export default defineNuxtRouteMiddleware(async (to) => {
  const store = useAuthStore()

  // Hydrate the cached user once if a token is present but the store
  // has not seen the backend yet (typical for a hard refresh).
  if (store.isAuthenticated && store.user === null) {
    try {
      await store.fetchMe()
    } catch {
      store.logout()
    }
  }

  // Public-only routes (login/register) bounce signed-in users away.
  if (to.meta.publicOnly === true && store.isAuthenticated) {
    return navigateTo("/dashboard")
  }
})
