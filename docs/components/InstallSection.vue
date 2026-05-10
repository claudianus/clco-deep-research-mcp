<template>
  <section class="border-t border-gray-800/60 py-20">
    <UContainer>
      <div class="mb-12 text-center">
        <h2 class="text-3xl font-bold tracking-tight">{{ $t('install.title') }}</h2>
      </div>

      <div class="mx-auto grid max-w-6xl gap-8 lg:grid-cols-3">
        <!-- Auto Setup -->
        <UCard class="border-indigo-500/30 bg-indigo-950/10" :ui="{ body: { base: 'p-6' } }">
          <div class="mb-4 flex items-center justify-between">
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-rocket-launch" class="text-emerald-400" />
              <h3 class="text-lg font-semibold">{{ $t('install.autoTitle') }}</h3>
            </div>
            <UBadge color="emerald" variant="subtle" size="sm">Recommended</UBadge>
          </div>
          <p class="mb-4 text-sm text-gray-400">{{ $t('install.autoDesc') }}</p>
          <!-- OS Tabs -->
          <div class="flex gap-2 mb-3">
            <button
              class="rounded-md px-3 py-1 text-xs font-medium transition-colors"
              :class="osTab === 'mac' ? 'bg-indigo-500/20 text-indigo-400' : 'text-gray-500 hover:text-gray-300'"
              @click="osTab = 'mac'"
            >
              macOS / Linux
            </button>
            <button
              class="rounded-md px-3 py-1 text-xs font-medium transition-colors"
              :class="osTab === 'win' ? 'bg-indigo-500/20 text-indigo-400' : 'text-gray-500 hover:text-gray-300'"
              @click="osTab = 'win'"
            >
              Windows
            </button>
          </div>

          <!-- One-liner -->
          <div class="rounded-lg border border-gray-800 bg-gray-950 p-4 font-mono text-sm">
            <div class="flex items-center justify-between gap-2">
              <code class="text-emerald-400 break-all">{{ currentCommand }}</code>
              <UButton
                :icon="copied.setup ? 'i-heroicons-check' : 'i-heroicons-document-duplicate'"
                color="gray"
                variant="ghost"
                size="xs"
                class="shrink-0"
                @click="copy('setup', currentCommand)"
              />
            </div>
          </div>

          <div class="mt-2 text-xs text-gray-600">
            No curl? <code class="text-gray-500">pip install maru-deep-pro-search && maru-deep-pro-search setup</code>
          </div>
          <div class="mt-4 space-y-2 text-sm text-gray-400">
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-check-circle" class="text-emerald-400" />
              <span>{{ $t('install.autoDetect') }}</span>
            </div>
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-check-circle" class="text-emerald-400" />
              <span>{{ $t('install.autoBackup') }}</span>
            </div>
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-check-circle" class="text-emerald-400" />
              <span>{{ $t('install.autoInject') }}</span>
            </div>
          </div>
          <div class="mt-4 rounded-lg border border-gray-800 bg-gray-950 p-3 font-mono text-xs text-gray-500">
            <div class="flex items-center justify-between">
              <code>--list</code>
              <span class="text-gray-600">{{ $t('install.flagList') }}</span>
            </div>
            <div class="flex items-center justify-between mt-1">
              <code>--check</code>
              <span class="text-gray-600">{{ $t('install.flagCheck') }}</span>
            </div>
            <div class="flex items-center justify-between mt-1">
              <code>--restore</code>
              <span class="text-gray-600">{{ $t('install.flagRestore') }}</span>
            </div>
          </div>
        </UCard>

        <!-- Manual -->
        <UCard class="border-gray-800 bg-gray-900/40" :ui="{ body: { base: 'p-6' } }">
          <h3 class="mb-4 text-lg font-semibold">Claude Code</h3>
          <div class="rounded-lg border border-gray-800 bg-gray-950 p-4 font-mono text-sm">
            <div class="flex items-center justify-between">
              <code class="text-gray-300">claude mcp add maru-deep-pro-search pip:maru-deep-pro-search</code>
              <UButton
                :icon="copied.claude ? 'i-heroicons-check' : 'i-heroicons-document-duplicate'"
                color="gray"
                variant="ghost"
                size="xs"
                @click="copy('claude', 'claude mcp add maru-deep-pro-search pip:maru-deep-pro-search')"
              />
            </div>
          </div>
        </UCard>

        <!-- Config -->
        <UCard class="border-gray-800 bg-gray-900/40" :ui="{ body: { base: 'p-6' } }">
          <h3 class="mb-4 text-lg font-semibold">{{ $t('install.config') }}</h3>
          <div class="rounded-lg border border-gray-800 bg-gray-950 p-4 font-mono text-sm leading-relaxed text-gray-300">
            <pre>{
  "mcpServers": {
    "maru-deep-pro-search": {
      "command": "python3",
      "args": [
        "-m",
        "maru_deep_pro_search.server"
      ]
    }
  }
}</pre>
          </div>

          <h3 class="mb-4 mt-8 text-lg font-semibold">{{ $t('install.env') }}</h3>
          <div class="space-y-2 text-sm text-gray-400">
            <div class="flex justify-between rounded-md bg-gray-950 px-3 py-2">
              <code class="text-indigo-300">MARU_SEARCH_ENGINE</code>
              <span>duckduckgo_lite</span>
            </div>
            <div class="flex justify-between rounded-md bg-gray-950 px-3 py-2">
              <code class="text-indigo-300">MARU_SEARCH_MAX_RESULTS</code>
              <span>10</span>
            </div>
            <div class="flex justify-between rounded-md bg-gray-950 px-3 py-2">
              <code class="text-indigo-300">MARU_SEARCH_MAX_CONCURRENT</code>
              <span>5</span>
            </div>
          </div>
        </UCard>
      </div>
    </UContainer>
  </section>
</template>

<script setup>
const copied = reactive({ setup: false, pip: false, claude: false })
const osTab = ref('mac')

const commandMap = {
  mac: 'curl -sSL https://raw.githubusercontent.com/claudianus/maru-deep-pro-search/main/scripts/install.sh | bash',
  win: 'irm https://raw.githubusercontent.com/claudianus/maru-deep-pro-search/main/scripts/install.ps1 | iex',
}
const currentCommand = computed(() => commandMap[osTab.value])

function copy(key, text) {
  navigator.clipboard.writeText(text)
  copied[key] = true
  setTimeout(() => copied[key] = false, 2000)
}
</script>
