import re
from typing import List, Dict, Any, Optional
from services.retrieval_service import RetrievalService, retrieval_service
from services.rag_service import RAGService, rag_service

from services.language_service import language_service

# Structured BIS Application Service Categories
BIS_SERVICES_CATEGORIES = [
    {
        "id": "product_certification",
        "name": "Product Certification",
        "description": "Information on ISI mark scheme, compliance testing, and product certification procedures."
    },
    {
        "id": "bis_registration",
        "name": "BIS Registration",
        "description": "Compulsory Registration Scheme (CRS) details for electronic and IT products."
    },
    {
        "id": "licensing",
        "name": "Licensing",
        "description": "Guidance on BIS CML licence application, documentation, and validity verification."
    },
    {
        "id": "indian_standards",
        "name": "Indian Standards",
        "description": "Directory and technical specifications of formulated Indian Standards (IS codes)."
    },
    {
        "id": "testing",
        "name": "Testing",
        "description": "Information on BIS laboratory network and product sample testing procedures."
    },
    {
        "id": "certification_process",
        "name": "Certification Process",
        "description": "Step-by-step workflow for factory audit, sample evaluation, and licence issuance."
    },
    {
        "id": "consumer_services",
        "name": "Consumer Services",
        "description": "Consumer protection services, hallmarking (HUID) verification, and grievance submission."
    },
    {
        "id": "industry_services",
        "name": "Industry Services",
        "description": "Services for manufacturers, importers, and technical committee participation."
    },
    {
        "id": "standards_information",
        "name": "Standards Information",
        "description": "Access to sectional committee details and technical standard parameter lookups."
    },
    {
        "id": "complaints_grievances",
        "name": "Complaints / Grievances",
        "description": "Procedure for reporting non-compliant ISI products or lodging regulatory complaints."
    },
    {
        "id": "general_bis_information",
        "name": "General BIS Information",
        "description": "Overview of Bureau of Indian Standards role as National Standards Body of India."
    }
]

# Standard Identifier Regex Pattern
# Matches: IS 10500, IS/ISO 9001, IS 456, ISO 9001, IEC 60601, IS 10500:2012, etc.
STANDARD_IDENTIFIER_REGEX = re.compile(
    r'\b(?:IS(?:/ISO)?|ISO|IEC|ASTM|EN|BS)\s*(?::\s*)?\d+(?:[-:\/]\d+)*(?::\d{4})?\b',
    re.IGNORECASE
)


