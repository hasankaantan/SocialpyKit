import { defineStore } from "pinia"

import { authApi } from "../api"
import type { components } from "../api/schema"

type UserResponse = components["schemas"]["UserResponse"]

const TOKEN_KEY = "socialpykit_token"

interface AuthState {
  token: string | null
  user: UserResponse | null
}

export const useAuthStore = defineStore("auth", {
  state: (): AuthState => ({
    token: localStorage.getItem(TOKEN_KEY),
    user: null,
  }),

  getters: {
    isAuthenticated: (state): boolean => state.token !== null,
  },

  actions: {
    /**
     * Exchange email + password for a bearer token, persist it, then
     * load the current user behind it.
     */
    async login(email: string, password: string): Promise<void> {
      const response = await authApi.login(email, password)
      this.token = response.access_token
      localStorage.setItem(TOKEN_KEY, response.access_token)
      await this.fetchMe()
    },

    /**
     * Create a new account and immediately log in with it.
     */
    async register(email: string, password: string): Promise<void> {
      await authApi.register({ email, password })
      await this.login(email, password)
    },

    /**
     * Refresh the cached user. No-op when no token is present.
     */
    async fetchMe(): Promise<void> {
      if (this.token === null) return
      this.user = await authApi.me()
    },

    /**
     * Drop the bearer token from memory and localStorage. The next page
     * load will boot in the unauthenticated state.
     */
    logout(): void {
      this.token = null
      this.user = null
      localStorage.removeItem(TOKEN_KEY)
    },
  },
})

export { TOKEN_KEY }
