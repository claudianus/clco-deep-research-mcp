<template>
  <section class="surface-0 py-16 md:py-24">
    <UContainer>
      <div class="text-center mb-10">
        <SectionTitle size="xl">{{ title }}</SectionTitle>
        <p class="mt-3 text-gray-400 max-w-2xl mx-auto">7-phase pipeline from query expansion to citation-native synthesis. No generative LLMs in the server.</p>
      </div>

      <div class="mb-10">
        <div class="flex flex-wrap justify-center gap-2 mb-6">
          <UButton v-for="(phase, i) in phases" :key="phase.label" :variant="activePhase === i ? 'solid' : 'ghost'" :color="activePhase === i ? 'violet' : 'gray'" size="sm" @click="activePhase = i">{{ phase.label }}</UButton>
        </div>
        <div class="grid md:grid-cols-3 gap-4">
          <div v-for="step in phaseSteps[activePhase]" :key="step.title" class="surface-200 rounded-xl p-4 border border-white/[0.06] hover:border-violet-500/30 transition-colors">
            <div class="flex items-center gap-2 mb-2">
              <SafeIcon :name="step.icon" class="text-violet-400" />
              <span class="text-sm font-semibold text-white">{{ step.title }}</span>
            </div>
            <p class="text-xs text-gray-400 leading-relaxed">{{ step.desc }}</p>
          </div>
        </div>
      </div>

      <div class="surface-200 rounded-2xl border border-white/[0.06] overflow-hidden">
        <div class="px-4 py-3 border-b border-white/[0.06] flex items-center gap-2">
          <div class="terminal-dot bg-red-400/80" />
          <div class="terminal-dot bg-yellow-400/80" />
          <div class="terminal-dot bg-green-400/80" />
          <span class="ml-2 text-xs text-gray-500 font-mono">architecture.md</span>
        </div>
        <div class="p-4 md:p-6 overflow-x-auto">
          <pre class="font-mono text-xs md:text-sm leading-relaxed text-gray-300 whitespace-pre">
┌─────────────────────────────────────────────────────────────────┐
│ MCP Client Layer                                                │
│ (Claude Code, Cursor, Kimi, Windsurf)                           │
└────────────────────┬────────────────────────────────────────────┘
                     │ JSON-RPC 2.0 / stdio
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    maru-deep-pro-search                         │
│  ┌──────────────┐  ┌────────┐  ┌─────────────────────────────┐  │
│  │ 4 Prompts    │  │ 8 Tools│  │ TOOL_GUIDANCE               │  │
│  │ (research-   │  │        │  │ (context-level rules)       │  │
│  │  first, ...) │  └────────┘  └─────────────────────────────┘  │
│  └──────────────┘                                               │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  ┌──────────────┐     ┌──────────┐     ┌─────────────────────┐ │
│  │ Query        │────▶│ 7 Engines│────▶│ Result Merge &      │ │
│  │ Expander     │     │ (async)  │     │ Fuzzy Deduplication │ │
│  │ (templates   │     │ Registry │     │ (Jaccard + semantic)│ │
│  │ + synonyms)  │     │ pattern  │     └─────────────────────┘ │
│  └──────────────┘     └──────────┘                             │
│                     ┌──────────────────────────────────────┐   │
│                     │ Hybrid Ranking: BM25×0.35 + auth×0.20 +│   │
│                     │ freshness×0.15 + code×0.10 +           │   │
│                     │ semantic(cos_sim)×0.20 [multilingual]  │   │
│                     └──────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Smart Fetch: probe → domain filter → priority queue →    │  │
│  │ error-aware strategy → session reuse → early abort       │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Content: trafilatura → htmldate → code.py → sanitize.py  │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Synthesis: rule-based + [1] [2] [3] citations + gap detect│  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
          </pre>
        </div>
      </div>

      <p class="text-center text-sm text-gray-500 mt-6">{{ footer }}</p>
    </UContainer>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import SectionTitle from '~/components/ui/SectionTitle.vue'

defineProps<{ title: string; footer: string }>()
const activePhase = ref(0)
const phases = [{ label: 'Query & Search' }, { label: 'Rank & Fetch' }, { label: 'Extract & Synthesize' }]
const phaseSteps = [
  [
    { icon: 'i-lucide-search', title: 'Query Expansion', desc: 'Template-based expansion with synonym injection and keyword clustering for broader coverage.' },
    { icon: 'i-lucide-globe', title: '7-Engine Search', desc: 'Parallel async search across DuckDuckGo, SearXNG, Bing, Google, Naver, Qwant, Startpage.' },
    { icon: 'i-lucide-git-merge', title: 'Result Merge', desc: 'Cross-engine deduplication using Jaccard similarity + semantic vector comparison.' },
  ],
  [
    { icon: 'i-lucide-bar-chart-3', title: 'Hybrid Ranking', desc: 'BM25 × 0.35 + authority × 0.20 + freshness × 0.15 + code_density × 0.10 + semantic × 0.20' },
    { icon: 'i-lucide-shield', title: 'Smart Fetch', desc: 'Error-type-aware handling: DNS→skip, SSL→stealth, 403→stealth. Domain history blacklist.' },
    { icon: 'i-lucide-zap', title: 'Early Abort', desc: 'Stop at 3 HIGH-quality results. Session reuse per engine. Asyncio concurrency.' },
  ],
  [
    { icon: 'i-lucide-file-text', title: 'Content Extraction', desc: 'trafilatura → htmldate → code.py → sanitize.py. 21-language code detection.' },
    { icon: 'i-lucide-link', title: 'Citation-Native', desc: 'Every claim backed by [1], [2] citations with real URLs. Gap detection for missing coverage.' },
    { icon: 'i-lucide-cpu', title: 'Zero LLM Server', desc: 'Synthesis is rule-based. Your agent\'s LLM handles reasoning. Server has no generative model.' },
  ],
]
</script>
