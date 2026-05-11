import type { PerformanceMetric } from '~/types';

export function usePerformanceMetrics(): PerformanceMetric[] {
  return [
    { metric: 'Cache hit (KnowledgeStore)', target: '<100ms', implementation: 'SQLite FTS5 + indexed domain_stats' },
    { metric: 'Full deep_research', target: '<10s', implementation: '7 engines, 5 concurrent, early abort at 3 HIGH results' },
    { metric: 'Scrapling session startup', target: '~0ms (amortized)', implementation: 'Single session reused per engine instance' },
    { metric: 'Semantic model load', target: '~2s (first call only)', implementation: 'Lazy init, CPU-only' },
    { metric: 'Memory footprint', target: '~150MB base', implementation: '+120MB with semantic model. No GPU required.' },
  ];
}
