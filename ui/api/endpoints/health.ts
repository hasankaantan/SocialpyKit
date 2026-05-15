import { useApi } from "~/composables/useApi"

export const healthApi = {
  async check(): Promise<void> {
    await useApi()("/api/health")
  },
} as const
