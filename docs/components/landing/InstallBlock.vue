<template>
  <section id="install" class="surface-100 py-16 md:py-24">
    <UContainer>
      <div class="max-w-3xl mx-auto">
        <div class="text-center mb-10">
          <SectionTitle size="xl">{{ oneLiner }}</SectionTitle>
          <p class="mt-3 text-gray-400">One command. Auto-detection. Zero configuration.</p>
        </div>

        <div class="terminal-window">
          <div class="terminal-header">
            <div class="terminal-dot bg-red-400/80" />
            <div class="terminal-dot bg-yellow-400/80" />
            <div class="terminal-dot bg-green-400/80" />
            <div class="flex-1" />
            <div class="flex gap-1">
              <UButton v-for="(tab, i) in tabs" :key="tab.label" :variant="activeTab === i ? 'solid' : 'ghost'" :color="activeTab === i ? 'violet' : 'gray'" size="xs" @click="activeTab = i">{{ tab.label }}</UButton>
            </div>
          </div>
          <div class="terminal-body">
            <div v-if="activeTab === 0" class="space-y-1">
              <div><span class="prompt">$</span> <span class="command">curl -sSL https://raw.githubusercontent.com/claudianus/maru-deep-pro-search/main/scripts/install.sh | bash</span></div>
              <div class="text-gray-500"># Detects your AI agent, injects MCP config, enforces research-first rules</div>
            </div>
            <div v-else-if="activeTab === 1" class="space-y-1">
              <div><span class="prompt">$</span> <span class="command">pip install maru-deep-pro-search[semantic]</span></div>
              <div><span class="prompt">$</span> <span class="command">maru-deep-pro-search setup</span></div>
              <div class="text-gray-500"># Manual setup with full semantic search support</div>
            </div>
            <div v-else class="space-y-1">
              <div><span class="prompt">$</span> <span class="command">uv pip install maru-deep-pro-search[semantic]</span></div>
              <div><span class="prompt">$</span> <span class="command">maru-deep-pro-search setup</span></div>
              <div class="text-gray-500"># Fast install with uv package manager</div>
            </div>
          </div>
        </div>

        <div class="mt-6 flex flex-col sm:flex-row items-center justify-center gap-4 text-sm text-gray-500">
          <div class="flex items-center gap-2"><span class="text-emerald-400">✅</span><span>No API keys required</span></div>
          <div class="flex items-center gap-2"><span class="text-violet-400">⚡</span><span>Works with Claude, Cursor, Kimi, Windsurf</span></div>
        </div>
      </div>
    </UContainer>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import SectionTitle from '~/components/ui/SectionTitle.vue'

defineProps<{ oneLiner: string; noCurlLabel: string }>()
const activeTab = ref(0)
const tabs = [{ label: 'macOS / Linux' }, { label: 'pip' }, { label: 'uv' }]
</script>
