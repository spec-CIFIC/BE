from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


# ==================== 요청/응답 DTO ====================

# ===== SUBJECT (과목) =====
class SubjectBase(BaseModel):
    subjectName: str


class SubjectCreate(SubjectBase):
    pass


class SubjectResponse(SubjectBase):
    id: int

    class Config:
        from_attributes = True


# ===== CONCEPT (개념) =====
class ConceptBase(BaseModel):
    subjectId: int
    conceptName: str


class ConceptCreate(ConceptBase):
    pass


class ConceptResponse(ConceptBase):
    id: int

    class Config:
        from_attributes = True


# ===== QUESTIONS (문제) =====
class QuestionsBase(BaseModel):
    subjectId: int
    conceptId: int
    stem: str
    choices: list[str]
    answerIndex: int
    explanation: Optional[str] = None


class QuestionsCreate(QuestionsBase):
    pass


class QuestionsResponse(QuestionsBase):
    id: int
    createdAt: datetime

    class Config:
        from_attributes = True


# ===== USER (사용자) =====
class UserBase(BaseModel):
    email: EmailStr
    name: str
    subjectId: Optional[int] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    subjectId: Optional[int] = None


class UserResponse(UserBase):
    id: int
    provider: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


# ===== ANON_SESSION (익명 세션) =====
class AnonSessionCreate(BaseModel):
    pass


class AnonSessionResponse(BaseModel):
    id: int
    sessionToken: str
    createdAt: datetime
    expiresAt: datetime
    mergedUserId: Optional[int] = None

    class Config:
        from_attributes = True


# ===== ATTEMPT (풀이 기록) =====
class AttemptBase(BaseModel):
    questionId: int
    selectedIndex: int
    durationMs: Optional[int] = None


class AttemptCreate(AttemptBase):
    userId: Optional[int] = None
    anonSessionId: Optional[int] = None


class AttemptResponse(AttemptBase):
    id: int
    userId: Optional[int] = None
    anonSessionId: Optional[int] = None
    isCorrect: bool
    createdAt: datetime

    class Config:
        from_attributes = True


# ===== MASTERY (숙련도) =====
class MasteryBase(BaseModel):
    userId: int
    conceptId: int
    score: float
    sampleSize: int


class MasteryCreate(MasteryBase):
    pass


class MasteryResponse(MasteryBase):
    id: int
    updatedAt: datetime

    class Config:
        from_attributes = True


# ===== WRONGNOTE (오답노트) =====
class WrongnoteBase(BaseModel):
    userId: int
    attemptId: int
    conceptId: int
    mistakeType: Optional[str] = None
    userMemo: Optional[str] = None
    reviewDueAt: Optional[datetime] = None


class WrongnoteCreate(WrongnoteBase):
    pass


class WrongnoteResponse(WrongnoteBase):
    id: int

    class Config:
        from_attributes = True


# ===== API 통합 응답 DTO =====
class QuestionWithAttemptResponse(BaseModel):
    """문제 풀이 응답"""
    id: int
    stem: str
    choices: list[str]
    answerIndex: int
    explanation: Optional[str]
    isCorrect: bool
    attemptId: int
    durationMs: Optional[int]

    class Config:
        from_attributes = True


class UserProgressResponse(BaseModel):
    """사용자 진도 조회 응답"""
    userId: int
    subjectId: int
    totalAttempts: int
    correctCount: int
    masteryScores: dict[int, float]  # conceptId: score

    class Config:
        from_attributes = True


class WrongnoteDetailResponse(BaseModel):
    """오답노트 상세 조회 응답"""
    wrongnoteId: int
    questionId: int
    stem: str
    userAnswer: int
    correctAnswer: int
    mistakeType: Optional[str]
    userMemo: Optional[str]
    reviewDueAt: Optional[datetime]
    concept: ConceptResponse

    class Config:
        from_attributes = True
