<script lang="ts" setup>
import type { ToasterProps } from "vue-sonner"

import {
  CircleCheckIcon,
  InfoIcon,
  Loader2Icon,
  OctagonXIcon,
  TriangleAlertIcon,
  XIcon,
} from "lucide-vue-next"
import { computed } from "vue"
import { Toaster as Sonner } from "vue-sonner"
import { cn } from "@/lib/utils"

const props = defineProps<ToasterProps>()

// Separate toastOptions so we can merge our defaults with caller overrides
// without producing a duplicate attribute on <Sonner>. Without this the
// template binds toast-options twice (once explicitly, once via v-bind)
// which vue-tsc flags as a strict type-check error.
const restProps = computed(() => {
  const { toastOptions: _toastOptions, ...rest } = props
  return rest
})
const mergedToastOptions = computed(() => ({
  classes: { toast: "rounded-2xl" },
  ...props.toastOptions,
}))
</script>

<template>
  <Sonner
    :class="cn('toaster group', props.class)"
    :style="{
      '--normal-bg': 'var(--popover)',
      '--normal-text': 'var(--popover-foreground)',
      '--normal-border': 'var(--border)',
      '--border-radius': 'var(--radius)',
    }"
    :toast-options="mergedToastOptions"
    v-bind="restProps"
  >
    <template #success-icon>
      <CircleCheckIcon class="size-4" />
    </template>
    <template #info-icon>
      <InfoIcon class="size-4" />
    </template>
    <template #warning-icon>
      <TriangleAlertIcon class="size-4" />
    </template>
    <template #error-icon>
      <OctagonXIcon class="size-4" />
    </template>
    <template #loading-icon>
      <div>
        <Loader2Icon class="size-4 animate-spin" />
      </div>
    </template>
    <template #close-icon>
      <XIcon class="size-4" />
    </template>
  </Sonner>
</template>
