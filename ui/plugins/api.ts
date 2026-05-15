import { TOKEN_COOKIE } from "~/stores/auth"

/**
 * Provides a typed `$api` instance — Nuxt's built-in `$fetch` pre-baked
 * with the API base URL and a bearer-token attaching `onRequest` hook.
 *
 * Replaces the old axios client + interceptor in api/client.ts.
 */
export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()

  const api = $fetch.create({
    baseURL: config.public.apiBase,
    timeout: 10_000,
    onRequest({ options }) {
      const token = useCookie<string | null>(TOKEN_COOKIE).value
      if (token !== null) {
        const headers = new Headers(options.headers)
        headers.set("Authorization", `Bearer ${token}`)
        options.headers = headers
      }
    },
  })

  return {
    provide: { api },
  }
})
