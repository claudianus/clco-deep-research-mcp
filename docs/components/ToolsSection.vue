<template>
  <section id="tools" class="border-t border-gray-800/60 py-20">
    <UContainer>
      <div class="mb-12 text-center">
        <UBadge color="violet" variant="subtle" size="lg" class="mb-4">Toolbox</UBadge>
        <h2 class="text-3xl font-bold tracking-tight sm:text-4xl">{{ $t('tools.title') }}</h2>
        <p class="mt-2 text-gray-400">{{ $t('tools.desc') }}</p>
      </div>

      <div class="mx-auto max-w-4xl space-y-4">
        <div
          v-for="(tool, i) in tools"
          :key="i"
          class="group rounded-xl border border-gray-800 bg-gray-950 transition-all hover:border-indigo-500/30"
        >
          <div class="flex items-start gap-4 p-5">
            <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-gray-900 text-xs font-bold text-indigo-400 ring-1 ring-gray-800">
              {{ i + 1 }}
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-3 mb-1">
                <h3 class="font-mono text-sm font-semibold text-indigo-300">{{ tool.name }}</h3>
                <span
                  v-if="tool.badge"
                  class="rounded bg-indigo-500/10 px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wider text-indigo-400"
                >{{ tool.badge }}</span>
              </div>
              <p class="text-sm text-gray-400">{{ tool.desc }}</p>
            </div>
          </div>
        </div>
      </div>
    </UContainer>
  </section>
</template>

<script setup>
const { t } = useI18n()
const tools = computed(() => [
  { name: 'answer', desc: t('tools.answer'), badge: 'Core' },
  { name: 'web_search', desc: t('tools.web_search'), badge: '' },
  { name: 'search_with_citations', desc: t('tools.search_with_citations'), badge: 'Academic' },
  { name: 'fetch_page', desc: t('tools.fetch_page'), badge: '' },
  { name: 'fetch_bulk', desc: t('tools.fetch_bulk'), badge: '' },
  { name: 'deep_research', desc: t('tools.deep_research'), badge: 'Premium' },
  { name: 'stealthy_fetch', desc: t('tools.stealthy_fetch'), badge: 'Anti-Bot' },
  { name: 'parallel_search', desc: t('tools.parallel_search'), badge: '' },
])
</script>
