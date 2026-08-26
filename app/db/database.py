# app/db/database.py
# 역할: DB 연결 설정 + 세션 관리
# Spring으로 치면 DataSource 설정 + EntityManagerFactory 설정에 해당합니다.

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL


# ─────────────────────────────────────────────────────────────
# 2. 엔진 (Spring의 DataSource / ConnectionPool에 해당)
# ─────────────────────────────────────────────────────────────
# DB와의 실제 연결을 생성하고 관리하는 핵심 객체입니다.
# 앱 전체에서 하나만 만들어 재사용합니다 (싱글턴).
#
# create_async_engine : 비동기 방식으로 DB에 접속하는 엔진을 만듭니다.
# echo=settings.SQL_ECHO : 실행 SQL 출력 여부를 설정으로 제어합니다.
#                          기본 False(조용). 쿼리 디버깅 시 .env에 SQL_ECHO=true.
engine = create_async_engine(DATABASE_URL, echo=settings.SQL_ECHO)


# ─────────────────────────────────────────────────────────────
# 3. 세션 팩토리 (Spring의 EntityManagerFactory에 해당)
# ─────────────────────────────────────────────────────────────
# 세션(Session)은 요청 하나와 1:1로 대응합니다.
# Spring에서 EntityManager 하나가 트랜잭션 하나를 담당하는 것과 동일한 개념입니다.
#
# async_sessionmaker  : 비동기 세션을 찍어내는 팩토리입니다.
# class_=AsyncSession : 생성할 세션의 타입을 비동기 세션으로 지정합니다.
# expire_on_commit=False :
#   commit() 이후에도 세션에서 꺼낸 ORM 객체의 속성을 그대로 읽을 수 있게 합니다.
#   비동기 환경에서 commit 후 객체에 재접근하면 추가 쿼리가 발생할 수 있는데,
#   이를 방지하기 위해 False로 설정하는 것이 권장됩니다.
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ─────────────────────────────────────────────────────────────
# 4. ORM Base 클래스
# ─────────────────────────────────────────────────────────────
# 모든 ORM 모델(테이블 클래스)이 상속받는 부모 클래스입니다.
# Spring의 @Entity 어노테이션이 JPA를 통해 테이블과 연결되듯,
# 이 Base를 상속받은 클래스는 SQLAlchemy가 DB 테이블로 인식합니다.
#
# orm.py 에서 이 Base를 import해 각 테이블 클래스에 상속시킵니다.
# main.py 에서 Base.metadata.create_all() 을 호출하면
# 상속받은 모든 클래스가 실제 DB 테이블로 생성됩니다.
class Base(DeclarativeBase):
    pass


# ─────────────────────────────────────────────────────────────
# 5. DB 세션 의존성 주입 함수
# ─────────────────────────────────────────────────────────────
# FastAPI의 라우터/엔드포인트에서 Depends(get_db) 형태로 사용합니다.
# Spring의 @Autowired EntityManager와 역할이 비슷하지만,
# FastAPI는 각 HTTP 요청마다 이 함수를 실행해 세션을 만들고,
# 요청 처리가 끝나면 자동으로 세션을 닫습니다.
#
# AsyncGenerator 타입 힌트는 "이 함수가 yield를 포함한 비동기 제너레이터"임을 명시합니다.
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    # AsyncSessionLocal()로 세션을 열고, 요청 처리가 끝나면 자동으로 close()합니다.
    # async with 블록이 끝나는 시점(= yield 이후)에 세션이 닫힙니다.
    async with AsyncSessionLocal() as session:
        yield session
