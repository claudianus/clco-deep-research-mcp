<template>
  <section class="surface-100 py-16 md:py-24">
    <UContainer>
      <div class="text-center mb-10">
        <SectionTitle size="xl">{{ title }}</SectionTitle>
        <p class="mt-3 text-gray-400">8 MCP tools exposed to your AI agent. All free. No API keys.</p>
      </div>

      <div class="mb-8 flex flex-wrap justify-center gap-2">
        <UButton v-for="(cat, i) in categories" :key="cat.label" :variant="activeCategory === i ? 'solid' : 'ghost'" :color="activeCategory === i ? 'violet' : 'gray'" size="sm" @click="activeCategory = i">{{ cat.label }}</UButton>
      </div>

      <div class="grid md:grid-cols-2 gap-4">
        <div v-for="tool in filteredTools" :key="tool.name" class="group surface-200 rounded-xl p-5 border border-white/[0.06] hover:border-violet-500/30 hover-lift">
          <div class="flex items-start justify-between mb-3">
            <div class="flex items-center gap-3">
              <div class="w-9 h-9 rounded-lg bg-violet-500/10 border border-violet-500/20 flex items-center justify-center">
                <SafeIcon :name="tool.icon" class="text-violet-400 text-sm" />
              </div>
              <div>
                <h3 class="text-sm font-semibold text-white font-mono">{{ tool.name }}</h3>
                <p class="text-xs text-gray-500">{{ tool.category }}</p>
              </div>
            </div>
            <UBadge v-if="tool.premium" color="violet" variant="subtle" size="xs" class="text-[10px]">Core</UBadge>
          </div>
          <p class="text-sm text-gray-400 leading-relaxed mb-3">{{ tool.desc }}</p>
          <div class="flex flex-wrap gap-1.5">
            <span v-for="tag in tool.tags" :key="tag" class="text-[10px] px-1.5 py-0.5 rounded bg-white/[0.04] text-gray-500 border border-white/[0.06]">{{ tag }}</span>
          </div>
        </div>
      </div>
    </UContainer>
  </section>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import SectionTitle from '~/components/ui/SectionTitle.vue'

defineProps<{ title: string }>()
const activeCategory = ref(0)
const categories = [{ label: 'All' }, { label: 'Search' }, { label: 'Fetch' }, { label: 'Advanced' }]
const tools = [
  { name: 'answer', category: 'Search', desc: 'Quick answer with inline citations from live web search.', icon: 'i-lucide-message-circle', premium: true, tags: ['citations', 'fast'] },
  { name: 'web_search', category: 'Search', desc: 'Scrape + rank + return cited results across 7 engines.', icon: 'i-lucide-search', premium: true, tags: ['7 engines', 'BM25'] },
  { name: 'search_with_citations', category: 'Search', desc: 'Pre-numbered sources for academic writing and research.', icon: 'i-lucide-book-open', premium: false, tags: ['academic', 'sources'] },
  { name: 'fetch_page', category: 'Fetch', desc: 'Extract clean content from a single URL with sanitization.', icon: 'i-lucide-file-text', premium: false, tags: ['clean', 'sanitize'] },
  { name: 'fetch_bulk', category: 'Fetch', desc: 'Parallel fetch with deduplication and priority queue.', icon: 'i-lucide-layers', premium: false, tags: ['parallel', 'dedup'] },
  { name: 'deep_research', category: 'Advanced', desc: '7-phase pipeline: expand → search → rank → crawl → synthesize.', icon: 'i-lucide-flask-conical', premium: true, tags: ['7-phase', '<10s'] },
  { name: 'stealthy_fetch', category: 'Advanced', desc: 'Anti-bot bypass for protected sites with error recovery.', icon: 'i-lucide-shield', premium: false, tags: ['anti-bot', 'stealth'] },
  { name: 'parallel_search', category: 'Advanced', desc: 'Run multiple searches simultaneously with cross-engine merge.', icon: 'i-lucide-git-branch', premium: false, tags: ['async', 'merge'] },
]
const filteredTools = computed(() => {
  if (activeCategory.value === 0) return tools
  return tools.filter(t => t.category === categories[activeCategory.value].label)
})
</script>
