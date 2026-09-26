"""Business logic and AI services layer for LexiGuard."""

from services.action_service import generate_action_plan
from services.cache import CacheManager, cache_manager
from services.compare_service import compare_documents
from services.gemini_client import GeminiClient, gemini_client, get_last_call_info
from services.qa_service import answer_document_query
from services.risk_service import audit_contract_risks, verify_quote_authenticity
from services.simplify_service import simplify_document

__all__ = [
    "GeminiClient",
    "gemini_client",
    "get_last_call_info",
    "CacheManager",
    "cache_manager",
    "simplify_document",
    "audit_contract_risks",
    "verify_quote_authenticity",
    "answer_document_query",
    "compare_documents",
    "generate_action_plan",
]
