from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    String,
    DateTime,
    BigInteger,
    Text,
    Index,
)
from sqlalchemy.schema import Sequence

NotificationBase = declarative_base()


# Handle edge case
class NotificationLogModel(NotificationBase):
    __tablename__ = "notification_logs"
    ID = Column(
        BigInteger,
        Sequence("notification_id_seq", start=1000),
        primary_key=True
    )
    EventType = Column(String(100), nullable=False)
    UserID = Column(BigInteger, nullable=True)
    RecipientEmail = Column(String(255), nullable=False)
    Subject = Column(String(255), nullable=False)
    Message = Column(Text, nullable=False)
    Status = Column(String(50), nullable=False, default="pending")
    # pending, sent, failed
    SentAt = Column(DateTime, nullable=True)
    CreatedAt = Column(DateTime, nullable=False)
    UpdatedAt = Column(DateTime, nullable=False)

    # Indexes
    event_type_index = Index("idx_event_type", EventType)
    user_id_index = Index("idx_notification_user_id", UserID)
    status_index = Index("idx_notification_status", Status)
    recipient_email_index = Index("idx_recipient_email", RecipientEmail)

    def __repr__(self):
        return (
            f"NotificationID='{self.ID}', EventType='{self.EventType}', "
            f"RecipientEmail='{self.RecipientEmail}', Status='{self.Status}'"
        )

