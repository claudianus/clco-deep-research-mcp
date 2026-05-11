import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  site: 'https://claudianus.github.io',
  base: '/maru-deep-pro-search',
  integrations: [
    starlight({
      title: 'maru-deep-pro-search',
      tagline: 'Force your AI agent to research before it codes.',
      defaultLocale: 'en',
      locales: {
        en: {
          label: 'English',
          lang: 'en',
        },
        ko: {
          label: '한국어',
          lang: 'ko',
        },
      },
      social: {
        github: 'https://github.com/claudianus/maru-deep-pro-search',
      },
      editLink: {
        baseUrl: 'https://github.com/claudianus/maru-deep-pro-search/edit/main/docs/',
      },
      sidebar: [
        {
          label: 'Overview',
          items: [
            { label: 'Introduction', link: '/' },
            { label: 'Architecture', link: '/architecture/' },
            { label: 'Tools', link: '/tools/' },
          ],
        },
        {
          label: 'Deep Dive',
          items: [
            { label: 'Query Expansion', link: '/deep-dive/query-expansion/' },
            { label: 'Hybrid Ranking', link: '/deep-dive/hybrid-ranking/' },
            { label: 'Smart Fetch', link: '/deep-dive/smart-fetch/' },
            { label: 'Harness Platform', link: '/deep-dive/harness/' },
            { label: 'Prompt Injection Defense', link: '/deep-dive/prompt-injection-defense/' },
          ],
        },
        {
          label: 'Reference',
          items: [
            { label: 'Performance', link: '/performance/' },
            { label: 'Configuration', link: '/configuration/' },
            { label: 'Before & After', link: '/before-after/' },
          ],
        },
      ],
      customCss: [
        './src/styles/custom.css',
      ],
      pagefind: true,
      favicon: '/favicon.svg',
      head: [
        {
          tag: 'meta',
          attrs: {
            property: 'og:image',
            content: 'https://claudianus.github.io/maru-deep-pro-search/og-image.png',
          },
        },
      ],
    }),
    tailwind({
      applyBaseStyles: false,
    }),
  ],
});
