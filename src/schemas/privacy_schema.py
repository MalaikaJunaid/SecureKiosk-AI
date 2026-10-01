from typing import Dict
from pydantic import BaseModel, Field


class RedactionResult(BaseModel):
    original_text: str = Field(..., description="The raw input text prior to masking")
    redacted_text: str = Field(..., description="The safe, anonymized text")
    redacted_entities: Dict[str, int] = Field(
        default_factory=dict, 
        description="Count of redacted entity types (e.g., {'PERSON': 1, 'PHONE_NUMBER': 2})"
    )