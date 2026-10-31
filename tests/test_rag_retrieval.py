"""Tests for RAG Retrieval: BM25, Embeddings, Hybrid Retrieval, Query Router, and Reranker.
"""
import unittest
from complyai.connectors.india import IndiaConnector
from complyai.db.repository import RegulatoryRepository
from complyai.ingestion.pipeline import RegulatoryIngestionService
from complyai.rag.embeddings import EmbeddingService
from complyai.rag.bm25 import BM25Index
from complyai.rag.query_router import LegalQueryRouter
from complyai.rag.hybrid_retriever import HybridRegulatoryRetriever
from complyai.types import LegalDomain


class TestRAGRetrieval(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.repo = RegulatoryRepository()
        cls.ingestion = RegulatoryIngestionService(repository=cls.repo)
        cls.connector = IndiaConnector()
        cls.ingestion.ingest_all_from_connector(cls.connector)
        cls.retriever = HybridRegulatoryRetriever(repository=cls.repo)
        cls.router = LegalQueryRouter()

    def test_query_router_intent_and_domain(self):
        # Query 1: Cyber incident
        routed_cyber = self.router.route_query("What is the CERT-In incident reporting timeline?")
        self.assertEqual(routed_cyber.primary_domain, LegalDomain.CYBERSECURITY)
        self.assertEqual(routed_cyber.jurisdictions, ["India"])

        # Query 2: POSH
        routed_posh = self.router.route_query("Do we need an internal complaints committee for sexual harassment?")
        self.assertEqual(routed_posh.primary_domain, LegalDomain.LABOUR_EMPLOYMENT)

        # Query 3: Wage record
        routed_wage = self.router.route_query("Must we maintain a muster roll and wage register for employees?")
        self.assertEqual(routed_wage.primary_domain, LegalDomain.LABOUR_EMPLOYMENT)

    def test_bm25_exact_keyword_search(self):
        bm25 = BM25Index()
        bm25.add_document("doc1", "Internal complaints committee sexual harassment workplace")
        bm25.add_document("doc2", "Income tax corporate deduction TDS return")
        results = bm25.search("complaints committee")
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0][0], "doc1")

    def test_embedding_cosine_similarity(self):
        emb = EmbeddingService(dimension=64)
        v1 = emb.embed_text("data protection privacy breach")
        v2 = emb.embed_text("privacy breach personal data security")
        v3 = emb.embed_text("factory heavy machinery boiler steam")

        from complyai.db.repository import cosine_similarity
        sim_related = cosine_similarity(v1, v2)
        sim_unrelated = cosine_similarity(v1, v3)
        self.assertGreater(sim_related, sim_unrelated)

    def test_hybrid_retriever(self):
        results = self.retriever.retrieve(
            query="mandatory cyber incident reporting 6 hours to CERT-In",
            top_k=3,
        )
        self.assertGreater(len(results), 0)
        top_sec, score, top_doc = results[0]
        self.assertIn("CERT", top_doc.title.upper())
        self.assertIn("Direction-2", top_sec.section_number)


if __name__ == "__main__":
    unittest.main()

