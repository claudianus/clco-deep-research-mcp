<template>
  <section class="surface-100 py-16 md:py-24">
    <UContainer>
      <div class="text-center mb-10">
        <SectionTitle size="xl">{{ title }}</SectionTitle>
        <p class="mt-3 text-gray-400">What changes when your agent researches before it codes.</p>
      </div>

      <div class="grid lg:grid-cols-2 gap-6">
        <div class="surface-200 rounded-2xl border border-red-500/10 p-6">
          <div class="flex items-center gap-2 mb-5">
            <div class="w-8 h-8 rounded-lg bg-red-500/10 flex items-center justify-center"><span class="text-red-400">❌</span></div>
            <h3 class="text-lg font-semibold text-red-300">Before</h3>
          </div>
          <div class="space-y-3">
            <div v-for="row in rows" :key="row.before" class="flex items-start gap-3 p-3 rounded-lg bg-white/[0.02]">
              <span class="text-red-400/60 mt-0.5 flex-shrink-0">−</span>
              <span class="text-sm text-gray-400">{{ row.before }}</span>
            </div>
          </div>
        </div>

        <div class="surface-200 rounded-2xl border border-emerald-500/10 p-6">
          <div class="flex items-center gap-2 mb-5">
            <div class="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center"><span class="text-emerald-400">✓</span></div>
            <h3 class="text-lg font-semibold text-emerald-300">After</h3>
          </div>
          <div class="space-y-3">
            <div v-for="row in rows" :key="row.after" class="flex items-start gap-3 p-3 rounded-lg bg-white/[0.02]">
              <span class="text-emerald-400 mt-0.5 flex-shrink-0">✓</span>
              <span class="text-sm text-gray-300">{{ row.after }}</span>
            </div>
          </div>
        </div>
      </div>
    </UContainer>
  </section>
</template>

<script setup lang="ts">
import type { BeforeAfterRow } from '~/types'
import SectionTitle from '~/components/ui/SectionTitle.vue'

defineProps<{ title: string; rows: BeforeAfterRow[] }>()
</script>
