from datetime import  datetime,timezone
from sqlalchemy import String,DateTime
from sqlalchemy.orm import mapped_column,Mapped

from backend.app.database import Base

class User(Base):
    __tablename__ = "user"
    id:Mapped[int]=mapped_column(
        primary_key=True,
        index=True,
    )
    name:Mapped[str]=mapped_column(
        String(100),
        nullable=False
    )
    email:Mapped[str]=mapped_column(
        String(200),
        unique=True,
        index=True,
        nullable=False
    )
    hashed_password:Mapped[str]=mapped_column(
        String(100),
        nullable=False
    )
    created_at:Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda :datetime.now(timezone.utc)
    )