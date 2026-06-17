# 조직 표준 이슈 라벨 / 타입

ocolabs 조직 전체 레포의 이슈 **라벨**과 **타입**을 표준화한다. 신규 레포에도 자동 적용된다.

## 라벨 (13종)

`standard-labels.json`이 SSOT다. 색상/설명 기준은 `arca-client`.

| 라벨 | 용도 |
|------|------|
| 버그 | 문제 발생했을 때 바로 대응 |
| 기능 개선 | 기존 기능을 더 나은 방향으로 |
| UI/UX 개선 | 화면/경험 개선 |
| API 생성 | GET/POST API 생성 |
| API 연동 | 외부 API 또는 내부 백엔드 연동 |
| 데이터베이스 | DB 생성/변경 |
| 문서 업데이트 | 문서 보완·정리 |
| 설계 | 설계 문서 작성/변경 |
| 리팩토링 | 코드 구조 개선 (기능 변경 없음) |
| 테스트 | 테스트 코드 추가/수정 |
| 성능 개선 | 속도/리소스 최적화 |
| 인프라 | CI/CD, 배포, 환경 설정 |
| 중복 | 이미 등록된 이슈 있음 |

### 동기화 동작 (`scripts/sync-labels.py`)

- **비파괴**다. GitHub 기본 라벨(`bug`, `enhancement`, …)과 알려진 변형(`버그 발견`, `기획 필요`, …)을 표준명으로 **rename**(이슈 연결 보존, 대상 라벨이 없을 때만)하고, 누락 표준 라벨을 **생성**하며, 색/설명을 **통일**한다.
- 프로젝트 전용 라벨(`epic:`, `priority:`, `phase:`, …)은 **건드리지 않는다**.
- 비보관 org 레포 전체를 동적 대상화 → **신규 레포 자동 포함**.
- 특정 레포 제외: `standard-labels.json`의 `exclude_repos`에 추가.
- 라벨/색/매핑 변경: `standard-labels.json`만 수정하면 다음 동기화에 반영.

### 자동화 (`.github/workflows/label-sync.yml`)

- 매일 09:00 KST cron + 수동 실행(`workflow_dispatch`, dry-run 옵션 제공).
- **선행 설정(1회)**: org 레포 라벨 쓰기 토큰을 이 레포의 Actions 시크릿 `ORG_LABEL_SYNC_TOKEN`으로 추가.
  - classic PAT `scope: repo`, 또는 fine-grained PAT(`Issues: Read and write`, `Metadata: Read`, 대상=org 전체 레포).
  - 기본 `GITHUB_TOKEN`은 자기 레포만 수정 가능 → 타 레포 동기화 불가.
- 로컬 실행: `GH_TOKEN=... python3 scripts/sync-labels.py [--apply]`

## 타입 (org Issue Types, 5종)

`버그 / 기능 / 개선 / 작업 / 문서`. **org 레벨 정의라 모든 레포(신규 포함)에 자동 노출**되므로 동기화 워크플로가 필요 없다. 변경은 org Settings 또는 API(`PUT/POST /orgs/{org}/issue-types`, `admin:org` 필요)로 한다.

라벨↔타입 권장 매핑: 버그→버그 / 기능 개선→기능 / (UI/UX 개선·리팩토링·성능 개선)→개선 / (API 생성·API 연동·데이터베이스·테스트·인프라·설계)→작업 / 문서 업데이트→문서.
