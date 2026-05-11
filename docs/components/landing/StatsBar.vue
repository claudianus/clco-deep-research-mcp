<template>
  <section class="surface-50 border-y border-white/[0.04]">
    <UContainer class="py-8 md:py-10">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-6 md:gap-8">
        <div v-for="stat in stats" :key="stat.label" class="text-center">
          <div class="text-2xl md:text-3xl font-bold text-white mb-1">{{ stat.value }}</div>
          <div class="text-xs md:text-sm text-gray-500 font-medium uppercase tracking-wider">{{ stat.label }}</div>
        </div>
      </div>
    </UContainer>
  </section>
</template>

<script setup lang="ts">
const stats = [
  { value: '7', label: 'Search Engines' },
  { value: '8', label: 'MCP Tools' },
  { value: '193', label: 'Tests Passing' },
  { value: '$0', label: 'API Cost' },
]
</script>
