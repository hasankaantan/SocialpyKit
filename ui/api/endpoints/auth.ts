import { useApi } from "~/composables/useApi"

import type { paths } from "../schema"

type RegisterPayload =
  paths["/api/auth/register"]["post"]["requestBody"]["content"]["application/json"]
type RegisterResponse =
  paths["/api/auth/register"]["post"]["responses"]["201"]["content"]["application/json"]
type TokenResponse =
  paths["/api/auth/login"]["post"]["responses"]["200"]["content"]["application/json"]
type UserResponse =
  paths["/api/auth/me"]["get"]["responses"]["200"]["content"]["application/json"]

export const authApi = {
  async register(payload: RegisterPayload): Promise<RegisterResponse> {
    return useApi()<RegisterResponse>("/api/auth/register", {
      method: "POST",
      body: payload,
    })
  },

  /**
   * Exchange email + password for a bearer token via the oauth2
   * password-grant form body.
   */
  async login(email: string, password: string): Promise<TokenResponse> {
    const form = new URLSearchParams()
    form.append("username", email)
    form.append("password", password)
    return useApi()<TokenResponse>("/api/auth/login", {
      method: "POST",
      body: form,
    })
  },

  /**
   * Fetch the user behind the current bearer token. The token is picked
   * up automatically by the onRequest hook in plugins/api.ts, so callers
   * do not pass it explicitly.
   */
  async me(): Promise<UserResponse> {
    return useApi()<UserResponse>("/api/auth/me")
  },
} as const
