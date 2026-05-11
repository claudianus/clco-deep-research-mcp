export default defineAppConfig({
  ui: {
    primary: 'violet',
    gray: 'zinc',
    button: {
      default: {
        size: 'sm',
      },
    },
    card: {
      base: 'overflow-hidden',
      background: 'bg-white/[0.03] dark:bg-white/[0.03]',
      ring: 'ring-1 ring-white/[0.08] dark:ring-white/[0.08]',
      divide: 'divide-y divide-white/[0.06] dark:divide-white/[0.06]',
    },
    badge: {
      base: 'font-medium',
    },
    tabs: {
      list: {
        background: 'bg-white/[0.03] dark:bg-white/[0.03]',
        marker: {
          background: 'bg-white/[0.08] dark:bg-white/[0.08]',
        },
      },
    },
  },
});
