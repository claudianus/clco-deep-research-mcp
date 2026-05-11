import en from './i18n/en.json'
import ko from './i18n/ko.json'

export default defineNuxtConfig({
  modules: [
    '@nuxt/ui',
    '@nuxtjs/i18n',
    '@vueuse/nuxt',
    '@nuxt/fonts',
    '@nuxt/icon',
  ],
  ui: {
    primary: 'violet',
    gray: 'zinc',
  },
  colorMode: {
    preference: 'dark',
    fallback: 'dark',
  },
  i18n: {
    strategy: 'prefix_except_default',
    defaultLocale: 'en',
    locales: [
      { code: 'en', name: 'English' },
      { code: 'ko', name: '한국어' },
    ],
    detectBrowserLanguage: false,
  },
  ssr: true,
  nitro: {
    preset: 'github_pages',
  },
  app: {
    baseURL: '/maru-deep-pro-search/',
    buildAssetsDir: 'assets',
    head: {
      title: 'maru-deep-pro-search',
      meta: [
        { name: 'description', content: 'Force your AI agent to research before it codes.' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      ],
      link: [
        { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' },
      ],
    },
  },
  devtools: { enabled: false },
  fonts: {
    families: [
      { name: 'Inter', provider: 'google' },
      { name: 'JetBrains Mono', provider: 'google' },
    ],
  },
  // icon: {
  //   collections: ['lucide', 'simple-icons'],
  // },
});
