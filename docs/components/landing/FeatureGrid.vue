<template>
  <section class="surface-0 py-16 md:py-24">
    <UContainer>
      <div class="text-center mb-12">
        <SectionTitle size="xl">{{ title }}</SectionTitle>
        <p class="mt-3 text-gray-400 max-w-xl mx-auto">Zero API keys. Direct scraping. Citation-native answers across 7 search engines.</p>
      </div>

      <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="(feature, i) in features"
          :key="i"
          class="group surface-200 rounded-2xl p-5 md:p-6 border border-white/[0.06] hover-lift transition-colors"
          :class="feature.wide ? 'md:col-span-2 lg:col-span-1' : ''"
        >
          <div class="flex items-start gap-4">
            <div class="flex-shrink-0 w-10 h-10 rounded-xl bg-violet-500/10 border border-violet-500/20 flex items-center justify-center text-lg">
              {{ feature.icon }}
            </div>
            <div class="min-w-0">
              <h3 class="text-base font-semibold text-white mb-1.5 group-hover:text-violet-300 transition-colors">{{ feature.title }}</h3>
              <p class="text-sm text-gray-400 leading-relaxed">{{ feature.description }}</p>
              <div v-if="feature.tags" class="flex flex-wrap gap-1.5 mt-3">
                <span v-for="tag in feature.tags" :key="tag" class="text-[11px] px-2 py-0.5 rounded-full bg-white/[0.04] text-gray-500 border border-white/[0.06]">{{ tag }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </UContainer>
  </section>
</template>

<script setup lang="ts">
import SectionTitle from '~/components/ui/SectionTitle.vue'

defineProps<{
  title: string
  features: Array<{
    icon: string
    title: string
    description: string
    wide?: boolean
    tags?: string[]
  }>
}>()
</script>
