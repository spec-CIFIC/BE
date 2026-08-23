# 스키마 관리 규칙

Supabase + Alembic 기반 스키마 변경 절차 및 이력.

> 스키마 변경은 반드시 아래 순서를 따른다. Supabase 대시보드에서 직접 테이블/컬럼을 추가하지 않는다.

## 변경 절차

1. **`app/models/orm.py` 수정** — ORM 모델에 컬럼/테이블 추가·수정
2. **`docs/ERD/MVP_ERD.md` 동기화** — DBML과 관련 섹션 업데이트
3. **마이그레이션 파일 생성**
   ```bash
   alembic revision --autogenerate -m "변경 내용 설명"
   ```
4. **마이그레이션 적용**
   ```bash
   alembic upgrade head
   ```
5. **이 문서(SCHEMA_MANAGEMENT.md) 마이그레이션 이력 업데이트**
6. **Supabase 대시보드 Table Editor에서 결과 확인**

## 롤백 방법

```bash
# 한 단계 되돌리기
alembic downgrade -1

# 특정 버전으로 되돌리기
alembic downgrade <revision_id>
```

## 마이그레이션 이력

| 파일 | 내용 |
|---|---|
| `c0b1684d857f_init_tables.py` | 초기 8개 테이블 생성 |
| `9a423ea7e48c_add_supabase_uid_to_user_nullable_.py` | USER.supabase_uid 추가, USER.subjectId nullable 변경 |
| `bc2f51645b18_add_self_diagnosis_to_anon_session.py` | ANON_SESSION.self_diagnosis JSON 컬럼 추가 (입문자 자가진단 저장) |
| `953a90357d89_user_subjectid_not_null.py` | USER.subjectId NOT NULL 변경 (회원가입 시 과목 필수 선택) |
| `7dc2f2c87fa4_alter_datetime_columns_to_timestamptz.py` | 전체 datetime 컬럼 TIMESTAMP → TIMESTAMPTZ 변경 (timezone-aware 저장) |
| `a1b2c3d4e5f6_add_subject_to_anon_session.py` | ANON_SESSION.subjectId 추가 (입문자 과목 선택 선행 단계 저장, FK→SUBJECT, nullable) |
| `ccc6193aa22a_add_home_fields_to_user_and_question_type.py` | USER에 examName·examDate·streakCount·lastStudiedAt 추가, QUESTIONS에 questionType 추가 (홈화면 D-Day·streak·문제 유형 필터용) |
| `faa3eb159683_refactor_question_type_add_is_ai_generated.py` | questionType 값 정리(GENERATED→CALCULATION, PAST_EXAM→CALCULATION), isAiGenerated Boolean 컬럼 추가 (문제 형식과 출처를 분리) |

## 주의 사항

- Supabase 대시보드에서 직접 스키마를 바꾸면 `orm.py`와 불일치가 생긴다. **반드시 코드 → DB 방향으로만 변경한다.**
- 컬럼 삭제·이름 변경은 `--autogenerate`가 감지하지 못하는 경우가 있다. 마이그레이션 파일 생성 후 내용을 직접 확인한다.
- 운영 DB에 `upgrade` 전에 마이그레이션 파일 내용을 반드시 검토한다.
