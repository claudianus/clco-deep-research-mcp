import type { Feature } from '~/types';

export function useFeatures(): Feature[] {
  return [
    {
      icon: '🔑',
      title: 'Zero API Keys',
      description: 'No OpenAI, no Google Search API, no SerpAPI. Only direct HTTP scraping across 7 engines.',
    },
    {
      icon: '🧠',
      title: 'Semantic Hybrid Ranking',
      description: 'BM25 + dense vector similarity via multilingual-e5-small (33M, 384-dim, 100+ languages). Falls back gracefully.',
    },
    {
      icon: '🛡️',
      title: 'Smart Fallback',
      description: 'Error-type-aware handling (DNS→skip, SSL→stealth, 403→stealth). Domain history blacklist. Network probe.',
    },
    {
      icon: '📎',
      title: 'Citation-Native',
      description: 'Every result gets [1], [2] IDs before synthesis. LLMs cite sources accurately with real URLs and dates.',
    },
    {
      icon: '🗄️',
      title: 'Harness Platform',
      description: 'Project-level SQLite knowledge store with FTS5, domain stats, and optional semantic embeddings. 7-phase workflow engine.',
    },
    {
      icon: '⚡',
      title: 'Production Performance',
      description: 'Scrapling session reuse, early abort at 3 HIGH results, asyncio concurrency. Full deep_research <10s target.',
    },
  ];
}
