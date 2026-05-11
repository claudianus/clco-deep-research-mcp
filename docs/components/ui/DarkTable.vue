<template>
  <div class="overflow-hidden rounded-xl border border-gray-800">
    <table class="w-full text-sm">
      <thead class="bg-gray-800 text-gray-300">
        <tr>
          <th v-for="col in columns" :key="col.key" class="px-4 py-3 text-left font-semibold">
            {{ col.label }}
          </th>
        </tr>
      </thead>
      <tbody class="divide-y divide-gray-800">
        <tr v-for="(row, i) in rows" :key="i" :class="i % 2 === 1 ? 'bg-gray-900/30' : ''">
          <td v-for="col in columns" :key="col.key" class="px-4 py-3" :class="col.class">
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
  key: string;
  label: string;
  class?: string;
}

interface Row {
  [key: string]: any;
}

defineProps<{
  columns: Column[];
  rows: Row[];
}>();
</script>
