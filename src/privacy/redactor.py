from collections import Counter
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
from src.schemas.privacy_schema import RedactionResult


class PIIRedactor:
    def __init__(self):
        # 1. Explicitly configure the NLP engine to use the lightweight model
        nlp_config = {
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
        }
        provider = NlpEngineProvider(nlp_configuration=nlp_config)
        
        # 2. Pass the configured engine to the Analyzer
        self.analyzer = AnalyzerEngine(nlp_engine=provider.create_engine())
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