class BISSearchService:
    _instance: Optional['BISSearchService'] = None

    def __init__(
        self,
        ret_service: Optional[RetrievalService] = None,
        r_service: Optional[RAGService] = None
    ):
        self.retrieval_service = ret_service or RetrievalService.get_instance()
        if r_service is not None:
            self.rag_service = r_service
        elif ret_service is not None:
            self.rag_service = RAGService(ret_service=self.retrieval_service)
        else:
            self.rag_service = RAGService.get_instance()

    @classmethod
    def get_instance(cls) -> 'BISSearchService':
        """
        Singleton getter for BISSearchService.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_service_categories(self) -> List[Dict[str, str]]:
        """
        Returns list of structured, non-fabricated application service categories.
        """
        return BIS_SERVICES_CATEGORIES

    def detect_standard_identifier(self, query: str) -> Optional[str]:
        """
        Detects and extracts standard identifier patterns (e.g. 'IS 10500', 'IS/ISO 9001') from query text.
        Preserves numbers, hyphens, colons, and slashes without destructive lowercasing.
        """
        if not query or not query.strip():
            return None

        match = STANDARD_IDENTIFIER_REGEX.search(query.strip())
        if match:
            # Normalize whitespace within matched identifier while preserving original casing
            raw_id = match.group(0).strip()
            # Standardize spacing e.g. "IS10500" -> "IS 10500" if needed, but match.group(0) preserves user string
            return raw_id
        return None

    def detect_intent(self, query: str) -> str:
        """
        Lightweight deterministic intent detector.
        Classifies query into:
        CERTIFICATION, LICENSING, STANDARD_SEARCH, TESTING, CONSUMER_SERVICE, INDUSTRY_SERVICE, GENERAL_QUESTION, UNKNOWN
        """
        if not query or not query.strip():
            return "UNKNOWN"

        q_lower = query.strip().lower()

        # 1. Standard Search Intent (if standard identifier present or query explicitly searches standards)
        if self.detect_standard_identifier(query) or any(k in q_lower for k in ["is code", "is standard", "indian standard", "search standard", "specification for", "मानक", "मानके", "तपशील"]):
            return "STANDARD_SEARCH"

        # 2. Certification Intent
        if any(k in q_lower for k in ["certification", "isi mark", "get certified", "apply for certification", "crs scheme", "how to certify", "product certification", "प्रमाणन", "प्रमाणपत्र", "प्रमाणीकरण", "isi मार्क"]):
            return "CERTIFICATION"

        # 3. Licensing Intent
        if any(k in q_lower for k in ["license", "licence", "cml number", "cml licence", "licensing", "renew licence", "परवाना", "लायसन्स", "लाइसेंस"]):
            return "LICENSING"

        # 4. Testing Intent
        if any(k in q_lower for k in ["test", "testing", "laboratory", "labs", "sample test", "test report", "परीक्षण", "चाचणी", "प्रयोगशाळा", "प्रयोगशाला"]):
            return "TESTING"

        # 5. Consumer Service Intent
        if any(k in q_lower for k in ["consumer", "hallmark", "huid", "complaint", "grievance", "hallmarking", "ग्राहक", "हॉलमार्क", "तक्रार", "शिकायत"]):
            return "CONSUMER_SERVICE"

        # 6. Industry Service Intent
        if any(k in q_lower for k in ["industry", "manufacturer", "importer", "factory audit", "sit endorsement", "उद्योग", "उत्पादक", "निर्माता"]):
            return "INDUSTRY_SERVICE"

        # 7. General Question Intent
        if any(k in q_lower for k in ["what is bis", "what does bis do", "overview", "about bis", "bis services", "what services", "काय आहे", "क्या है", "माहिती", "जानकारी"]):
            return "GENERAL_QUESTION"

        return "UNKNOWN"

    def search_bis(
        self,
        query: str,
        service_filter: Optional[str] = None,
        top_k: int = 5,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes dedicated BIS search:
        1. Validates non-empty query.
        2. Detects standard identifier, user intent, and target language.
        3. Executes identifier-boosted retrieval via RetrievalService.
        4. Executes RAG generation via RAGService in target language.
        5. Returns structured search results, RAG answer, language, and source citations.
        """
        if not query or not query.strip():
            raise ValueError("Search query cannot be empty or whitespace-only.")

        clean_query = query.strip()
        if len(clean_query) > 1000:
            raise ValueError("Search query exceeds maximum allowed length of 1000 characters.")

        # Detect intent, standard identifier, and language
        intent = self.detect_intent(clean_query)
        detected_standard = self.detect_standard_identifier(clean_query)
        resolved_lang = language_service.resolve_language(clean_query, explicit_lang=language)

        # Validate service filter if provided
        valid_service_ids = {cat["id"] for cat in BIS_SERVICES_CATEGORIES}
        clean_service = service_filter.strip().lower() if service_filter and service_filter.strip() else None

        if clean_service and clean_service not in valid_service_ids:
            raise ValueError(f"Invalid service category filter '{service_filter}'. Valid options are: {', '.join(sorted(valid_service_ids))}")

        # Perform retrieval using existing RetrievalService
        retrieval_res = self.retrieval_service.retrieve(clean_query, top_k=top_k)
        retrieved_chunks = retrieval_res.get("results", [])

        # Identifier-aware hybrid re-ranking: if standard identifier detected, boost chunks containing exact identifier
        if detected_standard and retrieved_chunks:
            std_upper = detected_standard.upper()

            def rank_key(c):
                txt_upper = (c.get("chunk_text") or "").upper()
                fn_upper = (c.get("filename") or "").upper()
                # Primary key: 1 if standard identifier present in text or filename, else 0
                has_std = 1 if (std_upper in txt_upper or std_upper in fn_upper) else 0
                # Secondary key: similarity_score
                sim = c.get("similarity_score", 0.0)
                return (has_std, sim)

            retrieved_chunks = sorted(retrieved_chunks, key=rank_key, reverse=True)

        # Execute end-to-end RAG answer & sources using existing RAGService in target language
        rag_res = self.rag_service.answer_question(clean_query, top_k=top_k, language=resolved_lang)

        # Format public search result objects (reusing SourceItem schema format)
        formatted_results = self.rag_service._format_sources(retrieved_chunks)

        return {
            "query": clean_query,
            "intent": intent,
            "detected_standard": detected_standard,
            "service_filter": clean_service,
            "language": rag_res.get("language", resolved_lang),
            "results": formatted_results,
            "answer": rag_res.get("answer", ""),
            "sources": rag_res.get("sources", [])
        }


bis_search_service = BISSearchService.get_instance()
