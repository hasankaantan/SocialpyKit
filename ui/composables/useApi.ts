import type { $Fetch } from "ofetch"

/**
 * Thin accessor over the $api instance provided by plugins/api.ts.
 * Keeps endpoint files framework-agnostic (no useNuxtApp leak).
 */
export function useApi(): $Fetch {
  return useNuxtApp().$api as $Fetch
}
