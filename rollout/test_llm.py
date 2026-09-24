"""Check reasoning parameters on the HTTP request after LiteLLM translation."""

import json
import unittest

import httpx
from openai import OpenAI

from rollout.llm import LLMClient, args_for


class ReasoningRequestTest(unittest.TestCase):
    def test_effort_reaches_chat_completions_without_model_whitelist(self):
        requests = []

        def respond(request):
            body = json.loads(request.content)
            requests.append(body)
            return httpx.Response(200, json={
                "id": "test", "object": "chat.completion", "created": 0,
                "model": body["model"],
                "choices": [{"index": 0, "finish_reason": "stop",
                             "message": {"role": "assistant", "content": "OK"}}],
                "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
            })

        with httpx.Client(transport=httpx.MockTransport(respond)) as transport:
            client = OpenAI(api_key="test-key", base_url="https://example.invalid/v1",
                            http_client=transport)
            cases = [(model, effort)
                     for model in ("openai/deepseek-v4p1-flash-wave", "openai/custom-model")
                     for effort in ("max", "medium", "")]
            for model, effort in cases:
                with self.subTest(model=model, effort=effort):
                    args = args_for(model, effort, max_tokens=128)
                    args["client"] = client
                    result = LLMClient(model, args, max_attempts=1).chat(
                        [{"role": "user", "content": "Reply OK"}])
                    self.assertEqual(result.content, "OK")
                    self.assertEqual(requests[-1]["model"], model.removeprefix("openai/"))
                    if effort:
                        self.assertEqual(requests[-1]["reasoning_effort"], effort)
                    else:
                        self.assertNotIn("reasoning_effort", requests[-1])
                    self.assertNotIn("reasoning", requests[-1])


if __name__ == "__main__":
    unittest.main()
