<template>
  <section class="border-t border-gray-800/60 py-20">
    <UContainer>
      <div class="mb-4 text-center">
        <UBadge color="indigo" variant="subtle" size="lg" class="mb-4">Dominance</UBadge>
        <h2 class="text-3xl font-bold tracking-tight sm:text-4xl">{{ $t('comparison.title') }}</h2>
        <p class="mt-3 text-gray-400">{{ $t('comparison.subtitle') }}</p>
      </div>

      <div class="mt-12 overflow-hidden rounded-2xl border border-gray-800">
        <div class="overflow-x-auto">
          <table class="w-full text-left text-sm">
            <thead>
              <tr class="border-b border-gray-800 bg-gray-900/60">
                <th class="px-6 py-4 font-semibold text-gray-300">{{ $t('comparison.feature') }}</th>
                <th class="px-6 py-4 text-center font-bold text-indigo-400">{{ $t('comparison.us') }}</th>
                <th class="px-6 py-4 text-center font-semibold text-gray-500">{{ $t('comparison.brave') }}</th>
                <th class="px-6 py-4 text-center font-semibold text-gray-500">{{ $t('comparison.perplexity') }}</th>
                <th class="px-6 py-4 text-center font-semibold text-gray-500">{{ $t('comparison.others') }}</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-800/60">
              <tr v-for="(row, i) in rows" :key="i" class="transition-colors hover:bg-gray-900/30">
                <td class="px-6 py-4 font-medium text-gray-200">{{ row.feature }}</td>
                <td class="px-6 py-4 text-center">
                  <div class="inline-flex items-center justify-center rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-bold text-emerald-400 ring-1 ring-emerald-500/20">
                    {{ row.us }}
                  </div>
                </td>
                <td class="px-6 py-4 text-center">
                  <CellBadge :value="row.brave" />
                </td>
                <td class="px-6 py-4 text-center">
                  <CellBadge :value="row.perplexity" />
                </td>
                <td class="px-6 py-4 text-center">
                  <CellBadge :value="row.others" />
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </UContainer>
  </section>
</template>

<script setup>
const { t } = useI18n()
const rows = computed(() => [
  { feature: t('comparison.noApiKeys'), us: t('comparison.yes'), brave: t('comparison.no'), perplexity: t('comparison.paid'), others: t('comparison.partial') },
  { feature: t('comparison.deepResearch'), us: t('comparison.yes'), brave: t('comparison.no'), perplexity: t('comparison.yes'), others: t('comparison.no') },
  { feature: t('comparison.citations'), us: t('comparison.yes'), brave: t('comparison.no'), perplexity: t('comparison.yes'), others: t('comparison.no') },
  { feature: t('comparison.bm25'), us: t('comparison.yes'), brave: t('comparison.no'), perplexity: t('comparison.no'), others: t('comparison.no') },
  { feature: t('comparison.codeAware'), us: t('comparison.yes'), brave: t('comparison.no'), perplexity: t('comparison.partial'), others: t('comparison.no') },
  { feature: t('comparison.antiBot'), us: t('comparison.yes'), brave: t('comparison.no'), perplexity: t('comparison.no'), others: t('comparison.partial') },
  { feature: t('comparison.korean'), us: t('comparison.yes'), brave: t('comparison.no'), perplexity: t('comparison.partial'), others: t('comparison.no') },
  { feature: t('comparison.multiEngine'), us: t('comparison.yes'), brave: t('comparison.no'), perplexity: t('comparison.no'), others: t('comparison.partial') },
  { feature: t('comparison.tokenMgmt'), us: t('comparison.yes'), brave: t('comparison.no'), perplexity: t('comparison.no'), others: t('comparison.no') },
  { feature: t('comparison.freshness'), us: t('comparison.yes'), brave: t('comparison.no'), perplexity: t('comparison.partial'), others: t('comparison.no') },
])
</script>
