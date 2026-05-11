<template>
  <div class="mx-auto max-w-lg rounded-xl border border-indigo-500/20 bg-gray-900/80 p-4 backdrop-blur">
    <div class="mb-3 flex gap-2">
      <button
        v-for="cmd in commands"
        :key="cmd.os"
        class="rounded-md px-3 py-1 text-xs font-medium transition"
        :class="activeOs === cmd.os ? 'bg-indigo-500/20 text-indigo-400' : 'text-gray-500 hover:text-gray-300'"
        @click="activeOs = cmd.os"
      >
        {{ cmd.label }}
      </button>
    </div>
    <div class="flex items-center gap-2 rounded-lg bg-gray-950 p-3 font-mono text-sm">
      <span class="text-gray-600">$</span>
      <span class="text-emerald-400">{{ activeCommand.command }}</span>
      <button class="ml-auto rounded p-1 text-gray-500 hover:text-white transition" @click="copy">
        <svg class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <rect x="9" y="9" width="13" height="13" rx="2" />
          <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
        </svg>
      </button>
    </div>
    <p class="mt-2 text-xs text-gray-500">{{ oneLiner }}</p>
    <p class="mt-1 text-xs text-gray-600">
      {{ noCurlLabel }} <code class="text-gray-500">pip install maru-deep-pro-search[semantic] && maru-deep-pro-search setup</code>
    </p>
  </div>
</template>

<script setup lang="ts">
const commands = useInstallCommands();
const activeOs = ref<'mac' | 'win'>('mac');
const activeCommand = computed(() => commands.find(c => c.os === activeOs.value)!);

function copy() {
  navigator.clipboard.writeText(activeCommand.value.command);
}

defineProps<{
  oneLiner: string;
  noCurlLabel: string;
}>();
</script>
