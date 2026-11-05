import unittest

from agents.orchestrator import RecommendationOrchestrator


class EmptyGraph(RecommendationOrchestrator):
    async def retrieve(self, state):
        return {"candidates": [], "degraded": False, "retries": 0}


class FailingGraph(RecommendationOrchestrator):
    async def retrieve(self, state):
        return {"candidates": [{"id": "real", "name": "真实商品"}], "degraded": False, "retries": 0}

    async def rank(self, state):
        self.calls = getattr(self, "calls", 0) + 1
        return {"items": [], "review_passed": False}


class GraphTests(unittest.IsolatedAsyncioTestCase):
    async def test_empty_never_creates_products(self):
        result = await EmptyGraph(None).recommend("耳机")
        self.assertEqual(result["items"], [])

    async def test_failed_ranking_retries_once_and_uses_candidates(self):
        graph = FailingGraph(None)
        result = await graph.recommend("耳机")
        self.assertEqual(graph.calls, 2)
        self.assertEqual(result["items"][0]["product"]["id"], "real")
        self.assertTrue(result["degraded"])
