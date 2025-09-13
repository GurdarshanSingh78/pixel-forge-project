from typing import List
from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, Enum, func, ForeignKey, Boolean
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Mapped, mapped_column
import enum
from app.core.paths import DATABASE_FILE

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DATABASE_FILE}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class JobType(enum.Enum):
    FREE = "free"; PAID = "paid"

class JobStatus(enum.Enum):
    PENDING = "pending"; PROCESSING = "processing"; COMPLETED = "completed"; FAILED = "failed"

class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    query: Mapped[str] = mapped_column(String, index=True)
    email: Mapped[str] = mapped_column(String)
    image_count: Mapped[int] = mapped_column(Integer)
    job_type: Mapped[JobType] = mapped_column(Enum(JobType))
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.PENDING, nullable=False)
    email_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    images: Mapped[List["JobImage"]] = relationship("JobImage", back_pop_ulates="job", cascade="all, delete-orphan")

class JobImage(Base):
    __tablename__ = "job_images"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("jobs.id"))
    file_path: Mapped[str] = mapped_column(String)
    job: Mapped["Job"] = relationship("Job", back_pop_ulates="images")

def create_db_and_tables():
    """Creates database tables, checking first if they exist."""
    # --- THIS IS THE FIX ---
    # The 'checkfirst=True' argument makes this operation safe for multi-worker environments.
    Base.metadata.create_all(bind=engine, checkfirst=True)