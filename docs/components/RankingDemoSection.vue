<template>
  <section class="border-t border-gray-800/60 py-20">
    <UContainer>
      <div class="mb-4 text-center">
        <UBadge color="fuchsia" variant="subtle" size="lg" class="mb-4">Intelligence</UBadge>
        <h2 class="text-3xl font-bold tracking-tight sm:text-4xl">{{ $t('ranking.title') }}</h2>
        <p class="mt-3 text-gray-400">{{ $t('ranking.subtitle') }}</p>
      </div>

      <div class="mt-12 grid gap-8 lg:grid-cols-2">
        <!-- Before -->
        <div class="rounded-2xl border border-gray-800 bg-gray-900/30 p-6">
          <h3 class="mb-4 text-center text-sm font-bold tracking-wider text-gray-500 uppercase">{{ $t('ranking.before') }}</h3>
          <div class="space-y-3">
            <div
              v-for="(item, i) in beforeItems"
              :key="i"
              class="flex items-center gap-3 rounded-lg border border-gray-800 bg-gray-950 p-3"
            >
              <span class="flex h-6 w-6 shrink-0 items-center justify-center rounded bg-gray-800 text-xs font-bold text-gray-500">{{ i + 1 }}</span>
              <span class="text-sm text-gray-300">{{ item.text }}</span>
              <span
                class="ml-auto shrink-0 rounded px-2 py-0.5 text-xs font-medium"
                :class="item.badgeClass"
              >{{ item.badge }}</span>
            </div>
          </div>
        </div>

        <!-- After -->
        <div class="relative rounded-2xl border border-indigo-500/20 bg-gray-900/30 p-6">
          <div class="absolute inset-0 rounded-2xl bg-gradient-to-br from-indigo-500/5 to-violet-500/5" />
          <h3 class="relative mb-4 text-center text-sm font-bold tracking-wider text-indigo-400 uppercase">{{ $t('ranking.after') }}</h3>
          <div class="relative space-y-3">
            <div
              v-for="(item, i) in afterItems"
              :key="i"
              class="flex items-center gap-3 rounded-lg border border-gray-800 bg-gray-950 p-3 transition-colors hover:border-indigo-500/20"
            >
              <span class="flex h-6 w-6 shrink-0 items-center justify-center rounded bg-indigo-500/10 text-xs font-bold text-indigo-400">{{ i + 1 }}</span>
              <span class="text-sm text-gray-300">{{ item.text }}</span>
              <span
                class="ml-auto shrink-0 rounded px-2 py-0.5 text-xs font-medium"
                :class="item.badgeClass"
              >{{ item.badge }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Why box -->
      <div class="mt-8 rounded-xl border border-gray-800 bg-gray-900/40 p-6">
        <div class="flex items-start gap-4">
          <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-indigo-500/10 text-indigo-400">
            <UIcon name="i-heroicons-light-bulb" class="h-5 w-5" />
          </div>
          <div>
            <h4 class="mb-1 font-semibold">{{ $t('ranking.why') }}</h4>
            <p class="text-sm leading-relaxed text-gray-400">{{ $t('ranking.whyDesc') }}</p>
          </div>
        </div>
      </div>
    </UContainer>
  </section>
</template>

<script setup>
const { t } = useI18n()
const badgeClasses = {
  seo: 'bg-red-500/10 text-red-400',
  official: 'bg-emerald-500/10 text-emerald-400',
  solved: 'bg-blue-500/10 text-blue-400',
  stale: 'bg-amber-500/10 text-amber-400',
  code: 'bg-violet-500/10 text-violet-400',
}

const beforeItems = computed(() => [
  { text: t('ranking.result1'), badge: t('ranking.badgeSeo'), badgeClass: badgeClasses.seo },
  { text: t('ranking.result4'), badge: t('ranking.badgeStale'), badgeClass: badgeClasses.stale },
  { text: t('ranking.result2'), badge: t('ranking.badgeOfficial'), badgeClass: badgeClasses.official },
  { text: t('ranking.result5'), badge: t('ranking.badgeCode'), badgeClass: badgeClasses.code },
  { text: t('ranking.result3'), badge: t('ranking.badgeSolved'), badgeClass: badgeClasses.solved },
])

const afterItems = computed(() => [
  { text: t('ranking.result3'), badge: t('ranking.badgeSolved'), badgeClass: badgeClasses.solved },
  { text: t('ranking.result2'), badge: t('ranking.badgeOfficial'), badgeClass: badgeClasses.official },
  { text: t('ranking.result5'), badge: t('ranking.badgeCode'), badgeClass: badgeClasses.code },
  { text: t('ranking.result4'), badge: t('ranking.badgeStale'), badgeClass: badgeClasses.stale },
  { text: t('ranking.result1'), badge: t('ranking.badgeSeo'), badgeClass: badgeClasses.seo },
])
</script>
