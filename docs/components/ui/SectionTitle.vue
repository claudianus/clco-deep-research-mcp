<template>
  <div class="mb-8 text-center">
    <h2 class="text-2xl font-bold" :class="gradient ? 'bg-gradient-to-r from-indigo-400 via-violet-400 to-fuchsia-400 bg-clip-text text-transparent' : 'text-gray-100'">
      <slot />
    </h2>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  gradient?: boolean;
}>(), {
  gradient: false,
});
</script>
