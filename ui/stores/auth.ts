import { defineStore } from "pinia"

import { authApi } from "~/api"
import type { components } from "~/api/schema"

type UserResponse = components["schemas"]["UserResponse"]

const TOKEN_COOKIE = "socialpykit_token"

interface AuthState {
  user: UserResponse | null
}

export const useAuthStore = defineStore("auth", {
  state: (): AuthState => ({
    user: null,
  }),

  getters: {
    token(): string | null {
      return useCookie<string | null>(TOKEN_COOKIE).value
    },
    isAuthenticated(): boolean {
      return this.token !== null
    },
  },

  actions: {
    async login(email: string, password: string): Promise<void> {
      const response = await authApi.login(email, password)
      useCookie<string | null>(TOKEN_COOKIE, {
        maxAge: 60 * 60 * 24 * 30,
        sameSite: "lax",
        secure: !import.meta.dev,
        path: "/",
      }).value = response.access_token
      await this.fetchMe()
    },

    async register(email: string, password: string): Promise<void> {
      await authApi.register({ email, password })
      await this.login(email, password)
    },

    async fetchMe(): Promise<void> {
      if (this.token === null) return
      this.user = await authApi.me()
    },

    logout(): void {
      this.user = null
      useCookie<string | null>(TOKEN_COOKIE).value = null
    },
  },
})

export { TOKEN_COOKIE }
