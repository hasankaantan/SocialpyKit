import { http } from "../client"
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
    const { data } = await http.post<RegisterResponse>("/api/auth/register", payload)
    return data
  },

  /**
   * Exchange email + password for a bearer token via the oauth2
   * password-grant form body.
   */
  async login(email: string, password: string): Promise<TokenResponse> {
    const form = new URLSearchParams()
    form.append("username", email)
    form.append("password", password)
    const { data } = await http.post<TokenResponse>("/api/auth/login", form, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    })
    return data
  },

  /**
   * Fetch the user behind ``token``. Caller is responsible for storing the
   * token (auth store or composable).
   */
  async me(token: string): Promise<UserResponse> {
    const { data } = await http.get<UserResponse>("/api/auth/me", {
      headers: { Authorization: `Bearer ${token}` },
    })
    return data
  },
} as const
