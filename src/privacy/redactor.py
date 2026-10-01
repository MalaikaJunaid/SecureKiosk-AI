from collections import Counter
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from src.schemas.privacy_schema import RedactionResult


class PIIRedactor:
    def __init__(self):
        """
        Initializes the Presidio NLP engines. 
        Loading this is computationally expensive, so it should only happen once at startup.
        """
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()

    def redact(self, text: str) -> RedactionResult:
        """
        Scans text for PII entities and replaces them with strict <ENTITY_TYPE> tokens.
        """
        if not text or not text.strip():
            return RedactionResult(original_text=text, redacted_text=text, redacted_entities={})

        # Analyze text for all supported PII entities (Names, Emails, Phones, etc.)
        results = self.analyzer.analyze(text=text, entities=[], language="en")

        # Anonymize findings by replacing them with their categorical token (e.g., <PERSON>)
        anonymized_result = self.anonymizer.anonymize(text=text, analyzer_results=results)

        # Tally the counts of what was removed for monitoring/telemetry
        entity_counts = Counter([res.entity_type for res in results])

        return RedactionResult(
            original_text=text,
            redacted_text=anonymized_result.text,
            redacted_entities=dict(entity_counts)
        )