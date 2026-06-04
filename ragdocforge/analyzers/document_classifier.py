from ragdocforge.analyzers.metadata_extractor import MetadataExtractor
from ragdocforge.schemas.document_models import ParsedDocument


class DocumentClassifier:
    def classify(self, document: ParsedDocument) -> ParsedDocument:
        return MetadataExtractor().enrich(document)
