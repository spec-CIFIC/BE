import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

# ── 설정 파일(.env) 로드 ───────────────────────────────────────
# pydantic-settings가 .env를 읽어 DATABASE_URL을 가져옵니다.
from app.core.config import settings

# ── ORM 모델 import ───────────────────────────────────────────
# Base를 import해야 Alembic이 어떤 테이블이 있는지 알 수 있습니다.
# orm.py의 모든 모델은 Base를 상속받으므로, Base만 가져오면 됩니다.
from app.db.database import Base
import app.models.orm  # noqa: F401 — 모델을 Base에 등록하기 위해 import (사용 안 해도 필수)

# ── Alembic 기본 설정 ─────────────────────────────────────────
# alembic.ini 파일을 읽어오는 설정 객체입니다.
config = context.config

# alembic.ini의 loggers 섹션을 Python 로깅 설정으로 적용합니다.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# .env에서 읽은 DATABASE_URL을 Alembic 설정에 주입합니다.
# alembic.ini의 sqlalchemy.url = placeholder 를 실제 URL로 덮어씁니다.
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# autogenerate 시 비교 대상이 되는 메타데이터입니다.
# Base.metadata 안에 orm.py의 모든 테이블 정보가 담겨 있습니다.
target_metadata = Base.metadata


# ── 오프라인 마이그레이션 (DB 연결 없이 SQL 파일만 생성) ──────────
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


# ── 온라인 마이그레이션 (실제 DB에 연결해 테이블 생성/수정) ─────────
def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    # asyncpg(비동기 드라이버)를 사용하므로 비동기 엔진을 만듭니다.
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # 마이그레이션은 짧게 연결했다 끊으므로 풀 미사용
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


# 오프라인/온라인 중 어느 모드로 실행됐는지 판단해 분기합니다.
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
