# app/models/orm.py
# 역할: SQLAlchemy ORM 모델 정의 (DB 테이블과 1:1 매핑)
# Spring의 @Entity 클래스들에 해당합니다.
#
# [schemas.py vs orm.py 구분]
# - schemas.py : HTTP 요청/응답 데이터의 형태를 정의 (Pydantic, 외부용)
# - orm.py     : 실제 DB 테이블 구조를 정의 (SQLAlchemy, 내부용)
# 둘은 역할이 다르므로 분리합니다.

from datetime import datetime, timezone

from sqlalchemy import JSON, BigInteger, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


# ─────────────────────────────────────────────────────────────
# SUBJECT (과목)
# ─────────────────────────────────────────────────────────────
class Subject(Base):
    # __tablename__ : 실제 DB에 생성될 테이블 이름
    # Spring의 @Table(name = "SUBJECT")에 해당합니다.
    __tablename__ = "SUBJECT"

    # --- 컬럼 정의 ---
    # Column(타입, 옵션...) 형태로 정의합니다.
    # Spring의 @Column 어노테이션에 해당합니다.

    # primary_key=True  : PK 지정 (@Id)
    # autoincrement=True: 자동 증가 (@GeneratedValue(strategy=IDENTITY))
    id = Column(BigInteger, primary_key=True, autoincrement=True)

    subjectName = Column(String(50), nullable=False)

    # --- 관계(Relationship) 정의 ---
    # Spring의 @OneToMany(mappedBy = "subject")에 해당합니다.
    # "Concept" : 연결할 ORM 클래스 이름 (문자열로 작성 → 순환 참조 방지)
    # back_populates : 반대편 모델에서 이 관계를 참조할 속성 이름과 연결
    # lazy="selectin" : 부모 객체를 조회할 때 자식 목록도 자동으로 SELECT해서 로드합니다.
    #                   비동기 환경에서는 기본 lazy 로딩이 동작하지 않으므로 반드시 지정해야 합니다.
    concepts = relationship("Concept", back_populates="subject", lazy="selectin")
    questions = relationship("Questions", back_populates="subject", lazy="selectin")
    users = relationship("User", back_populates="subject", lazy="selectin")


# ─────────────────────────────────────────────────────────────
# CONCEPT (개념)
# ─────────────────────────────────────────────────────────────
class Concept(Base):
    __tablename__ = "CONCEPT"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # ForeignKey("테이블명.컬럼명") : FK 제약 조건을 걸어 참조 무결성을 보장합니다.
    # Spring의 @ManyToOne + @JoinColumn(name = "subjectId")에 해당합니다.
    subjectId = Column(BigInteger, ForeignKey("SUBJECT.id"), nullable=False)

    conceptName = Column(String(100), nullable=False)

    # back_populates="concepts" : Subject 모델의 concepts 속성과 양방향으로 연결
    # Spring의 @ManyToOne(fetch = FetchType.LAZY)에 해당합니다.
    subject = relationship("Subject", back_populates="concepts")
    questions = relationship("Questions", back_populates="concept", lazy="selectin")
    masteries = relationship("Mastery", back_populates="concept", lazy="selectin")
    wrongnotes = relationship("Wrongnote", back_populates="concept", lazy="selectin")


# ─────────────────────────────────────────────────────────────
# QUESTIONS (문제)
# ─────────────────────────────────────────────────────────────
class Questions(Base):
    __tablename__ = "QUESTIONS"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    subjectId = Column(BigInteger, ForeignKey("SUBJECT.id"), nullable=False)
    conceptId = Column(BigInteger, ForeignKey("CONCEPT.id"), nullable=False)

    # Text : 길이 제한 없는 긴 문자열 (문제 본문)
    stem = Column(Text, nullable=False)

    # JSON : 파이썬 list[str]을 DB에 JSON 문자열로 저장/불러옵니다.
    # SQLite는 네이티브 JSON 타입이 없지만 SQLAlchemy가 직렬화/역직렬화를 대신 처리합니다.
    choices = Column(JSON, nullable=False)

    answerIndex = Column(Integer, nullable=False)
    explanation = Column(Text, nullable=True)

    # 검증 파이프라인 결과. 생성 직후 PENDING, 5단계 통과 시 APPROVED.
    # PENDING / APPROVED / HUMAN_REVIEW / REJECTED
    status = Column(String(20), nullable=False, default="PENDING")

    # 검증 파이프라인 종합 신뢰도 점수 (0.0~1.0). 라우팅 기준값.
    trustScore = Column(Float, nullable=True)

    # default=lambda: datetime.now(timezone.utc) : INSERT 시 현재 시각을 자동으로 채웁니다.
    # Spring의 @CreationTimestamp에 해당합니다.
    createdAt = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    subject = relationship("Subject", back_populates="questions")
    concept = relationship("Concept", back_populates="questions")
    attempts = relationship("Attempt", back_populates="question", lazy="selectin")


