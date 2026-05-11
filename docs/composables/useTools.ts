import type { Tool } from '~/types';

export function useTools(): Tool[] {
  return [
    { name: 'answer', description: 'Quick answer with inline citations' },
    { name: 'web_search', description: 'Scrape + rank + return cited results' },
    { name: 'search_with_citations', description: 'Pre-numbered sources for academic writing' },
    { name: 'fetch_page', description: 'Extract clean content from a single URL' },
    { name: 'fetch_bulk', description: 'Parallel fetch with deduplication' },
    { name: 'deep_research', description: '7-phase pipeline: expand → search → rank → crawl → synthesize' },
    { name: 'stealthy_fetch', description: 'Anti-bot bypass for protected sites' },
    { name: 'parallel_search', description: 'Run multiple searches simultaneously' },
  ];
}
