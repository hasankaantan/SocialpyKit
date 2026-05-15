import { http } from "../client"

export const healthApi = {
  async check(): Promise<void> {
    await http.get("/api/health")
  },
} as const
