import type { BeforeAfterRow } from '~/types';

export function useBeforeAfterRows(): BeforeAfterRow[] {
  return [
    { before: 'Agent answers with stale 2023 training data', after: 'Live web search with freshness scoring' },
    { before: 'No sources, possible hallucination', after: 'Every claim backed by [1], [2] citations with real URLs' },
    { before: 'Manual MCP config per agent', after: 'One-liner auto-detects & configures all agents' },
    { before: '$5–50/month API costs', after: 'Forever free' },
    { before: 'Raw engine ordering', after: 'BM25 + semantic + metadata hybrid ranking' },
    { before: 'Single point of failure', after: '7-engine failover + smart fallback + domain history' },
  ];
}
