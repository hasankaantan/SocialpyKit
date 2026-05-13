import { http } from "../client"
import type { paths } from "../schema"

type UserList =
  paths["/api/users/"]["get"]["responses"]["200"]["content"]["application/json"]
type UpdateSelfPayload =
  paths["/api/users/me"]["patch"]["requestBody"]["content"]["application/json"]
type UpdateSelfResponse =
  paths["/api/users/me"]["patch"]["responses"]["200"]["content"]["application/json"]
type AdminUpdatePayload =
  paths["/api/users/{user_id}"]["patch"]["requestBody"]["content"]["application/json"]
type AdminUpdateResponse =
  paths["/api/users/{user_id}"]["patch"]["responses"]["200"]["content"]["application/json"]

export const usersApi = {
  /** GET /api/users — admin only. */
  async list(): Promise<UserList> {
    const { data } = await http.get<UserList>("/api/users/")
    return data
  },

  /** PATCH /api/users/me — caller updates their own profile. */
  async updateSelf(payload: UpdateSelfPayload): Promise<UpdateSelfResponse> {
    const { data } = await http.patch<UpdateSelfResponse>("/api/users/me", payload)
    return data
  },

  /** DELETE /api/users/me — caller deletes their own account. */
  async deleteSelf(): Promise<void> {
    await http.delete("/api/users/me")
  },

  /** PATCH /api/users/{user_id} — admin only. */
  async updateAsAdmin(
    userId: number,
    payload: AdminUpdatePayload,
  ): Promise<AdminUpdateResponse> {
    const { data } = await http.patch<AdminUpdateResponse>(
      `/api/users/${userId}`,
      payload,
    )
    return data
  },

  /** DELETE /api/users/{user_id} — admin only. */
  async deleteAsAdmin(userId: number): Promise<void> {
    await http.delete(`/api/users/${userId}`)
  },
} as const