# ─────────────────────────────────────────────────────────────
# USER (사용자)
# ─────────────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "USER"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # Supabase Auth의 auth.users.id (UUID). 로그인 시 유저 식별에 사용.
    supabase_uid = Column(String(36), unique=True, nullable=True)

    email = Column(String(100), unique=True, nullable=False)

    # nullable=True : 소셜 로그인 사용자는 비밀번호가 없으므로 null 허용
    password = Column(String(255), nullable=True)
    name = Column(String(50), nullable=False)

    # provider : 'LOCAL' / 'GOOGLE' / 'KAKAO' 등
    provider = Column(String(20), nullable=True)
    subjectId = Column(BigInteger, ForeignKey("SUBJECT.id"), nullable=True)

    createdAt = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # onupdate=lambda: datetime.now(timezone.utc) : UPDATE 시 현재 시각으로 자동 갱신됩니다.
    # Spring의 @UpdateTimestamp에 해당합니다.
    updatedAt = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    subject = relationship("Subject", back_populates="users")
    attempts = relationship("Attempt", back_populates="user", lazy="selectin")
    masteries = relationship("Mastery", back_populates="user", lazy="selectin")
    wrongnotes = relationship("Wrongnote", back_populates="user", lazy="selectin")


# ─────────────────────────────────────────────────────────────
# ANON_SESSION (익명 세션)
# ─────────────────────────────────────────────────────────────
class AnonSession(Base):
    __tablename__ = "ANON_SESSION"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # unique=True : 같은 토큰이 두 개 존재하면 안 되므로 유니크 제약
    sessionToken = Column(String(100), unique=True, nullable=False)
    createdAt = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    expiresAt = Column(DateTime, nullable=False)

    # 로그인 시 이 익명 세션을 병합할 유저를 가리키는 FK.
    # nullable=True : 아직 로그인 전이면 null입니다.
    mergedUserId = Column(BigInteger, ForeignKey("USER.id"), nullable=True)

    # foreign_keys=[mergedUserId] :
    #   AnonSession → User 방향의 FK가 여러 개 생길 가능성에 대비해 명시합니다.
    #   SQLAlchemy가 어떤 FK를 기준으로 조인할지 혼동하지 않도록 지정합니다.
    merged_user = relationship("User", foreign_keys=[mergedUserId])
    attempts = relationship("Attempt", back_populates="anon_session", lazy="selectin")


# ─────────────────────────────────────────────────────────────
# ATTEMPT (풀이 기록)
# ─────────────────────────────────────────────────────────────
class Attempt(Base):
    __tablename__ = "ATTEMPT"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # userId, anonSessionId 중 하나만 채워집니다 (ERD 설계 결정).
    # 로그인 사용자 → userId만 채움, anonSessionId는 null
    # 익명 사용자   → anonSessionId만 채움, userId는 null
    userId = Column(BigInteger, ForeignKey("USER.id"), nullable=True)
    anonSessionId = Column(BigInteger, ForeignKey("ANON_SESSION.id"), nullable=True)

    questionId = Column(BigInteger, ForeignKey("QUESTIONS.id"), nullable=False)
    selectedIndex = Column(Integer, nullable=False)
    isCorrect = Column(Boolean, nullable=False)

    # nullable=True : 소요 시간을 측정하지 않은 경우 null 허용
    durationMs = Column(Integer, nullable=True)
    createdAt = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="attempts", foreign_keys=[userId])
    anon_session = relationship("AnonSession", back_populates="attempts", foreign_keys=[anonSessionId])
    question = relationship("Questions", back_populates="attempts")
    wrongnotes = relationship("Wrongnote", back_populates="attempt", lazy="selectin")


# ─────────────────────────────────────────────────────────────
# MASTERY (숙련도)
# ─────────────────────────────────────────────────────────────
class Mastery(Base):
    __tablename__ = "MASTERY"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    userId = Column(BigInteger, ForeignKey("USER.id"), nullable=False)
    conceptId = Column(BigInteger, ForeignKey("CONCEPT.id"), nullable=False)

    # Float : 0.0 ~ 1.0 사이의 숙련도 점수
    score = Column(Float, nullable=False)

    # 진단 신뢰도 계산에 사용하는 표본 수 (풀이 기록 누적 횟수)
    sampleSize = Column(Integer, nullable=False)

    updatedAt = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="masteries")
    concept = relationship("Concept", back_populates="masteries")


# ─────────────────────────────────────────────────────────────
# WRONGNOTE (오답노트)
# ─────────────────────────────────────────────────────────────
class Wrongnote(Base):
    __tablename__ = "WRONGNOTE"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    userId = Column(BigInteger, ForeignKey("USER.id"), nullable=False)
    attemptId = Column(BigInteger, ForeignKey("ATTEMPT.id"), nullable=False)
    conceptId = Column(BigInteger, ForeignKey("CONCEPT.id"), nullable=False)

    # AI가 판정한 실수 유형 (예: "잔존가치_누락", "이자율_혼동" 등)
    mistakeType = Column(Text, nullable=True)

    # 사용자가 직접 작성하는 자유 메모
    userMemo = Column(Text, nullable=True)

    # 간격 반복 학습을 위한 복습 예정 시각
    reviewDueAt = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="wrongnotes")
    attempt = relationship("Attempt", back_populates="wrongnotes")
    concept = relationship("Concept", back_populates="wrongnotes")
