<template>
  <div class="overflow-hidden rounded-xl border border-white/[0.08]">
    <table class="w-full text-sm">
      <thead>
        <tr class="bg-white/[0.03] border-b border-white/[0.06]">
          <th
            v-for="col in columns"
            :key="col.key"
            class="px-4 py-3 text-left font-semibold text-gray-400 text-xs uppercase tracking-wider"
          >
            {{ col.label }}
          </th>
        </tr>
      </thead>
      <tbody class="divide-y divide-white/[0.04]">
        <tr
          v-for="(row, i) in rows"
          :key="i"
          class="transition-colors hover:bg-white/[0.02]"
          :class="i % 2 === 1 ? 'bg-white/[0.01]' : ''"
        >
          <td
            v-for="col in columns"
            :key="col.key"
            class="px-4 py-3"
            :class="col.class"
          >
            <slot :name="col.key" :row="row" :value="row[col.key]">
              {{ row[col.key] }}
            </slot>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
interface Column {
  key: string
  label: string
  class?: string
}

interface Row {
  [key: string]: any
}

defineProps<{
  columns: Column[]
  rows: Row[]
}>()
</script>
