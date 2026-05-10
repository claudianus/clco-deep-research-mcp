<template>
  <section class="relative overflow-hidden pb-24 pt-20">
    <!-- Animated grid background -->
    <div class="absolute inset-0 bg-[linear-gradient(to_right,#1f2937_1px,transparent_1px),linear-gradient(to_bottom,#1f2937_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] opacity-20" />
    <div class="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-900/20 via-gray-950 to-gray-950" />

    <UContainer class="relative">
      <div class="mx-auto max-w-3xl text-center">
        <UBadge color="indigo" variant="subtle" size="lg" class="mb-6">
          MCP Server
        </UBadge>
        <h1 class="mb-6 text-4xl font-extrabold tracking-tight sm:text-6xl">
          <span class="bg-gradient-to-r from-indigo-400 via-violet-400 to-fuchsia-400 bg-clip-text text-transparent">
            {{ $t('hero.title') }}
          </span>
        </h1>

        <!-- Typing effect subtitle -->
        <p class="mb-2 text-lg text-gray-400 sm:text-xl min-h-[1.75rem]">
          <span class="text-indigo-400 font-semibold">{{ displayedText }}</span>
          <span class="inline-block w-0.5 h-5 bg-indigo-400 ml-1 animate-pulse align-middle" />
        </p>
        <p class="mb-10 text-lg text-gray-500 sm:text-xl">
          {{ $t('hero.subtitle') }}
        </p>

        <div class="flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
          <div class="flex w-full max-w-lg flex-col gap-2 rounded-lg border border-indigo-500/30 bg-gray-900/80 px-4 py-3 backdrop-blur">
            <!-- OS Tabs -->
            <div class="flex gap-2 mb-1">
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
            <!-- Command -->
            <div class="flex items-center gap-2 font-mono text-sm">
              <span class="text-gray-500">$</span>
              <span class="text-emerald-400">{{ currentCommand }}</span>
              <UButton
                :icon="copied ? 'i-heroicons-check' : 'i-heroicons-document-duplicate'"
                color="gray"
                variant="ghost"
                size="xs"
                class="ml-auto shrink-0"
                @click="copyInstall"
              />
            </div>
            <div class="text-xs text-gray-500">
              One-liner: installs + auto-detects your AI agent · Injects MCP config · Enforces research-first rules
            </div>
          </div>
        </div>

        <div class="mt-8 flex justify-center gap-3">
          <UButton
            :label="$t('hero.ctaInstall')"
            icon="i-heroicons-rocket-launch"
            to="#install"
            color="indigo"
            variant="solid"
            size="lg"
          />
          <UButton
            :label="$t('hero.ctaDemo')"
            icon="i-heroicons-magnifying-glass"
            to="#pipeline"
            color="gray"
            variant="solid"
            size="lg"
          />
        </div>
      </div>
    </UContainer>
  </section>
</template>

<script setup>
const { t } = useI18n()
const copied = ref(false)
const osTab = ref('mac')

const commandMap = {
  mac: 'curl -sSL https://raw.githubusercontent.com/claudianus/maru-deep-pro-search/main/scripts/install.sh | bash',
  win: 'irm https://raw.githubusercontent.com/claudianus/maru-deep-pro-search/main/scripts/install.ps1 | iex',
}
const currentCommand = computed(() => commandMap[osTab.value])

function copyInstall() {
  navigator.clipboard.writeText(currentCommand.value)
  copied.value = true
  setTimeout(() => copied.value = false, 2000)
}

// Typing effect
const phrases = computed(() => [
  t('hero.typing1'),
  t('hero.typing2'),
  t('hero.typing3'),
  t('hero.typing4'),
])

const displayedText = ref('')
let phraseIndex = 0
let charIndex = 0
let isDeleting = false
let typeSpeed = 100

function typeEffect() {
  const current = phrases.value[phraseIndex]

  if (isDeleting) {
    displayedText.value = current.substring(0, charIndex - 1)
    charIndex--
    typeSpeed = 50
  } else {
    displayedText.value = current.substring(0, charIndex + 1)
    charIndex++
    typeSpeed = 100
  }

  if (!isDeleting && charIndex === current.length) {
    isDeleting = true
    typeSpeed = 2000
  } else if (isDeleting && charIndex === 0) {
    isDeleting = false
    phraseIndex = (phraseIndex + 1) % phrases.value.length
    typeSpeed = 500
  }

  setTimeout(typeEffect, typeSpeed)
}

onMounted(() => {
  setTimeout(typeEffect, 1000)
})
</script>
