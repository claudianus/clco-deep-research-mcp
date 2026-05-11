<template>
  <div>
    <HeroSection :tagline="$t('hero.tagline')">
      <InstallBlock :one-liner="$t('install.oneLiner')" :no-curl-label="$t('install.noCurl')" />
    </HeroSection>

    <FeatureGrid :title="$t('features.title')" :features="features" />
    <ArchitectureSection :title="$t('architecture.title')" :footer="$t('architecture.footer')" />
    <ToolsSection :title="$t('tools.title')" :tools="tools" />
    <PerformanceSection :title="$t('performance.title')" :metrics="metrics" />
    <BeforeAfterSection :title="$t('beforeAfter.title')" :rows="beforeAfterRows" />

    <section class="border-t border-gray-800/60 py-16">
      <UContainer class="text-center">
        <SectionTitle>{{ $t('testing.title') }}</SectionTitle>
        <div class="rounded-lg bg-gray-950 p-3 font-mono text-sm text-emerald-400 inline-block">
          {{ $t('testing.command') }}
        </div>
        <p class="mt-4 text-gray-400">{{ $t('testing.result') }}</p>
      </UContainer>
    </section>

    <section class="border-t border-gray-800/60 py-8">
      <UContainer class="text-center">
        <p class="text-sm text-gray-500">{{ $t('license.text') }}</p>
      </UContainer>
    </section>
  </div>
</template>

<script setup lang="ts">
const features = useFeatures();
const tools = useTools();
const metrics = usePerformanceMetrics();
const beforeAfterRows = useBeforeAfterRows();
</script>
