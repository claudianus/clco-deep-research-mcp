<template>
  <div ref="container" class="mermaid-diagram">
    <div v-if="!ready" class="flex items-center justify-center py-12 text-sm text-gray-500">
      Loading diagram...
    </div>
  </div>
</template>

<script setup>
const props = defineProps({ definition: String })
const container = ref(null)
const ready = ref(false)

onMounted(async () => {
  if (process.client) {
    const mermaid = await import('mermaid')
    mermaid.default.initialize({
      startOnLoad: false,
      theme: 'dark',
      darkMode: true,
      themeVariables: {
        fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace',
        fontSize: '14px',
      },
    })
    if (container.value) {
      const { svg } = await mermaid.default.render('mermaid-' + Math.random().toString(36).slice(2), props.definition)
      container.value.innerHTML = svg
      ready.value = true
    }
  }
})
</script>

<style>
.mermaid-diagram svg {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 0 auto;
}
</style>
