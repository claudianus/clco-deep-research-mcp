<template>
  <section class="border-t border-gray-800/60 py-16">
    <UContainer>
      <SectionTitle>{{ title }}</SectionTitle>
      <div class="grid gap-3 sm:grid-cols-2">
        <div
          v-for="tool in tools"
          :key="tool.name"
          class="flex items-center gap-3 rounded-lg border border-gray-800 bg-gray-900/40 px-4 py-3"
        >
          <code class="rounded bg-gray-800 px-2 py-0.5 text-sm text-indigo-300 whitespace-nowrap">{{ tool.name }}</code>
          <span class="text-sm text-gray-300">{{ tool.description }}</span>
        </div>
      </div>
    </UContainer>
  </section>
</template>

<script setup lang="ts">
import type { Tool } from '~/types';

defineProps<{
  title: string;
  tools: Tool[];
}>();
</script>
