"""Tests for API endpoints."""
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_dashboard_summary():
    response = client.get("/api/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_beneficiaries" in data
    assert "completion_rate" in data


def test_program_performance():
    response = client.get("/api/programs/performance")
    assert response.status_code == 200


def test_beneficiary_analytics():
    response = client.get("/api/beneficiaries/analytics")
    assert response.status_code == 200


def test_data_quality():
    response = client.get("/api/data-quality")
    assert response.status_code == 200


def test_reports_list():
    response = client.get("/api/reports")
    assert response.status_code == 200


def test_ai_chat():
    response = client.post("/api/ai/chat", json={"message": "What is the completion rate?"})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data


def test_ai_chat_dropout_recommendation():
    response = client.post(
        "/api/ai/chat",
        json={"message": "WHAT can be done to reduce dropout?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "dropout" in data["answer"].lower()
    assert "attendance" in data["answer"].lower()
    assert data["relevant_kpis"]["dropout_rate"] >= 0


@pytest.mark.parametrize(
    "question, expected_text",
    [
        ("How is the data quality?", "data quality"),
        ("Why is dropout increasing?", "does not establish why"),
        ("Which programs are at risk?", "early-warning"),
    ],
)
def test_ai_management_question_intents(question, expected_text):
    response = client.post("/api/ai/chat", json={"message": question})
    assert response.status_code == 200
    assert expected_text in response.json()["answer"].lower()


def test_ai_insights():
    response = client.get("/api/ai/insights")
    assert response.status_code == 200


def test_ai_faqs():
    response = client.get("/api/ai/faqs")
    assert response.status_code == 200
    faqs = response.json()["faqs"]
    assert len(faqs) == 4
    assert faqs[0]["question"] == "What is KPC InsightFlow AI?"


def test_periods():
    response = client.get("/api/periods")
    assert response.status_code == 200


def test_data_sources():
    response = client.get("/api/data-sources")
    assert response.status_code == 200
