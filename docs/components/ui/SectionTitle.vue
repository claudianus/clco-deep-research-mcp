<template>
  <h2
    :class="[
      'font-bold tracking-tight',
      sizeClass,
      gradient ? 'text-gradient-violet' : 'text-white',
    ]"
  >
    <slot />
  </h2>
</template>

<script setup lang="ts">
const props = withDefaults(defineProps<{
  size?: 'sm' | 'md' | 'lg' | 'xl' | '2xl'
  gradient?: boolean
}>(), {
  size: 'lg',
  gradient: true,
})

const sizeClass = computed(() => {
  const map: Record<string, string> = {
    sm: 'text-lg',
    md: 'text-xl',
    lg: 'text-2xl md:text-3xl',
    xl: 'text-3xl md:text-4xl',
    '2xl': 'text-4xl md:text-5xl lg:text-6xl',
  }
  return map[props.size]
})
</script>
