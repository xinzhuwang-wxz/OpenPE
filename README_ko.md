<div align="center">

# OpenPE — 원리에서 종국으로

**LLM 기반 제1원리 인과 분석 프레임워크**

[![License: GPL-3.0](https://img.shields.io/badge/License-GPL%203.0-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-green.svg)](https://python.org)
[![Claude Code](https://img.shields.io/badge/Built%20with-Claude%20Code-orange.svg)](https://claude.ai/claude-code)

[English](README.md) · [中文](README_zh.md) · [한국어](README_ko.md)

</div>

---

모든 사건에는 원인이 있습니다. 모든 원인에는 또 다른 원인이 있습니다. 이것은 하나의 네트워크를 형성합니다 — 선이 아닌 네트워크입니다. 각 노드는 자체 인과 관계 네트워크의 중심입니다.

하지만 이 네트워크는 무한히 확장되지 않습니다. 출발점에서 멀어질수록 설명력은 약해집니다 — 선형이 아닌 곱셈적으로. 어느 시점에서 흔적은 사라집니다. 이 경계는 결함이 아닙니다. 하나의 출발점에서 이해할 수 있는 자연스러운 지평선입니다.

OpenPE는 이 지평선 안에서 작동합니다. 제1원리에서 인과 그래프를 구축하고, 모든 연결을 반박 검증으로 테스트하며, 증거가 뒷받침하는 만큼만 예측합니다 — **원리**에서 **종국**으로.

---

## 빠른 시작

### 방법 1: 수동 설정

```bash
git clone https://github.com/xinzhuwang-wxz/OpenPE.git
cd OpenPE

# pixi 설치 (미설치 시)
curl -fsSL https://pixi.sh/install.sh | bash

# 분석 프로젝트 생성
python src/scaffold_analysis.py analyses/my_analysis
cd analyses/my_analysis

# 설정
# analysis_config.yaml 편집 → question과 domain 설정
pixi install
claude   # orchestrator agent 시작
```

### 방법 2: Claude Code 원클릭 실행

[Claude Code](https://claude.ai/claude-code)에 직접 붙여넣기:

```
Clone https://github.com/xinzhuwang-wxz/OpenPE and use OpenPE's scaffolding + orchestrator flow to complete this analysis: <당신의 질문>
```

Claude Code가 분석 디렉토리를 생성하고, 의존성을 설치하고, 7단계를 모두 자율 실행합니다 — 인과 DAG, 반박 검증, 시나리오 예측, 감사 추적이 포함된 완전한 보고서를 생성합니다.

---

## 작동 방식

```
질문 ─→ 0단계: 발견 ─→ 1단계: 전략 ─→ 2단계: 탐색
          │              │              │
      인과 DAG        방법 선택       EDA + 차트
      데이터 수집     EP 평가        분포 확인
      품질 게이트     체인 계획
          │              │              │
          ▼              ▼              ▼
      3단계: 분석 ─→ 4단계: 예측 ─→ 5단계: 검증
          │              │              │
      인과 검증      몬테카를로 시뮬레이션  독립 재현
      3중 반박 배터리  민감도 분석       EP 전파 감사
      EP 전파        종국 분류         인과 라벨 감사
          │              │              │
          ▼              ▼              ▼
                  6단계: 문서화
                      │
                  분석 보고서 (MD + PDF)
                  감사 추적 (주장 + 출처 + 논리)
                  EP 감쇠 시각화
```

각 단계는 동일한 루프를 따릅니다:

1. **실행** — 서브에이전트가 산출물 생성 (계획 모드로 시작)
2. **검토** — 독립 검토자가 이슈를 A(차단) / B(수정 필요) / C(제안)으로 분류
3. **확인** — 중재자가 통과/반복/회귀 결정
4. **커밋** — STATE.md에 상태 추적
5. **인간 게이트** — 5단계 이후, 최종 보고서 전 인간 승인

---

## 세 가지 핵심 혁신

### 1. 설명력 (EP) — 불확실성 하의 정량적 추론

대부분의 분석 프레임워크는 신뢰도를 이진적으로 처리합니다: "믿는다" 또는 "안 믿는다." OpenPE는 **설명력 (Explanatory Power)** 을 도입합니다 — 인과 체인을 따라 얼마나 많은 설명 가치가 남아있는지 추적하는 연속적이고 곱셈적인 척도입니다.

```
EP = truth × relevance

truth:     이 인과 관계가 실제인지에 대한 확신 (0–1)
relevance: 이 인과 관계가 결과의 분산을 얼마나 설명하는지 (0–1)
```

인과 체인 A → B → C → D를 따라, **Joint EP는 곱셈적으로 감쇠**합니다:

```
Joint_EP = EP(A→B) × EP(B→C) × EP(C→D)
```

이는 심오한 결과를 가져옵니다: 긴 인과 체인은 자연스럽게 설명력을 잃습니다. 각 엣지가 EP=0.7인 5링크 체인의 Joint_EP는 0.17 — 소프트 절단 임계값을 간신히 넘는 수준입니다. 프레임워크는 명시적 중단 규칙을 적용합니다:

| 임계값 | Joint EP | 행동 |
|--------|----------|------|
| **하드 절단** | < 0.05 | 탐색 중단. 이 체인은 분석 지평선을 넘었습니다. |
| **소프트 절단** | < 0.15 | 경량 평가만. 서브체인 확장 없음. |
| **서브체인 확장** | > 0.30 | 상세 조사 가치 있음. 서브분석 생성. |

EP 값은 분석 생명주기에 걸쳐 진화합니다. 분석 전 라벨 (`LITERATURE_SUPPORTED` → truth=0.70, `THEORIZED` → 0.40, `SPECULATIVE` → 0.15)은 3단계 반박 검증을 통해 분석 후 분류로 업데이트됩니다 (`DATA_SUPPORTED` → 0.85, `CORRELATION` → 0.50, `HYPOTHESIZED` → 0.15, `DISPUTED` → 0.30).

**왜 중요한가:** EP는 분석 신뢰도의 감쇠를 가시적이고 정량적으로 만듭니다. 산문에 불확실성을 숨기는 대신, 모든 인과 논증은 독자가 추적하고 도전할 수 있는 숫자를 가집니다.

### 2. 위약 기반 모순 탐지 (DISPUTED 분류)

표준 인과 추론은 반박 결과를 스코어카드로 취급합니다: 더 많은 테스트 통과 → 더 강한 증거. OpenPE는 증거 패턴에서 **논리적 모순**을 탐지하는 의미론적 레이어를 추가합니다.

모든 인과 엣지는 세 가지 반박 검증을 거칩니다:
- **위약 검증** — 처리 변수를 랜덤 변수로 대체; 효과가 사라져야 함
- **랜덤 공통 원인 검증** — 랜덤 혼란 변수 추가; 추정값이 안정적이어야 함
- **데이터 부분집합 검증** — 랜덤 80% 부분집합으로 추정; 일관적이어야 함

분류는 **위약을 인과적 앵커**로 사용합니다:

- 위약이 **통과**하면 (효과가 처리 특이적 / "실제"), 부분집합과 공통원인 검증 실패는 모순 — 실제 효과는 안정적이고 강건해야 합니다
- 위약이 **실패**하면 (효과가 처리 특이적이지 않음), 부분집합 통과는 모순 — 비실제 효과는 완벽하게 안정적일 수 없습니다

이러한 모순이 탐지되면, 엣지는 `DISPUTED`로 분류됩니다 — DATA_SUPPORTED도 CORRELATION도 아닌, 인간 검토를 위한 플래그입니다. 프레임워크는 모순된 증거를 자동 분류하기를 거부합니다.

```python
# 모순 탐지 로직 (Scheme C)
if placebo_passed and (not subset_passed or not cc_passed):
    return "DISPUTED"   # 실제이지만 불안정/혼란 — 모순
if not placebo_passed and subset_passed:
    return "DISPUTED"   # 비실제이지만 완벽히 안정 — 모순
```

**왜 중요한가:** 대부분의 프레임워크는 증거가 자체 모순되더라도 분류를 강제합니다. DISPUTED는 일부 패턴에 깔끔한 답이 없음을 인정하고 — 알고리즘적 추측 대신 인간 판단으로 라우팅합니다.

### 3. 증거 기반 계층 전환을 가진 교차 분석 메모리

OpenPE 분석은 제로에서 시작하지 않습니다. 계층화된 메모리 시스템이 분석 간 도메인 지식을 축적하며, 신뢰도 기반 생명주기를 관리합니다:

| 계층 | 범위 | 로딩 | 내용 |
|------|------|------|------|
| **L0** | 보편적 | 항상 로드 | ≥3회 분석으로 검증된 교차 도메인 원칙 |
| **L1** | 도메인 | 매칭 도메인 시 로드 | 도메인 특화 경험 (방법, 데이터 소스, 실패 교훈) |
| **L2** | 상세 | 요청 시 | 전체 분석 요약 (자동 생성) |

메모리는 정적이지 않습니다. 진화합니다:

```
생성 (L1, 신뢰도=0.50)
  → 2차 분석에서 확증 (+0.15 → 0.65)
  → 3차 분석에서 확증 (+0.15 → 0.80) → L0로 승급
  → 4차 분석에서 반박 (-0.25 → 0.55)
  → 5차 분석에서 반박 (-0.25 → 0.30) → L1로 강등
  → 시간에 따라 감쇠 (분석당 -0.01)
  → 최종: 신뢰도 < 0.05 AND 활성도 < 0.01 → 망각 (삭제)
```

생명주기는 `commit_session()`에서 완전 자동화됩니다:
- **승급** (L1→L0): ≥2회 독립 확증
- **강등** (L0→L1): 신뢰도 0.30 미만으로 하락
- **망각**: 신뢰도 ≤ 0.05 AND 활성도 < 0.01 → 파일 삭제
- **보관**: 차가운 L2 항목 (활성도 < 0.1) → `_archive/`로 이동
- **멱등 커밋**: 마커 파일이 충돌 후 재시작 시 이중 감쇠 방지

글로벌 메모리는 저장소 루트 (`memory/`)에 있습니다. 새 분석은 스캐폴딩을 통해 스냅샷을 상속하고, 완료 후 높은 신뢰도의 발견을 다시 글로벌로 프로모션합니다.

**왜 중요한가:** 같은 도메인의 세 번째 분석은 첫 번째보다 낫습니다 — 코드가 개선되어서가 아니라, 메모리 시스템이 무엇이 효과적이고 무엇이 아닌지 학습했기 때문입니다.

---

## 차용한 기반 기술

OpenPE는 세 가지 주목할 만한 프로젝트의 아이디어를 차용하여 제1원리 분석 맥락에 맞게 적용했습니다:

### ACG Protocol → 감사 추적 (IGM/SSR/VAR)

[ACG Protocol](https://github.com/Kos-M/acg_protocol)은 인라인 근거 마커와 소스 검증 레지스트리를 도입했습니다. OpenPE는 이를 3층 감사 추적으로 적용합니다:

- **IGM** (인라인 근거 마커): `[C1:a1b2c3d4e5:phase3/data.csv:row42]` — 모든 주장이 소스에 연결되는 해시를 내장
- **SSR** (구조화 소스 레지스트리): SHA-256 해시, 소스 유형, 데이터셋별 검증 상태
- **VAR** (진실성 감사 레지스트리): `verify_logic()`를 통한 자동 일관성 검사로 추론 논리 체인 추적

### Graphiti → 시간적 인과 지식 그래프

[Graphiti](https://github.com/getzep/graphiti)의 시간적 EntityEdge 모델이 OpenPE 인과 지식 그래프의 유효성 윈도우 패턴에 영감을 주었습니다. 관계는 `valid_at`/`invalid_at`/`expired_at` 타임스탬프를 가지며, 인과 메커니즘이 참인지 *여부*뿐 아니라 *언제* 참이었는지 기록할 수 있습니다. 신뢰도 기반 재사용 정책 (SKIP / LIGHTWEIGHT_VERIFY / MUST_RETEST)과 결합하여 높은 신뢰도의 관계는 향후 분석에서 재검증을 건너뛸 수 있습니다.

### OpenViking → 메모리 활성도 평가

[OpenViking](https://github.com/volcengine/OpenViking)의 메모리 생명주기 시스템이 활성도 평가 공식을 제공했습니다: `sigmoid(빈도) × 지수감쇠(최근성)`. OpenPE는 이를 사용하여 활발히 사용되는 메모리와 부실한 메모리를 구별하고, 메모리 시스템을 유한하게 유지하는 보관 및 망각 메커니즘을 구동합니다.

---

## 프로젝트 구조

```
OpenPE/
├── src/
│   ├── scaffold_analysis.py    # 분석 디렉토리 생성
│   ├── templates/              # CLAUDE.md 템플릿 + 공유 스크립트
│   │   ├── scripts/            # EP 엔진, 인과 파이프라인, 메모리 저장소...
│   │   └── report_template/    # 전문 PDF 스타일링
│   ├── methodology/            # 사양 문서 (01-09 + 부록)
│   ├── conventions/            # 도메인 지식 (인과 추론, 시계열, 패널 분석)
│   └── orchestration/          # 세션 관리 사양
├── .claude/
│   ├── agents/                 # 에이전트 프로필 정의 (15+ 전문 에이전트)
│   ├── hooks/                  # 분석 격리 샌드박스
│   └── skills/                 # 분석 파이프라인 스킬
├── CLAUDE.md                   # 프로젝트 수준 지침
├── pyproject.toml              # 루트 pixi 설정
└── LICENSE                     # GPL-3.0
```

분석 스캐폴딩 시:

```
analyses/my_analysis/           # 독립 git 저장소
├── CLAUDE.md                   # Orchestrator 프로토콜 (자체 완결)
├── analysis_config.yaml        # 질문, 도메인, EP 임계값
├── STATE.md                    # 파이프라인 상태 (단계, 반복, 차단)
├── pixi.toml                   # 환경 + 태스크 그래프
├── scripts/                    # 공유 모듈 (템플릿에서 복사)
├── memory/                     # L0/L1/L2/causal_graph
├── conventions/ → src/conventions  # 심볼릭 링크
├── methodology/ → src/methodology  # 심볼릭 링크
└── phase{0..6}_*/
    ├── CLAUDE.md               # 단계별 지침
    ├── exec/                   # 산출물 (DISCOVERY.md, ANALYSIS.md, ...)
    ├── scripts/                # 단계별 코드
    ├── figures/                # PDF + PNG 차트
    └── review/                 # REVIEW_NOTES.md
```

---

## 입력 모드

| 모드 | 시나리오 | 동작 |
|------|---------|------|
| **A** — 질문만 | 데이터 미제공 | 완전 자율: 가설, 데이터 수집, 품질 게이트 |
| **B** — 질문 + 데이터 | 사용자 데이터셋 제공 | 사용자 데이터는 수집 데이터와 동일한 품질 게이트 통과 |
| **C** — 질문 + 가설 | 사용자 인과 가설 제공 | 사용자 가설은 후보 DAG 중 하나 — 신뢰 특권 없음 |

---

## 요구사항

- **Python** ≥ 3.11
- **[pixi](https://pixi.sh)** — 의존성 관리 (나머지 모두 설치)
- **[Claude Code](https://claude.ai/claude-code)** — LLM orchestrator
- **pandoc** ≥ 3.0 + xelatex — PDF 생성 (pixi를 통해 설치)

---

## 감사의 말

OpenPE는 [slop-X](https://github.com/jfc-mit/slop-X)에서 시작되었으며 이를 모든 도메인으로 일반화합니다.

다음 오픈소스 프로젝트에서도 영감을 받고 패턴을 적용했습니다:

| 프로젝트 | 차용한 내용 | 라이선스 |
|---------|------------|---------|
| [ACG Protocol](https://github.com/Kos-M/acg_protocol) | UGVP 사실 근거 (IGM/SSR/VAR 감사 구조) | — |
| [Graphiti](https://github.com/getzep/graphiti) | 지식 그래프의 시간적 EntityEdge 유효성 모델 | Apache-2.0 |
| [OpenViking](https://github.com/volcengine/OpenViking) | 메모리 생명주기 활성도 평가 (`sigmoid × recency`) | Apache-2.0 |
| [Causica](https://github.com/microsoft/causica) | 그래프 평가 메트릭 패턴 | MIT |
| [causal-learn](https://github.com/py-why/causal-learn) | 인과 구조 발견을 위한 PC 알고리즘 | MIT |
| [DoWhy](https://github.com/py-why/dowhy) | 인과 추론 + 반박 검증 프레임워크 | MIT |
| [DeerFlow](https://github.com/bytedance/deer-flow) | 멀티 에이전트 오케스트레이션 패턴 | MIT |

개발 워크플로우는 [Superpowers](https://github.com/cline/superpowers-marketplace) Claude Code 스킬로 구동되었습니다 — 특히 `writing-plans`, `subagent-driven-development`, `test-driven-development`, `code-reviewer`.

---

## 라이선스

[GPL-3.0](LICENSE) — 자유롭게 사용, 수정, 배포 가능. 파생 작품도 GPL-3.0으로 오픈소스해야 합니다.
