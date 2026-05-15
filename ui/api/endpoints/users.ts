import { useApi } from "~/composables/useApi"

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
    return useApi()<UserList>("/api/users/")
  },

  /** PATCH /api/users/me — caller updates their own profile. */
  async updateSelf(payload: UpdateSelfPayload): Promise<UpdateSelfResponse> {
    return useApi()<UpdateSelfResponse>("/api/users/me", {
      method: "PATCH",
      body: payload,
    })
  },

  /** DELETE /api/users/me — caller deletes their own account. */
  async deleteSelf(): Promise<void> {
    await useApi()("/api/users/me", { method: "DELETE" })
  },

  /** PATCH /api/users/{user_id} — admin only. */
  async updateAsAdmin(
    userId: number,
    payload: AdminUpdatePayload,
  ): Promise<AdminUpdateResponse> {
    return useApi()<AdminUpdateResponse>(`/api/users/${userId}`, {
      method: "PATCH",
      body: payload,
    })
  },

  /** DELETE /api/users/{user_id} — admin only. */
  async deleteAsAdmin(userId: number): Promise<void> {
    await useApi()(`/api/users/${userId}`, { method: "DELETE" })
  },
} as const
