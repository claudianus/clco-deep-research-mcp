<template>
  <div
    v-if="value === $t('comparison.yes')"
    class="inline-flex items-center justify-center rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-bold text-emerald-400 ring-1 ring-emerald-500/20"
  >
    {{ value }}
  </div>
  <div
    v-else-if="value === $t('comparison.no')"
    class="inline-flex items-center justify-center rounded-full bg-red-500/10 px-3 py-1 text-xs font-bold text-red-400 ring-1 ring-red-500/20"
  >
    {{ value }}
  </div>
  <div
    v-else
    class="inline-flex items-center justify-center rounded-full bg-amber-500/10 px-3 py-1 text-xs font-bold text-amber-400 ring-1 ring-amber-500/20"
  >
    {{ value }}
  </div>
</template>

<script setup>
defineProps({ value: String })
const { t } = useI18n()
</script>
