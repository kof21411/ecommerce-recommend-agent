import unittest
from unittest.mock import patch
from agents.intent import classify_intent, parse_budget, search_terms
from agents.orchestrator import RecommendationOrchestrator


class IntentTests(unittest.TestCase):
    def test_intents(self):
        self.assertEqual(classify_intent("你好"), "chat")
        self.assertEqual(classify_intent("推荐适合跑步的耳机"), "recommend")
        self.assertEqual(classify_intent("对比苹果和小米手机"), "compare")
        self.assertEqual(classify_intent("这款耳机支持降噪吗"), "qa")

    def test_budgets(self):
        for query in ("500元以内的耳机", "预算500元", "不超过500元", "earbuds under 500"):
            self.assertEqual(parse_budget(query), 500)
        self.assertIsNone(parse_budget("买一台2024款手机"))

    def test_chinese_fallback_terms(self):
        terms = search_terms("推荐500元以内适合跑步的蓝牙耳机")
        self.assertIn("耳机", terms)
        self.assertIn("蓝牙", terms)
        self.assertNotIn("500", terms)


class ChatRoutingTests(unittest.IsolatedAsyncioTestCase):
    async def test_greeting_does_not_search_products(self):
        graph = RecommendationOrchestrator(None)
        with patch("agents.orchestrator.settings.OPENAI_API_KEY", ""):
            result = await graph.process_message("你好", [])
        self.assertEqual(result["intent"], "chat")
        self.assertEqual(result["items"], [])
