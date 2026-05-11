<template>
  <section class="border-t border-gray-800/60 py-16">
    <UContainer>
      <SectionTitle>{{ title }}</SectionTitle>
      <div class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <UCard
          v-for="feature in features"
          :key="feature.title"
          :ui="{ base: 'border border-gray-800 bg-gray-900/40', body: { base: 'p-5' } }"
        >
          <div class="mb-2 text-2xl">{{ feature.icon }}</div>
          <h3 class="mb-1 font-semibold text-gray-100">{{ feature.title }}</h3>
          <p class="text-sm text-gray-400">{{ feature.description }}</p>
        </UCard>
      </div>
    </UContainer>
  </section>
</template>

<script setup lang="ts">
import type { Feature } from '~/types';

defineProps<{
  title: string;
  features: Feature[];
}>();
</script>
