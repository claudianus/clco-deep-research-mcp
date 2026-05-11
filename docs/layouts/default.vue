<template>
  <div class="min-h-screen bg-[#0a0a0f] text-gray-100 antialiased">
    <!-- Nav -->
    <nav class="sticky top-0 z-50 border-b border-gray-800/60 bg-[#0a0a0f]/80 backdrop-blur-xl">
      <UContainer>
        <div class="flex h-14 items-center justify-between">
          <NuxtLink :to="localePath('/')" class="bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-lg font-bold text-transparent">
            maru-deep-pro-search
          </NuxtLink>
          <div class="flex items-center gap-4 text-sm">
            <NuxtLink :to="localePath('/')" class="text-gray-400 hover:text-white transition">{{ $t('nav.home') }}</NuxtLink>
            <NuxtLink :to="localePath('/architecture')" class="text-gray-400 hover:text-white transition">{{ $t('nav.architecture') }}</NuxtLink>
            <NuxtLink :to="localePath('/tools')" class="text-gray-400 hover:text-white transition">{{ $t('nav.tools') }}</NuxtLink>
            <NuxtLink to="https://github.com/claudianus/maru-deep-pro-search" target="_blank" class="text-gray-400 hover:text-white transition">GitHub</NuxtLink>
            <NuxtLink to="https://pypi.org/project/maru-deep-pro-search/" target="_blank" class="text-gray-400 hover:text-white transition">PyPI</NuxtLink>
            <NuxtLink v-if="locale === 'en'" :to="switchLocalePath('ko')" class="rounded-md bg-gray-800 px-2 py-1 text-xs text-gray-300 hover:bg-gray-700 transition">🇰🇷 KO</NuxtLink>
            <NuxtLink v-else :to="switchLocalePath('en')" class="rounded-md bg-gray-800 px-2 py-1 text-xs text-gray-300 hover:bg-gray-700 transition">🇺🇸 EN</NuxtLink>
          </div>
        </div>
      </UContainer>
    </nav>

    <!-- Main -->
    <main>
      <slot />
    </main>

    <!-- Footer -->
    <footer class="border-t border-gray-800/60 py-8">
      <UContainer>
        <div class="flex flex-col items-center justify-between gap-3 sm:flex-row">
          <p class="text-sm text-gray-500">MIT © <NuxtLink to="https://github.com/claudianus" class="text-gray-400 hover:text-white transition">claudianus</NuxtLink></p>
          <div class="flex gap-4 text-sm text-gray-500">
            <NuxtLink to="https://github.com/claudianus/maru-deep-pro-search" class="hover:text-white transition">GitHub</NuxtLink>
            <NuxtLink to="https://pypi.org/project/maru-deep-pro-search/" class="hover:text-white transition">PyPI</NuxtLink>
            <NuxtLink to="https://github.com/claudianus/maru-deep-pro-search/blob/main/CHANGELOG.md" class="hover:text-white transition">{{ $t('nav.changelog') }}</NuxtLink>
          </div>
        </div>
      </UContainer>
    </footer>
  </div>
</template>

<script setup>
const { locale } = useI18n();
const switchLocalePath = useSwitchLocalePath();
const localePath = useLocalePath();
</script>
