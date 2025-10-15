#!/usr/bin/env python3
"""Test different Llama Stack endpoints

NOTE: This is an integration test that requires a running LlamaStack server.
It will be skipped in CI environments.
"""

import os

import pytest
import requests

# Skip this test in CI environments
pytestmark = pytest.mark.skipif(
    os.getenv("CI") == "true",
    reason="Integration test - requires running LlamaStack server",
)

base_url = "http://localhost:8321"

endpoints = [
    "/v1/inference/chat_completion",
    "/v1/chat/completions",
    "/v1/openai/v1/chat/completions",
    "/inference/chat_completion",
]

test_payload = {
    "model": "ollama/llama3.3:70b",
    "messages": [{"role": "user", "content": "hi"}],
    "max_tokens": 5,
}

print("Testing Llama Stack endpoints...")
print("=" * 60)

for endpoint in endpoints:
    url = f"{base_url}{endpoint}"
    print(f"\nTesting: {url}")
    try:
        response = requests.post(
            url,
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        if response.status_code == 200:
            print(f"✅ SUCCESS! Status: {response.status_code}")
            result = response.json()
            if "choices" in result:
                print(f"   Response: {result['choices'][0]['message']['content']}")
            else:
                print(f"   Response: {result}")
        else:
            print(f"❌ Failed. Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "=" * 60)
