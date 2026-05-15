import { useApi } from "~/composables/useApi"

import type { paths } from "../schema"

type DummyList =
  paths["/api/dummy/"]["get"]["responses"]["200"]["content"]["application/json"]
type DummyCreatePayload =
  paths["/api/dummy/"]["put"]["requestBody"]["content"]["application/json"]
type DummyCreateResponse =
  paths["/api/dummy/"]["put"]["responses"]["200"]["content"]["application/json"]

export const dummyApi = {
  async list(params?: { limit?: number; offset?: number }): Promise<DummyList> {
    return useApi()<DummyList>("/api/dummy/", { query: params })
  },
  async create(payload: DummyCreatePayload): Promise<DummyCreateResponse> {
    return useApi()<DummyCreateResponse>("/api/dummy/", {
      method: "PUT",
      body: payload,
    })
  },
} as const
