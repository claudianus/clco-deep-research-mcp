<template>
  <div>
    <HeroSection :tagline="$t('hero.tagline')" />
    <StatsBar />
    <FeatureGrid :title="$t('features.title')" :features="features" />
    <InstallBlock :one-liner="$t('install.oneLiner')" :no-curl-label="$t('install.noCurl')" />
    <ArchitectureSection :title="$t('architecture.title')" :footer="$t('architecture.footer')" />
    <ToolsSection :title="$t('tools.title')" />
    <PerformanceSection :title="$t('performance.title')" :metrics="metrics" />
    <BeforeAfterSection :title="$t('beforeAfter.title')" :rows="beforeAfterRows" />
    <section class="surface-0 py-16 md:py-24 border-t border-white/[0.04]">
      <UContainer class="text-center">
        <SectionTitle size="xl">{{ $t('testing.title') }}</SectionTitle>
        <div class="mt-6 inline-flex items-center gap-3 surface-200 rounded-xl px-6 py-4 border border-white/[0.06]">
          <span class="text-emerald-400">💻</span>
          <code class="font-mono text-sm text-emerald-400">pytest tests/ -v</code>
        </div>
        <p class="mt-4 text-gray-400">{{ $t('testing.result') }}</p>
      </UContainer>
    </section>
  </div>
</template>

<script setup lang="ts">
import HeroSection from '~/components/landing/HeroSection.vue'
import StatsBar from '~/components/landing/StatsBar.vue'
import FeatureGrid from '~/components/landing/FeatureGrid.vue'
import InstallBlock from '~/components/landing/InstallBlock.vue'
import ArchitectureSection from '~/components/landing/ArchitectureSection.vue'
import ToolsSection from '~/components/landing/ToolsSection.vue'
import PerformanceSection from '~/components/landing/PerformanceSection.vue'
import BeforeAfterSection from '~/components/landing/BeforeAfterSection.vue'
import SectionTitle from '~/components/ui/SectionTitle.vue'

const features = useFeatures();
const metrics = usePerformanceMetrics();
const beforeAfterRows = useBeforeAfterRows();
</script>
