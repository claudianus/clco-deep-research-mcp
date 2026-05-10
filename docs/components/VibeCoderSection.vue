<template>
  <section class="border-t border-gray-800/60 py-20">
    <UContainer>
      <div class="mb-4 text-center">
        <UBadge color="fuchsia" variant="subtle" size="lg" class="mb-4">Vibe Coding</UBadge>
        <h2 class="text-3xl font-bold tracking-tight sm:text-4xl">{{ isKo ? '딥리서치와 함께하는 바이브 코딩' : 'Vibe Coding with Deep Research' }}</h2>
        <p class="mt-3 text-gray-400">{{ isKo ? '추측하지 마세요. 먼저 리서치하고, 그다음 개발하세요.' : "Don't guess. Research first, then build." }}</p>
      </div>

      <div class="mt-12 grid gap-6 lg:grid-cols-2">
        <div
          v-for="(s, i) in scenarios"
          :key="i"
          class="group relative rounded-2xl border border-gray-800 bg-gray-900/30 p-6 transition-all hover:border-fuchsia-500/30 hover:bg-gray-800/40"
        >
          <div class="absolute inset-0 rounded-2xl bg-gradient-to-br from-fuchsia-500/5 to-violet-500/5 opacity-0 transition-opacity group-hover:opacity-100" />
          <div class="relative">
            <!-- Header -->
            <div class="mb-4 flex items-center gap-3">
              <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-fuchsia-500/10 text-fuchsia-400 ring-1 ring-fuchsia-500/20">
                <UIcon :name="s.icon" class="h-5 w-5" />
              </div>
              <h3 class="text-lg font-semibold">{{ s.title }}</h3>
            </div>

            <!-- Prompt -->
            <div class="mb-4">
              <div class="mb-1.5 text-[10px] font-bold uppercase tracking-wider text-gray-500">Prompt</div>
              <div class="rounded-lg border border-gray-800 bg-gray-950 p-3 text-sm leading-relaxed text-gray-300">
                {{ s.prompt }}
              </div>
            </div>

            <!-- Result -->
            <div>
              <div class="mb-1.5 text-[10px] font-bold uppercase tracking-wider text-emerald-400">Result</div>
              <div class="space-y-1 rounded-lg border border-gray-800 bg-gray-950 p-3">
                <p v-for="(line, idx) in s.result" :key="idx" class="text-sm leading-relaxed text-gray-400">{{ line }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </UContainer>
  </section>
</template>

<script setup>
const { locale } = useI18n()
const isKo = computed(() => locale.value === 'ko')

const scenarios = computed(() => {
  if (isKo.value) {
    return [
      {
        icon: 'i-heroicons-rocket-launch',
        title: '프로젝트 기획',
        prompt: '실시간 협업 텍스트 에디터를 개발하려고 합니다. 시장 트렌드, 경쟁사, 검증된 기술 스택을 딥리서치해서 최적의 아키텍처를 제안해줘.',
        result: [
          '14개 소스 분석 [1]-[14]:',
          '• 트렌드: CRDT 채택률 2023년 이후 340% 상승 [1][2]',
          '• 경쟁사: Notion(프로프라이어터리), Etherpad(노후화), Yjs가 OSS 시장 지배 [3]',
          '• 검증된 스택: Yjs + WebSocket + PostgreSQL — Linear, Figma도 사용 [4][5]',
          '• 피할 것: OT 알고리즘(신규 프로젝트에 복잡도 과다) [6]',
        ],
      },
      {
        icon: 'i-heroicons-scale',
        title: '기술 스택 검증',
        prompt: 'Next.js API에 tRPC와 GraphQL 중 어떤 걸 써야 할까? 트레이드오프, 성능 벤치마크, 2024년 커뮤니티 채택률을 리서치해줘.',
        result: [
          '11개 소스 리서치 [1]-[11]:',
          '• tRPC: 타입 안전 end-to-end, 스키마 중복 제로, 모노레포에 최적 [1][2]',
          '• GraphQL: 공개 API, 다중 클라이언트, 복잡 쿼리에 유리 [3]',
          '• 판결: 내규 Next.js 앱은 tRPC, 3rd-party 접근 필요하면 GraphQL [4]',
          '• 벤치마크: 단순 쿼리는 tRPC가 ~2.3배 빠름, 복잡 중첩은 GraphQL 우세 [5]',
        ],
      },
      {
        icon: 'i-heroicons-bug-ant',
        title: '다중 소스 기반 디버깅',
        prompt: "Next.js 14 App Router에서 'Module not found: Can't resolve fs' 에러가 나요. 공식 문서, GitHub 이슈, Stack Overflow에서 검증된 해결책을 찾아줘.",
        result: [
          '8개 소스 교차 검증 [1]-[8]:',
          '• 원인: Next.js 14 App Router는 기본적으로 Edge Runtime — fs는 Node 전용 [1]',
          "• 해결책 A: 라우트 파일에 export const runtime = 'nodejs' 추가 [2]",
          '• 해결책 B: fs 의존 라이브러리는 dynamic import + ssr: false 사용 [3][4]',
          '• 검증: GitHub에서 47개 이슈가 해결책 A로 클로즈됨 [5]',
        ],
      },
      {
        icon: 'i-heroicons-shield-check',
        title: '보안 및 CVE 리서치',
        prompt: 'CVE-2024-21529가 우리 Express.js 백엔드에 미치는 영향을 평가해줘. 패치, 우회책, 현재 버전이 취약한지 알려줘.',
        result: [
          '6개 보안 소스 분석 [1]-[6]:',
          '• 심각도: HIGH (CVSS 7.5) — express.static 경로 탐색 [1]',
          '• 영향: express < 4.19.0 — 현재 버전(4.18.2) 취약함 [2]',
          '• 패치: express@4.19.2로 업그레이드 또는 경로 정규화 미들웨어 적용 [3]',
          '• 우회책: helmet + strict path validation을 static 미들웨어 전에 추가 [4]',
        ],
      },
      {
        icon: 'i-heroicons-document-text',
        title: '기술 문서 및 학술 작성',
        prompt: '시스템 설계 문서용으로 Raft와 Paxos 합의 알고리즘의 기술적 비교를 적절한 인출과 함께 작성해줘.',
        result: [
          '9개 학술/기술 소스 종합 [1]-[9]:',
          '• Raft: 이해와 구현이 쉬움 (Ongaro & Ousterhout, 2014) [1]',
          '• Paxos: 이론적 정확성이 입증됨, 이론상 더 효율적 (Lamport, 1989) [2]',
          '• 프로덕션 사용: etcd/RabbitMQ는 Raft; Chubby/Spanner는 Paxos 계열 [3][4]',
          '• 권장: 형식적 방법 팀이 없으면 신규 시스템에 Raft [5]',
        ],
      },
    ]
  }

  return [
    {
      icon: 'i-heroicons-rocket-launch',
      title: 'Project Planning',
      prompt: 'I want to build a real-time collaborative text editor. Deep research market trends, competitors, and verified tech stacks, then propose the best architecture.',
      result: [
        'After analyzing 14 sources [1]-[14]:',
        '• Trend: CRDT adoption up 340% since 2023 [1][2]',
        '• Competitors: Notion (proprietary), Etherpad (aging), Yjs dominates OSS [3]',
        '• Verified stack: Yjs + WebSocket + PostgreSQL — used by Linear, Figma [4][5]',
        '• Avoid: OT algorithms (complexity too high for new projects) [6]',
      ],
    },
    {
      icon: 'i-heroicons-scale',
      title: 'Tech Stack Validation',
      prompt: 'Should I use tRPC or GraphQL for my Next.js API? Research trade-offs, performance benchmarks, and community adoption in 2024.',
      result: [
        'Research across 11 sources [1]-[11]:',
        '• tRPC: Type-safe end-to-end, zero schema duplication, fastest for monorepos [1][2]',
        '• GraphQL: Better for public APIs, multiple clients, complex querying [3]',
        '• Verdict: tRPC for internal Next.js apps, GraphQL if you need 3rd-party access [4]',
        '• Benchmark: tRPC ~2.3x faster for simple queries, GraphQL wins on complex nested [5]',
      ],
    },
    {
      icon: 'i-heroicons-bug-ant',
      title: 'Debug with Multi-Source Evidence',
      prompt: "I'm getting 'Module not found: Can't resolve fs' in Next.js 14 app router. Find verified solutions from official docs, GitHub issues, and Stack Overflow.",
      result: [
        'Cross-referenced 8 sources [1]-[8]:',
        '• Root cause: Next.js 14 App Router runs in Edge Runtime by default — fs is Node-only [1]',
        "• Solution A: Add export const runtime = 'nodejs' in route file [2]",
        '• Solution B: Use dynamic import with ssr: false for fs-dependent libs [3][4]',
        '• Verified: 47 GitHub issues closed with Solution A [5]',
      ],
    },
    {
      icon: 'i-heroicons-shield-check',
      title: 'Security & CVE Research',
      prompt: 'Assess the impact of CVE-2024-21529 on our Express.js backend. Find patches, workarounds, and whether our current version is affected.',
      result: [
        'Security analysis from 6 sources [1]-[6]:',
        '• Severity: HIGH (CVSS 7.5) — path traversal in express.static [1]',
        '• Affected: express < 4.19.0 — YOUR VERSION (4.18.2) IS VULNERABLE [2]',
        '• Patch: Upgrade to express@4.19.2 or apply path normalization middleware [3]',
        '• Workaround: Add helmet + strict path validation before static middleware [4]',
      ],
    },
    {
      icon: 'i-heroicons-document-text',
      title: 'Documentation & Academic Writing',
      prompt: 'Write a technical comparison of Raft vs Paxos consensus algorithms with proper citations for our system design document.',
      result: [
        'Synthesized from 9 academic & technical sources [1]-[9]:',
        '• Raft: Easier to understand and implement (Ongaro & Ousterhout, 2014) [1]',
        '• Paxos: Proven correctness, more efficient in theory (Lamport, 1989) [2]',
        '• Production usage: etcd/RabbitMQ use Raft; Chubby/Spanner use Paxos variants [3][4]',
        '• Recommendation: Raft for new systems unless you have formal methods team [5]',
      ],
    },
  ]
})
</script>
