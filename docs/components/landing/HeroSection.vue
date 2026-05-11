<template>
  <section class="relative overflow-hidden surface-0">
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute top-[-20%] left-[50%] -translate-x-1/2 w-[800px] h-[600px] rounded-full bg-violet-500/[0.07] blur-[120px]" />
      <div class="absolute top-[10%] left-[20%] w-[400px] h-[400px] rounded-full bg-indigo-500/[0.05] blur-[100px]" />
    </div>

    <UContainer class="relative z-10 pt-24 pb-16 md:pt-32 md:pb-24">
      <div class="max-w-5xl mx-auto text-center">
        <div class="mb-6 inline-flex items-center gap-2">
          <UBadge color="violet" variant="subtle" size="sm" class="font-mono text-xs">MCP Server · v0.9.0</UBadge>
          <UBadge color="emerald" variant="subtle" size="sm" class="font-mono text-xs">193 Tests Passing</UBadge>
        </div>

        <h1 class="text-4xl md:text-6xl lg:text-7xl font-extrabold tracking-tight leading-[1.1] mb-6">
          <span class="text-white">Force your AI agent</span><br />
          <span class="text-gradient-violet">to research first.</span>
        </h1>

        <p class="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto mb-8 leading-relaxed">{{ tagline }}</p>

        <div class="flex flex-col sm:flex-row items-center justify-center gap-3 mb-12">
          <UButton size="lg" color="violet" variant="solid" class="font-semibold px-6" @click="scrollToInstall">
            {{ $t('install.button') || 'Install in 10 seconds' }}
          </UButton>
          <UButton size="lg" color="gray" variant="ghost" class="font-medium" to="https://github.com/claudianus/maru-deep-pro-search" target="_blank">
            View on GitHub
          </UButton>
        </div>

        <div class="max-w-2xl mx-auto">
          <div class="terminal-window text-left">
            <div class="terminal-header">
              <div class="terminal-dot bg-red-400/80" />
              <div class="terminal-dot bg-yellow-400/80" />
              <div class="terminal-dot bg-green-400/80" />
              <span class="ml-2 text-xs text-gray-500 font-mono">bash — maru-deep-pro-search</span>
            </div>
            <div class="terminal-body space-y-1">
              <div><span class="prompt">$</span> <span class="command">curl -sSL https://raw.githubusercontent.com/claudianus/maru-deep-pro-search/main/scripts/install.sh | bash</span></div>
              <div class="text-emerald-400">✓ Package installed</div>
              <div class="text-emerald-400">✓ AI agent auto-detected</div>
              <div class="text-emerald-400">✓ MCP config injected</div>
              <div class="text-emerald-400">✓ Research-first rules enforced</div>
              <div class="text-gray-500 mt-2"># Or with pip: <span class="text-gray-300">pip install maru-deep-pro-search[semantic] && maru-deep-pro-search setup</span></div>
            </div>
          </div>
        </div>
      </div>
    </UContainer>
  </section>
</template>

<script setup lang="ts">
defineProps<{ tagline: string }>()
const scrollToInstall = () => {
  const el = document.getElementById('install')
  if (el) el.scrollIntoView({ behavior: 'smooth' })
}
</script>
