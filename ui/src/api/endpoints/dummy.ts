import { http } from "../client"
import type { paths } from "../schema"

type DummyList = paths["/api/dummy/"]["get"]["responses"]["200"]["content"]["application/json"]
type DummyCreatePayload = paths["/api/dummy/"]["put"]["requestBody"]["content"]["application/json"]
type DummyCreateResponse = paths["/api/dummy/"]["put"]["responses"]["200"]["content"]["application/json"]

export const dummyApi = {
  async list(params?: { limit?: number; offset?: number }): Promise<DummyList> {
    const { data } = await http.get<DummyList>("/api/dummy/", { params })
    return data
  },
  async create(payload: DummyCreatePayload): Promise<DummyCreateResponse> {
    const { data } = await http.put<DummyCreateResponse>("/api/dummy/", payload)
    return data
  },
} as const
