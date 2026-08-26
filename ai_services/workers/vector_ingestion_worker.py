"""Background Worker: Periodically ingests new field notes and metrics into FAISS."""

import time
import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.database import SessionLocal
from src.models.models import FieldNote, KPIMetric, FinancialLineItem, OperationalRisk

logger = logging.getLogger(__name__)


def ingest_unvectorized_notes(db: Session) -> int:
    notes = db.query(FieldNote).filter(FieldNote.vectorized == False).all()
    if not notes:
        return 0

    try:
        from ai_services.rag.vector_store import FAISSVectorStore
        store = FAISSVectorStore()

        notes_data = [
            {
                "id": n.id, "title": n.title, "content": n.content,
                "beneficiary_quote": n.beneficiary_quote, "project_id": n.project_id,
                "note_type": n.note_type, "location": n.location, "date_observed": n.date_observed,
            }
            for n in notes
        ]

        count = store.ingest_field_notes(notes_data)

        for note in notes:
            note.vectorized = True
        db.commit()

        logger.info(f"Vectorized {count} chunks from {len(notes)} field notes")
        return count
    except Exception as e:
        logger.error(f"Failed to vectorize notes: {e}")
        db.rollback()
        return 0


def run_worker(interval_seconds: int = 300):
    logger.info(f"Starting vector ingestion worker (interval: {interval_seconds}s)")
    while True:
        try:
            db = SessionLocal()
            count = ingest_unvectorized_notes(db)
            if count > 0:
                logger.info(f"Ingested {count} new vector chunks")
            db.close()
        except Exception as e:
            logger.error(f"Worker error: {e}")
        time.sleep(interval_seconds)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_worker()
