<template>
  <div class="min-h-screen surface-0 text-gray-100 antialiased">
    <nav class="sticky top-0 z-50 border-b border-white/[0.06] surface-0/80 backdrop-blur-xl">
      <UContainer>
        <div class="flex h-14 items-center justify-between">
          <NuxtLink :to="localePath('/')" class="text-lg font-bold text-gradient-violet">maru-deep-pro-search</NuxtLink>
          <div class="hidden md:flex items-center gap-6 text-sm text-gray-400">
            <NuxtLink :to="localePath('/')" class="hover:text-white transition">{{ $t('nav.home') }}</NuxtLink>
            <NuxtLink :to="localePath('/architecture')" class="hover:text-white transition">{{ $t('nav.architecture') }}</NuxtLink>
            <NuxtLink :to="localePath('/tools')" class="hover:text-white transition">{{ $t('nav.tools') }}</NuxtLink>
            <NuxtLink to="https://github.com/claudianus/maru-deep-pro-search" target="_blank" class="hover:text-white transition">GitHub</NuxtLink>
            <NuxtLink to="https://pypi.org/project/maru-deep-pro-search/" target="_blank" class="hover:text-white transition">PyPI</NuxtLink>
            <NuxtLink v-if="locale === 'en'" :to="switchLocalePath('ko')" class="hover:text-white transition text-xs">🇰🇷 KO</NuxtLink>
            <NuxtLink v-else :to="switchLocalePath('en')" class="hover:text-white transition text-xs">🇺🇸 EN</NuxtLink>
          </div>
        </div>
      </UContainer>
    </nav>
    <main><slot /></main>
    <footer class="border-t border-white/[0.06] surface-50">
      <UContainer>
        <div class="py-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-gray-500">
          <span>MIT © <NuxtLink to="https://github.com/claudianus" class="hover:text-white transition">claudianus</NuxtLink></span>
          <div class="flex gap-4">
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
const { locale } = useI18n()
const switchLocalePath = useSwitchLocalePath()
const localePath = useLocalePath()
</script>
