<template>
  <section class="surface-0 py-16 md:py-24">
    <UContainer>
      <div class="text-center mb-10">
        <SectionTitle size="xl">{{ title }}</SectionTitle>
        <p class="mt-3 text-gray-400">Production-ready performance targets. CPU-only. No GPU required.</p>
      </div>

      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
        <div v-for="stat in quickStats" :key="stat.label" class="surface-200 rounded-xl p-4 border border-white/[0.06] text-center">
          <div class="text-2xl font-bold text-emerald-400 mb-1">{{ stat.value }}</div>
          <div class="text-xs text-gray-500">{{ stat.label }}</div>
        </div>
      </div>

      <DarkTable :columns="columns" :rows="metrics">
        <template #target="{ value }">
          <span class="text-emerald-400 font-mono text-xs">{{ value }}</span>
        </template>
        <template #metric="{ value }">
          <span class="text-white font-medium">{{ value }}</span>
        </template>
      </DarkTable>
    </UContainer>
  </section>
</template>

<script setup lang="ts">
import type { PerformanceMetric } from '~/types'
import SectionTitle from '~/components/ui/SectionTitle.vue'
import DarkTable from '~/components/ui/DarkTable.vue'

const columns = [
  { key: 'metric', label: 'Metric' },
  { key: 'target', label: 'Target' },
  { key: 'implementation', label: 'Implementation' },
]

const quickStats = [
  { value: '<100ms', label: 'Cache Hit' },
  { value: '<10s', label: 'Deep Research' },
  { value: '~0ms', label: 'Session Startup' },
  { value: '~150MB', label: 'Base Memory' },
]

defineProps<{ title: string; metrics: PerformanceMetric[] }>()
</script>
