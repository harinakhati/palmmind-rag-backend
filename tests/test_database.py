import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, engine
from app.models import Document


@pytest.fixture
def mysql_test_session():
    """Create an isolated SQLAlchemy session for MySQL testing."""

    # Reuse the configured connection but target the test database.
    test_url = engine.url.set(
        database="palmmind_rag_test"
    )

    test_engine = create_engine(
        test_url,
        pool_pre_ping=True,
    )

    # Create tables only inside the isolated test database.
    Base.metadata.create_all(bind=test_engine)

    TestSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
    )

    db = TestSessionLocal()

    try:
        yield db

    finally:
        db.close()

        # Clean up only the isolated test database.
        Base.metadata.drop_all(bind=test_engine)

        test_engine.dispose()


def test_document_metadata_persists_in_mysql(mysql_test_session):
    db = mysql_test_session

    document = Document(
        document_id="mysql-integration-test-001",
        filename="sample.pdf",
        file_type=".pdf",
        chunking_method="recursive",
        chunk_size=1000,
        overlap=200,
        character_count=500,
        chunk_count=3,
        embedding_dimensions=384,
    )

    # Insert and commit the document.
    db.add(document)
    db.commit()

    # Retrieve the document from MySQL.
    saved_document = (
        db.query(Document)
        .filter_by(
            document_id="mysql-integration-test-001"
        )
        .first()
    )

    # Verify actual persisted values.
    assert saved_document is not None
    assert saved_document.filename == "sample.pdf"
    assert saved_document.file_type == ".pdf"
    assert saved_document.chunking_method == "recursive"
    assert saved_document.chunk_size == 1000
    assert saved_document.overlap == 200
    assert saved_document.character_count == 500
    assert saved_document.chunk_count == 3
    assert saved_document.embedding_dimensions == 384
    assert saved_document.created_at is not None