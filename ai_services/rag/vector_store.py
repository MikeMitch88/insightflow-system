"""FAISS Vector Store Manager: Ingests field notes and metrics for RAG retrieval."""

import os
import json
import pickle
from typing import Optional

import faiss
import numpy as np

from src.config import FAISS_INDEX_PATH, FAISS_CHUNK_SIZE, FAISS_CHUNK_OVERLAP


class FAISSVectorStore:
    """Manages a FAISS vector store for RAG-based report generation."""

    def __init__(self):
        self.index_path = FAISS_INDEX_PATH
        self.index: Optional[faiss.IndexFlatIP] = None
        self.documents: list[dict] = []
        self.embedder = None
        self._load_or_create()

    def _load_or_create(self):
        index_file = os.path.join(self.index_path, "faiss.index")
        docs_file = os.path.join(self.index_path, "documents.pkl")

        if os.path.exists(index_file) and os.path.exists(docs_file):
            self.index = faiss.read_index(index_file)
            with open(docs_file, "rb") as f:
                self.documents = pickle.load(f)
        else:
            os.makedirs(self.index_path, exist_ok=True)
            self.index = faiss.IndexFlatIP(384)
            self.documents = []

    def _get_embedder(self):
        if self.embedder is None:
            try:
                from sentence_transformers import SentenceTransformer
                self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
            except ImportError:
                self.embedder = "fallback"
        return self.embedder

    def _embed_text(self, text: str) -> np.ndarray:
        embedder = self._get_embedder()
        if embedder == "fallback":
            return np.random.randn(384).astype(np.float32)
        embedding = embedder.encode(text, normalize_embeddings=True)
        return embedding.astype(np.float32)

    def _chunk_text(self, text: str, chunk_size: int = FAISS_CHUNK_SIZE, overlap: int = FAISS_CHUNK_OVERLAP) -> list[str]:
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            if chunk.strip():
                chunks.append(chunk.strip())
            start = end - overlap
        return chunks

    def ingest_field_notes(self, notes: list[dict]) -> int:
        new_docs = 0
        for note in notes:
            content = f"{note.get('title', '')} {note.get('content', '')}"
            if note.get('beneficiary_quote'):
                content += f" Quote: {note['beneficiary_quote']}"

            chunks = self._chunk_text(content)
            for chunk in chunks:
                embedding = self._embed_text(chunk)
                self.index.add(embedding.reshape(1, -1))
                self.documents.append({
                    "text": chunk,
                    "source": "field_note",
                    "note_id": note.get("id"),
                    "project_id": note.get("project_id"),
                    "note_type": note.get("note_type"),
                    "location": note.get("location"),
                    "date_observed": str(note.get("date_observed", "")),
                })
                new_docs += 1

        self._save()
        return new_docs

    def ingest_kpi_metrics(self, metrics: list[dict]) -> int:
        new_docs = 0
        for metric in metrics:
            text = (
                f"KPI: {metric.get('kpi_name', '')} | "
                f"Category: {metric.get('kpi_category', 'N/A')} | "
                f"Target: {metric.get('target_value', 0)} | "
                f"Actual: {metric.get('actual_value', 0)} | "
                f"Attainment: {metric.get('attainment_pct', 0)}% | "
                f"Notes: {metric.get('notes', 'N/A')}"
            )
            embedding = self._embed_text(text)
            self.index.add(embedding.reshape(1, -1))
            self.documents.append({
                "text": text,
                "source": "kpi_metric",
                "metric_id": metric.get("id"),
                "project_id": metric.get("project_id"),
                "kpi_name": metric.get("kpi_name"),
            })
            new_docs += 1

        self._save()
        return new_docs

    def ingest_financial_items(self, items: list[dict]) -> int:
        new_docs = 0
        for item in items:
            text = (
                f"Financial: {item.get('line_item', '')} | "
                f"Category: {item.get('category', 'N/A')} | "
                f"Budget: {item.get('budget_amount', 0)} {item.get('currency', 'USD')} | "
                f"Spend: {item.get('actual_spend', 0)} | "
                f"Burn Rate: {item.get('burn_rate', 0)}% | "
                f"Variance: {item.get('variance', 0)} | "
                f"Notes: {item.get('notes', 'N/A')}"
            )
            embedding = self._embed_text(text)
            self.index.add(embedding.reshape(1, -1))
            self.documents.append({
                "text": text,
                "source": "financial_item",
                "item_id": item.get("id"),
                "project_id": item.get("project_id"),
                "line_item": item.get("line_item"),
            })
            new_docs += 1

        self._save()
        return new_docs

    def search(self, query: str, k: int = 5) -> list[dict]:
        if self.index.ntotal == 0:
            return []

        query_embedding = self._embed_text(query).reshape(1, -1)
        k = min(k, self.index.ntotal)
        distances, indices = self.index.search(query_embedding, k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.documents):
                doc = self.documents[idx].copy()
                doc["score"] = float(dist)
                results.append(doc)
        return results

    def search_by_source(self, query: str, source: str, k: int = 5) -> list[dict]:
        all_results = self.search(query, k=k * 3)
        filtered = [r for r in all_results if r.get("source") == source]
        return filtered[:k]

    def get_context_for_report(self, section: str, project_id: Optional[int] = None, k: int = 10) -> str:
        section_queries = {
            "executive_summary": "organization performance overview achievements impact",
            "programmatic_progress": "program progress KPI targets actuals beneficiaries enrollment",
            "financial_utilization": "budget spend burn rate financial utilization variance",
            "operational_challenges": "risks challenges mitigation issues problems",
            "impact_narratives": "beneficiary stories impact testimonials field observations",
            "next_quarter_outlook": "plans upcoming milestones targets next quarter future",
        }
        query = section_queries.get(section, section)
        results = self.search(query, k=k)

        if project_id:
            results = [r for r in results if r.get("project_id") == project_id] + results

        context_parts = []
        for r in results[:k]:
            context_parts.append(f"[{r.get('source', 'unknown')}] {r.get('text', '')}")
        return "\n\n".join(context_parts)

    def _save(self):
        os.makedirs(self.index_path, exist_ok=True)
        faiss.write_index(self.index, os.path.join(self.index_path, "faiss.index"))
        with open(os.path.join(self.index_path, "documents.pkl"), "wb") as f:
            pickle.dump(self.documents, f)

    def get_stats(self) -> dict:
        source_counts = {}
        for doc in self.documents:
            source = doc.get("source", "unknown")
            source_counts[source] = source_counts.get(source, 0) + 1
        return {
            "total_vectors": self.index.ntotal if self.index else 0,
            "total_documents": len(self.documents),
            "source_breakdown": source_counts,
        }

    def clear(self):
        self.index = faiss.IndexFlatIP(384)
        self.documents = []
        self._save()
