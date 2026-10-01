import pytest
from src.privacy.redactor import PIIRedactor


# Use scope="module" so the heavy NLP model only loads once for all tests in this file
@pytest.fixture(scope="module")
def redactor():
    return PIIRedactor()


def test_redact_person_and_phone(redactor):
    text = "The applicant John Doe can be reached at 555-019-2029."
    result = redactor.redact(text)

    # Verify PII is gone
    assert "John Doe" not in result.redacted_text
    assert "555-019-2029" not in result.redacted_text
    
    # Verify replacement tokens are present
    assert "<PERSON>" in result.redacted_text
    assert result.redacted_entities.get("PERSON", 0) >= 1


def test_no_pii_passthrough(redactor):
    text = "This document confirms that the ID card is valid."
    result = redactor.redact(text)

    # Verify safe text remains entirely untouched
    assert result.redacted_text == text
    assert len(result.redacted_entities) == 0


def test_empty_string_handling(redactor):
    result = redactor.redact("   ")
    assert result.redacted_text == "   "
    assert len(result.redacted_entities) == 0