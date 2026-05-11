<template>
  <section class="relative overflow-hidden pb-20 pt-16">
    <div class="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-900/20 via-[#0a0a0f] to-[#0a0a0f]" />
    <UContainer class="relative text-center">
      <UBadge color="indigo" variant="soft" class="mb-4">
        MCP Server · v0.9.0
      </UBadge>
      <h1 class="mb-4 text-4xl font-extrabold tracking-tight sm:text-6xl">
        <GradientText>Force your AI agent<br>to research first.</GradientText>
      </h1>
      <p class="mb-8 text-lg text-gray-400">
        {{ tagline }}
      </p>
      <slot />
    </UContainer>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  tagline: string;
}>();
</script>
