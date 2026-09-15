from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


# ===== SUBJECT (과목) =====

class SubjectBase(BaseModel):
    subjectName: str


class SubjectCreate(SubjectBase):
    pass


class SubjectResponse(SubjectBase):
    id: int
    questionCount: int = 0

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


class ConceptListItem(BaseModel):
    """GET /concepts — 단원학습 개념 목록 항목"""
    conceptId: int
    conceptName: str
    isStudyPlan: bool


# ===== QUESTIONS (문제) =====

class QuestionsBase(BaseModel):
    subjectId: int
    conceptId: int
    stem: str
    choices: list[str]
    answerIndex: int
    explanation: Optional[str] = None
    questionType: str = "CALCULATION"
    isAiGenerated: bool = True


class QuestionsCreate(QuestionsBase):
    pass


class QuestionsResponse(QuestionsBase):
    id: int
    createdAt: datetime

    class Config:
        from_attributes = True


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


# ===== USER (사용자) =====

class UserBase(BaseModel):
    email: EmailStr
    name: str
    subjectId: int


class UserCreate(UserBase):
    password: str


class RegisterRequest(BaseModel):
    subjectId: int


class UserUpdate(BaseModel):
    name: Optional[str] = None
    subjectId: Optional[int] = None
    examName: Optional[str] = None
    examDate: Optional[date] = None


class UserResponse(UserBase):
    id: int
    provider: Optional[str] = None
    examName: Optional[str] = None
    examDate: Optional[date] = None
    streakCount: int = 0
    weeklyAttemptCount: int = 0
    studyDays: int = 0
    createdAt: datetime
    updatedAt: datetime

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


class AttemptHistoryQuestionSummary(BaseModel):
    id: int
    stemPreview: str


class AttemptHistoryQuestionDetail(BaseModel):
    id: int
    stem: str
    choices: list[str]
    answerIndex: int
    explanation: Optional[str]


class AttemptHistoryConceptSummary(BaseModel):
    id: int
    conceptName: str


class AttemptHistorySubjectSummary(BaseModel):
    id: int
    subjectName: str


class AttemptHistoryItem(BaseModel):
    """GET /attempts — 학습 기록 목록 항목"""
    attemptId: int
    isCorrect: bool
    durationMs: Optional[int]
    createdAt: datetime
    question: AttemptHistoryQuestionSummary
    concept: AttemptHistoryConceptSummary
    subject: AttemptHistorySubjectSummary


class AttemptHistoryListResponse(BaseModel):
    """GET /attempts — 페이지네이션 메타 포함"""
    items: list[AttemptHistoryItem]
    total: int
    limit: int
    offset: int


class AttemptHistoryDetail(BaseModel):
    """GET /attempts/{attempt_id} — 학습 기록 상세"""
    attemptId: int
    isCorrect: bool
    durationMs: Optional[int]
    selectedIndex: int
    createdAt: datetime
    question: AttemptHistoryQuestionDetail
    concept: AttemptHistoryConceptSummary
    subject: AttemptHistorySubjectSummary


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
    questionId: int
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


class ReviewWrongnoteItem(BaseModel):
    """GET /wrongnotes — 문제 본문 포함 오답노트 항목"""
    wrongnoteId: int
    questionId: int
    subjectId: int
    subjectName: str
    conceptId: int
    conceptName: str
    stem: str
    choices: list[str]
    answerIndex: int
    userAnswer: Optional[int] = None
    explanation: Optional[str] = None
    mistakeType: Optional[str] = None
    userMemo: Optional[str] = None
    reviewDueAt: Optional[datetime] = None
    wrongCount: int
    updatedAt: datetime
    isStudyPlan: bool
    isFavorited: bool


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


class WrongnoteMemoUpdateRequest(BaseModel):
    """오답노트 코멘트(메모) 저장/수정 요청"""
    userMemo: str


class WrongnoteFavoriteUpdateRequest(BaseModel):
    """오답노트 즐겨찾기 ON/OFF 요청"""
    isFavorited: bool


# ===== STUDY_PLAN (주요 개념) =====

class StudyPlanCreateRequest(BaseModel):
    """주요 개념 일괄 등록 요청"""
    conceptIds: list[int]


class StudyPlanItem(BaseModel):
    conceptId: int
    conceptName: str
    createdAt: datetime


class StudyPlanListResponse(BaseModel):
    items: list[StudyPlanItem]


# ===== REVIEW (복습) =====

class ReviewConceptItem(BaseModel):
    """GET /review/concepts — 에빙하우스 복습 예정 개념"""
    conceptId: int
    conceptName: str
    score: float
    nextReviewAt: Optional[datetime] = None
    isStudyPlan: bool


# ===== INTRO (입문자 플로우) =====

class IntroSessionResponse(BaseModel):
    sessionToken: str
    expiresAt: datetime

    class Config:
        from_attributes = True


class SubjectSelectRequest(BaseModel):
    subjectId: int


class IntroConceptResponse(BaseModel):
    """과목 선택 후 약점 선택용 개념 목록"""
    id: int
    conceptName: str

    class Config:
        from_attributes = True


class SelfDiagnosisRequest(BaseModel):
    weakConceptIds: list[int]


class DiagnosticQuestionResponse(BaseModel):
    """진단 테스트용 문제 응답 — answerIndex/explanation 미노출"""
    id: int
    subjectId: int
    conceptId: int
    stem: str
    choices: list[str]

    class Config:
        from_attributes = True


class IntroAttemptRequest(BaseModel):
    questionId: int
    selectedIndex: int
    durationMs: Optional[int] = None


class IntroAttemptResponse(BaseModel):
    id: int
    isCorrect: bool
    explanation: Optional[str] = None


class ConceptWeakItem(BaseModel):
    conceptId: int
    conceptName: str


class ConceptResultItem(BaseModel):
    conceptId: int
    conceptName: str
    correct: int
    total: int
    accuracy: float


class IntroReportResponse(BaseModel):
    predictedWeak: list[ConceptWeakItem]
    actualResults: list[ConceptResultItem]


# ===== HOME (홈화면) =====

class HomeUserInfo(BaseModel):
    name: str
    streakCount: int


class HomeExamGoal(BaseModel):
    examName: str
    examDate: date
    dDay: int


class HomeReviewQueue(BaseModel):
    reviewConceptCount: int
    wrongNoteCount: int


class HomeResponse(BaseModel):
    user: HomeUserInfo
    examGoal: Optional[HomeExamGoal]
    reviewQueue: HomeReviewQueue
    dailyStrategy: str
    hasStudyPlan: bool
