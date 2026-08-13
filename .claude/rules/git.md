# Git 협업 규칙

## 브랜치 전략

```
main
 └── dev
      ├── feat/{도메인}       # 새 기능 (엔드포인트·도메인 단위)
      ├── refactor/{범위}     # 구조 변경 (동작 변화 없음)
      └── fix/{도메인}        # 버그 수정
```

- `main`: 버전 마일스톤(v0 완료 등) 시점에만 dev에서 머지
- `dev`: 기능 브랜치들을 모으는 통합 브랜치. PR은 여기로.
- `feat/{도메인}`: 도메인 단위 기능 개발 (예: `feat/questions`, `feat/attempts`)
- `refactor/{범위}`: 계층 분리·파일 구조 등 구조 개선 (예: `refactor/layered-arch`)
- `fix/{도메인}`: 버그 수정 (예: `fix/auth-token`)

### 브랜치 생성 원칙

작업 시작 전 **반드시 현재 브랜치를 확인**하고, 작업 성격에 맞는 브랜치를 새로 딴다.
기존 브랜치의 작업 범위와 다른 내용을 같은 브랜치에 커밋하지 않는다.

## 커밋 컨벤션

| 유형 | 의미 | 예시 |
|---|---|---|
| `feat` | 새 엔드포인트·기능 추가 | `feat: POST /attempts 풀이 제출 API 추가` |
| `fix` | 버그 수정 | `fix: 신규 유저 subjectId null 처리 누락` |
| `refactor` | 동작 변경 없는 구조 개선 | `refactor: router-service-repository 3계층 분리` |
| `docs` | ERD, 문서 수정 | `docs: MVP ERD attempts 테이블 반영` |
| `chore` | 설정·의존성·플랜 파일 | `chore: .claude/plans v0 단계 플랜 추가` |
| `test` | 테스트 코드 추가 | |
| `!HOTFIX` | 치명적 버그 긴급 수정 | |

- 커밋 제목은 **한국어**. 제목 50자 이내, 끝에 `.` 금지.
- 본문은 한국어.
- 태그: `v{MAJOR}.{MINOR}.{PATCH}` (예: `v0.1.0`)

## 커밋 & Push 절차 (반드시 준수)

1. **현재 브랜치 확인** — 작업 성격과 브랜치가 일치하는지 먼저 확인한다.
2. 커밋 전에 **제목 + Description을 먼저 제시하고 승인을 받는다.**
3. 승인 후 커밋 및 push 진행.
4. 이미 push된 커밋 수정 시(--amend, rebase 등) **force push 전에 명시적으로 알린다.**

## 스키마 변경 규칙

`app/models/orm.py` 수정 + Alembic 마이그레이션 생성·적용 시 반드시 함께 처리한다.

1. **`docs/ERD/MVP_ERD.md` 동기화** — DBML 반영
2. **`docs/ERD/SCHEMA_MANAGEMENT.md` 마이그레이션 이력 업데이트**
3. **순서**: orm.py 수정 → 마이그레이션 생성·적용 → docs 동기화
