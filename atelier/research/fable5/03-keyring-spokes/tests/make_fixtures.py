#!/usr/bin/env python3
"""Regenerate the recorded-response fixtures in tests/fixtures/.

The fixtures are hand-built to match each provider's documented response
shapes (see TESTS.md for the doc references). Image payloads embed a real
1x1 PNG constructed with zlib so decode paths and magic-byte checks are
exercised for real.

Run:  python tests/make_fixtures.py
"""
import base64
import json
import os
import struct
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURES = os.path.join(HERE, "fixtures")


def tiny_png():
    """A valid 1x1 red PNG, built from scratch (no Pillow needed)."""
    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data)))
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    idat = zlib.compress(b"\x00\xff\x00\x00")   # filter byte + RGB pixel
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", idat) + chunk(b"IEND", b""))


PNG_B64 = base64.b64encode(tiny_png()).decode("ascii")

JSON_FIXTURES = {
    # ---- OpenAI /v1/chat/completions -------------------------------------
    "openai_chat.json": {
        "id": "chatcmpl-fixture001",
        "object": "chat.completion",
        "created": 1755700000,
        "model": "gpt-4o-mini-2024-07-18",
        "choices": [{
            "index": 0,
            "message": {"role": "assistant",
                        "content": "A muted palette of ochre and slate."},
            "finish_reason": "stop",
        }],
        "usage": {"prompt_tokens": 42, "completion_tokens": 12,
                  "total_tokens": 54},
    },
    # ---- OpenAI /v1/images/generations (gpt-image-1) ----------------------
    "openai_image.json": {
        "created": 1755700000,
        "data": [{"b64_json": PNG_B64}],
        "usage": {"input_tokens": 13, "output_tokens": 1056,
                  "total_tokens": 1069,
                  "input_tokens_details": {"image_tokens": 0,
                                           "text_tokens": 13}},
    },
    # ---- Ollama's OpenAI-compatible /v1/chat/completions -------------------
    "ollama_chat.json": {
        "id": "chatcmpl-ollama-1",
        "object": "chat.completion",
        "created": 1755700000,
        "model": "llama3.1:8b",
        "choices": [{
            "index": 0,
            "message": {"role": "assistant",
                        "content": "Local llama reporting in."},
            "finish_reason": "stop",
        }],
        "usage": {"prompt_tokens": 15, "completion_tokens": 6,
                  "total_tokens": 21},
    },
    # ---- Gemini :generateContent (text) ------------------------------------
    "gemini_chat.json": {
        "candidates": [{
            "content": {"parts": [
                {"text": "Golden-hour glaze over wet cobblestones."}],
                "role": "model"},
            "finishReason": "STOP",
            "index": 0,
        }],
        "usageMetadata": {"promptTokenCount": 21, "candidatesTokenCount": 9,
                          "totalTokenCount": 30},
        "modelVersion": "gemini-2.5-flash",
    },
    # ---- Gemini :generateContent (native image output) ---------------------
    "gemini_image.json": {
        "candidates": [{
            "content": {"parts": [
                {"text": "Here is your image."},
                {"inlineData": {"mimeType": "image/png", "data": PNG_B64}},
            ], "role": "model"},
            "finishReason": "STOP",
            "index": 0,
        }],
        "usageMetadata": {"promptTokenCount": 8,
                          "candidatesTokenCount": 1290,
                          "totalTokenCount": 1298},
        "modelVersion": "gemini-2.5-flash-image",
    },
    # ---- Imagen :predict -----------------------------------------------------
    "imagen_predict.json": {
        "predictions": [
            {"mimeType": "image/png", "bytesBase64Encoded": PNG_B64},
            {"mimeType": "image/png", "bytesBase64Encoded": PNG_B64},
        ],
    },
    # ---- Anthropic /v1/messages ----------------------------------------------
    "anthropic_chat.json": {
        "id": "msg_fixture01",
        "type": "message",
        "role": "assistant",
        "model": "claude-sonnet-4-20250514",
        "content": [{"type": "text",
                     "text": "Chiaroscuro: dramatic light-dark contrast."}],
        "stop_reason": "end_turn",
        "usage": {"input_tokens": 18, "output_tokens": 11},
    },
}

SSE_FIXTURES = {
    # ---- OpenAI streaming chat (stream_options.include_usage) -------------
    "openai_chat_stream.sse": "\n\n".join([
        'data: {"id":"chatcmpl-f2","object":"chat.completion.chunk","model":"gpt-4o-mini","choices":[{"index":0,"delta":{"role":"assistant","content":""},"finish_reason":null}]}',
        'data: {"id":"chatcmpl-f2","object":"chat.completion.chunk","model":"gpt-4o-mini","choices":[{"index":0,"delta":{"content":"Hello"},"finish_reason":null}]}',
        'data: {"id":"chatcmpl-f2","object":"chat.completion.chunk","model":"gpt-4o-mini","choices":[{"index":0,"delta":{"content":", atelier."},"finish_reason":null}]}',
        'data: {"id":"chatcmpl-f2","object":"chat.completion.chunk","model":"gpt-4o-mini","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}',
        'data: {"id":"chatcmpl-f2","object":"chat.completion.chunk","model":"gpt-4o-mini","choices":[],"usage":{"prompt_tokens":9,"completion_tokens":4,"total_tokens":13}}',
        "data: [DONE]",
    ]) + "\n",
    # ---- Gemini :streamGenerateContent?alt=sse ------------------------------
    "gemini_chat_stream.sse": "\n\n".join([
        'data: {"candidates":[{"content":{"parts":[{"text":"Golden-hour "}],"role":"model"},"index":0}],"usageMetadata":{"promptTokenCount":21,"totalTokenCount":21},"modelVersion":"gemini-2.5-flash"}',
        'data: {"candidates":[{"content":{"parts":[{"text":"glaze."}],"role":"model"},"finishReason":"STOP","index":0}],"usageMetadata":{"promptTokenCount":21,"candidatesTokenCount":8,"totalTokenCount":29},"modelVersion":"gemini-2.5-flash"}',
    ]) + "\n",
    # ---- Anthropic streaming /v1/messages -----------------------------------
    "anthropic_chat_stream.sse": "\n\n".join([
        "event: message_start\n"
        'data: {"type":"message_start","message":{"id":"msg_f2","type":"message","role":"assistant","model":"claude-sonnet-4-20250514","usage":{"input_tokens":10,"output_tokens":1}}}',
        "event: content_block_start\n"
        'data: {"type":"content_block_start","index":0,"content_block":{"type":"text","text":""}}',
        "event: content_block_delta\n"
        'data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"Bonjour"}}',
        "event: content_block_delta\n"
        'data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":" atelier"}}',
        "event: content_block_stop\n"
        'data: {"type":"content_block_stop","index":0}',
        "event: message_delta\n"
        'data: {"type":"message_delta","delta":{"stop_reason":"end_turn"},"usage":{"output_tokens":5}}',
        "event: message_stop\n"
        'data: {"type":"message_stop"}',
    ]) + "\n",
}


def main():
    os.makedirs(FIXTURES, exist_ok=True)
    for name, obj in JSON_FIXTURES.items():
        path = os.path.join(FIXTURES, name)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(obj, fh, indent=2, sort_keys=True)
            fh.write("\n")
        print(f"wrote {path}")
    for name, text in SSE_FIXTURES.items():
        path = os.path.join(FIXTURES, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
