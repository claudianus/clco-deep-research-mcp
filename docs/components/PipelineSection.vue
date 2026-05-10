<template>
  <section class="relative overflow-hidden border-t border-gray-800/60 py-20">
    <div class="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom,_var(--tw-gradient-stops))] from-violet-900/10 via-gray-950 to-gray-950" />
    <UContainer class="relative">
      <div class="mb-4 text-center">
        <UBadge color="violet" variant="subtle" size="lg" class="mb-4">Pipeline</UBadge>
        <h2 class="text-3xl font-bold tracking-tight sm:text-4xl">{{ $t('pipeline.title') }}</h2>
        <p class="mt-3 text-gray-400">{{ $t('pipeline.subtitle') }}</p>
      </div>

      <div class="mt-16">
        <div class="relative">
          <!-- Connecting line -->
          <div class="absolute left-8 top-0 hidden h-full w-px bg-gradient-to-b from-indigo-500/50 via-violet-500/50 to-fuchsia-500/50 md:left-1/2 md:block md:-translate-x-px" />

          <div class="space-y-12">
            <div
              v-for="(step, i) in steps"
              :key="i"
              class="relative flex flex-col gap-6 md:flex-row"
              :class="i % 2 === 0 ? 'md:flex-row' : 'md:flex-row-reverse'"
            >
              <!-- Content -->
              <div class="flex-1 md:text-right" :class="i % 2 === 0 ? 'md:text-right' : 'md:text-left'">
                <div
                  class="group relative rounded-xl border border-gray-800 bg-gray-900/40 p-6 backdrop-blur transition-all hover:border-indigo-500/30 hover:bg-gray-800/60"
                >
                  <div class="absolute inset-0 rounded-xl bg-gradient-to-br from-indigo-500/5 to-violet-500/5 opacity-0 transition-opacity group-hover:opacity-100" />
                  <div class="relative">
                    <div class="mb-2 text-xs font-bold tracking-wider text-indigo-400 uppercase">Phase {{ i + 1 }}</div>
                    <h3 class="mb-1 text-lg font-semibold">{{ step.title }}</h3>
                    <p class="text-sm text-gray-400">{{ step.desc }}</p>
                  </div>
                </div>
              </div>

              <!-- Center dot -->
              <div class="relative flex items-center justify-center md:w-16">
                <div class="z-10 flex h-10 w-10 items-center justify-center rounded-full border border-indigo-500/30 bg-gray-950 text-sm font-bold text-indigo-400 shadow-lg shadow-indigo-500/10">
                  {{ i + 1 }}
                </div>
              </div>

              <!-- Spacer for alternating layout -->
              <div class="hidden flex-1 md:block" />
            </div>
          </div>
        </div>
      </div>
    </UContainer>
  </section>
</template>

<script setup>
const { t } = useI18n()
const steps = computed(() => [
  { title: t('pipeline.step1'), desc: t('pipeline.step1Desc') },
  { title: t('pipeline.step2'), desc: t('pipeline.step2Desc') },
  { title: t('pipeline.step3'), desc: t('pipeline.step3Desc') },
  { title: t('pipeline.step4'), desc: t('pipeline.step4Desc') },
  { title: t('pipeline.step5'), desc: t('pipeline.step5Desc') },
  { title: t('pipeline.step6'), desc: t('pipeline.step6Desc') },
  { title: t('pipeline.step7'), desc: t('pipeline.step7Desc') },
])
</script>
