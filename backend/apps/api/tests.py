from django.test import TestCase, Client
from django.core.cache import cache
import json

from apps.common.limits import MAX_PAYLOAD_BYTES


class ApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        cache.clear()

    def test_health_ok(self):
        resp = self.client.get("/api/v1/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("data", {}).get("status"), "ok")
        self.assertIn("trace_id", data)

    def test_chat_basic(self):
        body = {"message": "你好"}
        resp = self.client.post(
            "/api/v1/chat",
            data=json.dumps(body),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get("success"))
        self.assertIn("answer", data.get("data", {}))

    def test_chat_history_too_long(self):
        history = [{"role": "user", "content": "a"}] * 4  # 超過 3 回合
        body = {"message": "hi", "history": history}
        resp = self.client.post(
            "/api/v1/chat",
            data=json.dumps(body),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 422)
        data = resp.json()
        self.assertFalse(data.get("success"))
        self.assertEqual(data.get("error", {}).get("code"), "validation_error")

    def test_chat_payload_too_large_413(self):
        padding = "x" * (MAX_PAYLOAD_BYTES + 10)
        body = {"message": "hi", "padding": padding}
        resp = self.client.post(
            "/api/v1/chat",
            data=json.dumps(body),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 413)
        data = resp.json()
        self.assertFalse(data.get("success"))
        self.assertEqual(data.get("error", {}).get("code"), "payload_too_large")

    def test_chat_rate_limit(self):
        body = {"message": "hi"}
        last_status = None
        for i in range(21):
            resp = self.client.post(
                "/api/v1/chat",
                data=json.dumps(body),
                content_type="application/json",
            )
            last_status = resp.status_code
        self.assertEqual(last_status, 429)

