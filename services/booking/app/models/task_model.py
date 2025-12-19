from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    String,
    DateTime,
    BigInteger,
    Integer,
    Numeric,
    Text,
    Index,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.schema import Sequence

TaskBase = declarative_base()


class TaskModel(TaskBase):
    __tablename__ = "tasks"
    ID = Column(
        BigInteger,
        Sequence("task_id_seq", start=1000),
        primary_key=True
    )
    TaskType = Column(String(100), nullable=False)
    Status = Column(String(50), nullable=False, default="pending")
    UserID = Column(BigInteger, nullable=False)
    Priority = Column(String(20), nullable=False, default="medium")
    
    Parameters = Column(JSON, nullable=True)
    Result = Column(JSON, nullable=True)
    Progress = Column(Integer, nullable=False, default=0)
    ProcessingTime = Column(Numeric(10, 2), nullable=True)
    ErrorMessage = Column(Text, nullable=True)
    TaskReference = Column(String(50), nullable=False, unique=True)
    
    # Timestamps
    CreatedAt = Column(DateTime, nullable=False)
    StartedAt = Column(DateTime, nullable=True)
    UpdatedAt = Column(DateTime, nullable=False)
    CompletedAt = Column(DateTime, nullable=True)

    # Indexes
    task_ref_index = Index("idx_task_reference", TaskReference)
    task_type_index = Index("idx_task_type", TaskType)
    status_index = Index("idx_task_status", Status)
    user_id_index = Index("idx_task_user_id", UserID)
    priority_index = Index("idx_task_priority", Priority)
    
    __table_args__ = (
        UniqueConstraint("TaskReference", name="uq_task_reference"),
    )

    def __repr__(self):
        return (
            f"TaskID='{self.ID}', TaskReference='{self.TaskReference}', "
            f"TaskType='{self.TaskType}', Status='{self.Status}', "
            f"UserID='{self.UserID}', Progress='{self.Progress}%'"
        )
