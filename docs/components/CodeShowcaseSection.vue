<template>
  <section class="border-t border-gray-800/60 py-20">
    <UContainer>
      <div class="mb-4 text-center">
        <UBadge color="emerald" variant="subtle" size="lg" class="mb-4">Zero API Cost</UBadge>
        <h2 class="text-3xl font-bold tracking-tight sm:text-4xl">{{ $t('codeShowcase.title') }}</h2>
        <p class="mt-3 text-gray-400">{{ $t('codeShowcase.subtitle') }}</p>
      </div>

      <div class="mt-12 mx-auto max-w-3xl">
        <!-- Tabs -->
        <div class="flex gap-2 rounded-t-xl border border-gray-800 bg-gray-900/60 p-2">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="rounded-lg px-4 py-2 text-sm font-medium transition-colors"
            :class="activeTab === tab.key ? 'bg-indigo-500/10 text-indigo-400' : 'text-gray-500 hover:text-gray-300'"
            @click="activeTab = tab.key"
          >
            {{ tab.label }}
          </button>
        </div>

        <!-- Code block -->
        <div class="rounded-b-xl border border-t-0 border-gray-800 bg-gray-950 p-6">
          <div class="flex items-center justify-between mb-4">
            <div class="flex gap-1.5">
              <div class="h-3 w-3 rounded-full bg-red-500/20" />
              <div class="h-3 w-3 rounded-full bg-amber-500/20" />
              <div class="h-3 w-3 rounded-full bg-emerald-500/20" />
            </div>
            <UButton
              :icon="copied ? 'i-heroicons-check' : 'i-heroicons-document-duplicate'"
              color="gray"
              variant="ghost"
              size="xs"
              @click="copyCode"
            />
          </div>
          <pre class="overflow-x-auto text-sm leading-relaxed"><code class="language-python" v-html="highlightedCode" /></pre>
        </div>
      </div>
    </UContainer>
  </section>
</template>

<script setup>
const { t } = useI18n()
const activeTab = ref('quick')
const copied = ref(false)

const tabs = computed(() => [
  { key: 'quick', label: t('codeShowcase.tab1') },
  { key: 'deep', label: t('codeShowcase.tab2') },
  { key: 'cited', label: t('codeShowcase.tab3') },
])

const codeMap = computed(() => ({
  quick: t('codeShowcase.code1'),
  deep: t('codeShowcase.code2'),
  cited: t('codeShowcase.code3'),
}))

const currentCode = computed(() => codeMap.value[activeTab.value])

function copyCode() {
  navigator.clipboard.writeText(currentCode.value)
  copied.value = true
  setTimeout(() => copied.value = false, 2000)
}

// Simple syntax highlighting
const highlightedCode = computed(() => {
  let code = currentCode.value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')

  // Comments
  code = code.replace(/(#.*$)/gm, '<span class="text-gray-500">$1</span>')
  // Keywords
  code = code.replace(/\b(from|import|def|return|print|class|if|else|for|while|with|as|try|except)\b/g, '<span class="text-pink-400">$1</span>')
  // Strings
  code = code.replace(/(['"`'])(.*?)\1/g, '<span class="text-emerald-400">$1$2$1</span>')
  // Functions
  code = code.replace(/(\w+)(\()/g, '<span class="text-blue-400">$1</span>$2')
  // Numbers
  code = code.replace(/\b(\d+)\b/g, '<span class="text-amber-400">$1</span>')

  return code
})
</script>
