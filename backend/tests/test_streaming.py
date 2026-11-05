import unittest
from types import SimpleNamespace
from unittest.mock import patch

from agents.orchestrator import RecommendationOrchestrator


class FakeModel:
    async def astream(self, messages):
        yield SimpleNamespace(content="你好")
        yield SimpleNamespace(content="世界")


class FakeGraph:
    async def astream(self, inputs, stream_mode):
        yield {"retrieve": {"candidates": [{"id": "1"}]}}
        yield {"rank": {"items": [{"product": {"id": "1"}}]}}
        yield {"review": {"content": "结果已校验"}}


class StreamingTests(unittest.IsolatedAsyncioTestCase):
    async def test_chat_yields_model_chunks(self):
        agent = RecommendationOrchestrator.__new__(RecommendationOrchestrator)
        agent.llm = FakeModel()
        with patch("agents.orchestrator.settings.OPENAI_API_KEY", "test"):
            events = [event async for event in agent.stream_message("你好", [])]
        self.assertEqual([event["content"] for event in events], ["你好", "世界"])

    async def test_graph_streams_progress_and_validated_products(self):
        agent = RecommendationOrchestrator.__new__(RecommendationOrchestrator)
        agent.graph = FakeGraph()
        events = [event async for event in agent.stream_message("推荐耳机", [])]
        self.assertEqual(events[-1], {"type": "products", "items": [{"product": {"id": "1"}}]})
        self.assertEqual(events[-2]["content"], "结果已校验")
        self.assertGreaterEqual(len(events), 4)
