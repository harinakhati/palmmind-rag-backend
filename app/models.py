from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
)

from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    # Unique document identifier
    document_id = Column(
        String(36),
        primary_key=True,
        index=True,
    )

    # Original uploaded filename
    filename = Column(
        String(255),
        nullable=False,
    )

    # PDF or TXT
    file_type = Column(
        String(10),
        nullable=False,
    )

    # Fixed-size or recursive
    chunking_method = Column(
        String(50),
        nullable=False,
    )

    # Chunk configuration
    chunk_size = Column(
        Integer,
        nullable=False,
    )

    overlap = Column(
        Integer,
        nullable=False,
    )

    # Document processing information
    character_count = Column(
        Integer,
        nullable=False,
    )

    chunk_count = Column(
        Integer,
        nullable=False,
    )

    embedding_dimensions = Column(
        Integer,
        nullable=False,
    )

    # Upload timestamp
    created_at = Column(
    DateTime,
    default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    nullable=False,
)