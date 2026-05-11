import type { Feature } from '~/types';

export function useFeatures(): Feature[] {
  return [
    {
      icon: '🔑',
      title: 'Zero API Keys',
      description: 'No OpenAI, no Google Search API, no SerpAPI. Only direct HTTP scraping across 7 engines.',
      tags: ['free', '7 engines'],
    },
    {
      icon: '🧠',
      title: 'Semantic Hybrid Ranking',
      description: 'BM25 + dense vector similarity via multilingual-e5-small (33M, 384-dim, 100+ languages). Falls back gracefully.',
      wide: true,
      tags: ['BM25', 'e5-small', '100+ languages'],
    },
    {
      icon: '🛡️',
      title: 'Smart Fallback',
      description: 'Error-type-aware handling (DNS→skip, SSL→stealth, 403→stealth). Domain history blacklist. Network probe.',
      tags: ['stealth', 'failover'],
    },
    {
      icon: '📎',
      title: 'Citation-Native',
      description: 'Every result gets [1], [2] IDs before synthesis. LLMs cite sources accurately with real URLs and dates.',
      tags: ['sources', 'accuracy'],
    },
    {
      icon: '🗄️',
      title: 'Harness Platform',
      description: 'Project-level SQLite knowledge store with FTS5, domain stats, and optional semantic embeddings. 7-phase workflow engine.',
      wide: true,
      tags: ['SQLite', 'FTS5', '7-phase'],
    },
    {
      icon: '⚡',
      title: 'Production Performance',
      description: 'Scraping session reuse, early abort at 3 HIGH results, asyncio concurrency. Full deep_research <10s target.',
      tags: ['<10s', 'asyncio'],
    },
  ];
}
