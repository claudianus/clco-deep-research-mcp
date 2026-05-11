<template>
  <span :class="$attrs.class">{{ emoji }}</span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  name: string
}>()

const map: Record<string, string> = {
  'i-lucide-search': '🔍',
  'i-lucide-globe': '🌐',
  'i-lucide-git-merge': '🔀',
  'i-lucide-bar-chart-3': '📊',
  'i-lucide-shield': '🛡️',
  'i-lucide-zap': '⚡',
  'i-lucide-file-text': '📄',
  'i-lucide-link': '🔗',
  'i-lucide-cpu': '💻',
  'i-lucide-message-circle': '💬',
  'i-lucide-book-open': '📖',
  'i-lucide-layers': '🥞',
  'i-lucide-flask-conical': '🧪',
  'i-lucide-git-branch': '🌿',
  'i-lucide-terminal': '💻',
  'i-lucide-shield-check': '✅',
  'i-lucide-x-circle': '❌',
  'i-lucide-check-circle': '✅',
  'i-lucide-minus': '−',
  'i-lucide-check': '✓',
  'i-lucide-arrow-right': '→',
  'i-lucide-external-link': '↗',
  'i-lucide-menu': '☰',
  'i-lucide-x': '✕',
  'i-simple-icons-github': '⭐',
  'i-simple-icons-pypi': '🐍',
}

const emoji = computed(() => map[props.name] || '•')
</script>
