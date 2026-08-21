#!/usr/bin/env python3
"""Assemble TOP100.json from the curated Helix-relevant set."""

from __future__ import annotations

import json
from pathlib import Path

ROWS = [
    (1, "BerriAI/litellm", 56943, "NOASSERTION", "gateway", "Unified 100+ provider router and spend tracking", "spoke + cost table", "https://github.com/BerriAI/litellm"),
    (2, "songquanpeng/one-api", 36517, "MIT", "gateway", "Self-hosted OpenAI-compatible gateway", "keyring table", "https://github.com/songquanpeng/one-api"),
    (3, "QuantumNous/new-api", 45855, "AGPL-3.0", "gateway", "Multi-channel billing gateway", "usage ledger", "https://github.com/QuantumNous/new-api"),
    (4, "Portkey-AI/gateway", 12790, "MIT", "gateway", "Observability-first AI gateway", "redaction + route", "https://github.com/Portkey-AI/gateway"),
    (5, "mudler/LocalAI", 48609, "MIT", "gateway", "Local OpenAI-compatible inference", "openai_compat spoke", "https://github.com/mudler/LocalAI"),
    (6, "open-webui/open-webui", 149488, "NOASSERTION", "studio-ui", "Self-host chat, image gen, BYOK", "settings / model picker", "https://github.com/open-webui/open-webui"),
    (7, "danny-avila/LibreChat", 42311, "MIT", "studio-ui", "Multi-provider chat + agents", "threads / artifacts", "https://github.com/danny-avila/LibreChat"),
    (8, "lobehub/lobe-chat", 81908, "NOASSERTION", "studio-ui", "Polished multi-model client", "provider switch UX", "https://github.com/lobehub/lobe-chat"),
    (9, "chatboxai/chatbox", 41510, "GPL-3.0", "studio-ui", "Desktop BYOK client", "local key UX", "https://github.com/chatboxai/chatbox"),
    (10, "langgenius/dify", 153133, "NOASSERTION", "agent-studio", "Visual agent + RAG studio", "future workflow graph", "https://github.com/langgenius/dify"),
    (11, "langflow-ai/langflow", 153534, "MIT", "agent-studio", "Visual LangChain flows", "node graph idea", "https://github.com/langflow-ai/langflow"),
    (12, "FlowiseAI/Flowise", 55382, "NOASSERTION", "agent-studio", "No-code LLM flows", "tool compose", "https://github.com/FlowiseAI/Flowise"),
    (13, "n8n-io/n8n", 201517, "NOASSERTION", "agent-studio", "Automation with AI nodes", "future loom workers", "https://github.com/n8n-io/n8n"),
    (14, "langchain-ai/langgraph", 40185, "MIT", "agent", "Stateful multi-actor graphs", "conductor phases", "https://github.com/langchain-ai/langgraph"),
    (15, "langchain-ai/langchain", 144725, "MIT", "agent", "Tool and chain abstractions", "pattern only", "https://github.com/langchain-ai/langchain"),
    (16, "crewAIInc/crewAI", 57428, "MIT", "agent", "Role-based crews", "planner/critic roles", "https://github.com/crewAIInc/crewAI"),
    (17, "microsoft/autogen", 60562, "CC-BY-4.0", "agent", "Multi-agent conversations", "message protocol", "https://github.com/microsoft/autogen"),
    (18, "pydantic/pydantic-ai", 19432, "MIT", "agent", "Typed agents", "plan schema", "https://github.com/pydantic/pydantic-ai"),
    (19, "stanfordnlp/dspy", 37478, "MIT", "agent", "Programmatic prompting", "planner compile", "https://github.com/stanfordnlp/dspy"),
    (20, "567-labs/instructor", 13760, "MIT", "agent", "Structured JSON from LLMs", "extract_json", "https://github.com/567-labs/instructor"),
    (21, "dottxt-ai/outlines", 15659, "Apache-2.0", "agent", "Constrained generation", "future grammar plans", "https://github.com/dottxt-ai/outlines"),
    (22, "microsoft/semantic-kernel", 28477, "MIT", "agent", "Skills kernel", "brand kit as skill", "https://github.com/microsoft/semantic-kernel"),
    (23, "FoundationAgents/MetaGPT", 69936, "MIT", "agent", "SOP multi-agent company", "role SOPs", "https://github.com/FoundationAgents/MetaGPT"),
    (24, "OpenBMB/ChatDev", 34086, "Apache-2.0", "agent", "Chat-powered org", "critique loop", "https://github.com/OpenBMB/ChatDev"),
    (25, "Significant-Gravitas/AutoGPT", 186719, "NOASSERTION", "agent", "Autonomous loop reference", "hard phase cap", "https://github.com/Significant-Gravitas/AutoGPT"),
    (26, "run-llama/llama_index", 51790, "MIT", "agent", "Data / RAG index", "asset memory later", "https://github.com/run-llama/llama_index"),
    (27, "infiniflow/ragflow", 88983, "Apache-2.0", "agent", "RAG engine", "reference boards", "https://github.com/infiniflow/ragflow"),
    (28, "Comfy-Org/ComfyUI", 128817, "GPL-3.0", "image", "Node graph local gen", "optional loom worker", "https://github.com/Comfy-Org/ComfyUI"),
    (29, "AUTOMATIC1111/stable-diffusion-webui", 164605, "AGPL-3.0", "image", "Canonical local SD UI", "optional worker", "https://github.com/AUTOMATIC1111/stable-diffusion-webui"),
    (30, "lllyasviel/Fooocus", 52461, "GPL-3.0", "image", "Opinionated SDXL studio", "fewer knobs", "https://github.com/lllyasviel/Fooocus"),
    (31, "invoke-ai/InvokeAI", 27923, "Apache-2.0", "image", "Pro local canvas gen", "unified canvas UX", "https://github.com/invoke-ai/InvokeAI"),
    (32, "lllyasviel/stable-diffusion-webui-forge", 12966, "AGPL-3.0", "image", "Performance SD fork", "optional worker", "https://github.com/lllyasviel/stable-diffusion-webui-forge"),
    (33, "huggingface/diffusers", 34347, "Apache-2.0", "image", "Diffusers pipelines", "future local spoke", "https://github.com/huggingface/diffusers"),
    (34, "huggingface/transformers", 164311, "Apache-2.0", "image", "Model runtime", "future local spoke", "https://github.com/huggingface/transformers"),
    (35, "lllyasviel/ControlNet", 34076, "Apache-2.0", "image", "Structure-conditioned gen", "touch-edit analog", "https://github.com/lllyasviel/ControlNet"),
    (36, "Mikubill/sd-webui-controlnet", 17847, "GPL-3.0", "image", "ControlNet in A1111", "optional", "https://github.com/Mikubill/sd-webui-controlnet"),
    (37, "Stability-AI/generative-models", 27267, "MIT", "image", "Official Stability generators", "route note", "https://github.com/Stability-AI/generative-models"),
    (38, "black-forest-labs/flux", 25898, "Apache-2.0", "image", "FLUX family", "route note", "https://github.com/black-forest-labs/flux"),
    (39, "Comfy-Org/ComfyUI-Manager", 15855, "GPL-3.0", "image", "Comfy custom-node manager", "optional ops", "https://github.com/Comfy-Org/ComfyUI-Manager"),
    (40, "cubiq/ComfyUI_IPAdapter_plus", 6105, "GPL-3.0", "image", "Reference identity", "visual brand lock", "https://github.com/cubiq/ComfyUI_IPAdapter_plus"),
    (41, "excalidraw/excalidraw", 130157, "MIT", "canvas", "Infinite whiteboard", "board gestures", "https://github.com/excalidraw/excalidraw"),
    (42, "tldraw/tldraw", 49894, "NOASSERTION", "canvas", "Infinite canvas SDK", "future board engine", "https://github.com/tldraw/tldraw"),
    (43, "fabricjs/fabric.js", 31398, "MIT", "canvas", "Object 2d canvas", "layer model", "https://github.com/fabricjs/fabric.js"),
    (44, "konvajs/konva", 14708, "NOASSERTION", "canvas", "2d scene graph", "node drag", "https://github.com/konvajs/konva"),
    (45, "pixijs/pixijs", 48042, "MIT", "canvas", "WebGL scene", "future zoom", "https://github.com/pixijs/pixijs"),
    (46, "paperjs/paper.js", 15065, "NOASSERTION", "canvas", "Vector scripting", "vector notes", "https://github.com/paperjs/paper.js"),
    (47, "GrapesJS/grapesjs", 26152, "NOASSERTION", "design-editor", "Web builder", "layout blocks", "https://github.com/GrapesJS/grapesjs"),
    (48, "penpot/penpot", 58984, "MPL-2.0", "design-editor", "Open design tool", "export ideas", "https://github.com/penpot/penpot"),
    (49, "jgraph/drawio", 7632, "Apache-2.0", "design-editor", "Diagram canvas", "board export", "https://github.com/jgraph/drawio"),
    (50, "photopea/photopea", 8400, "NOASSERTION", "design-editor", "Browser PSD editor", "touch-edit inspiration", "https://github.com/photopea/photopea"),
    (51, "remotion-dev/remotion", 56992, "NOASSERTION", "video", "Programmatic video", "future loom video", "https://github.com/remotion-dev/remotion"),
    (52, "FFmpeg/FFmpeg", 63513, "NOASSERTION", "video", "Transcode / compose", "future worker", "https://github.com/FFmpeg/FFmpeg"),
    (53, "guoyww/AnimateDiff", 12217, "Apache-2.0", "video", "Image-to-motion", "optional", "https://github.com/guoyww/AnimateDiff"),
    (54, "kijai/ComfyUI-WanVideoWrapper", 6670, "Apache-2.0", "video", "Wan video in Comfy", "optional", "https://github.com/kijai/ComfyUI-WanVideoWrapper"),
    (55, "openai/whisper", 107740, "MIT", "audio", "Speech recognition", "voice brief later", "https://github.com/openai/whisper"),
    (56, "ggml-org/whisper.cpp", 53083, "MIT", "audio", "Local whisper", "optional", "https://github.com/ggml-org/whisper.cpp"),
    (57, "suno-ai/bark", 39246, "MIT", "audio", "Generative audio", "audio stub", "https://github.com/suno-ai/bark"),
    (58, "coqui-ai/TTS", 45929, "MPL-2.0", "audio", "Local TTS", "audio stub", "https://github.com/coqui-ai/TTS"),
    (59, "ollama/ollama", 179116, "MIT", "local-llm", "Local model runner", "ollama spoke", "https://github.com/ollama/ollama"),
    (60, "ggml-org/llama.cpp", 125013, "MIT", "local-llm", "GGUF runtime", "future spoke", "https://github.com/ggml-org/llama.cpp"),
    (61, "vllm-project/vllm", 89645, "Apache-2.0", "local-llm", "Fast local serving", "openai_compat", "https://github.com/vllm-project/vllm"),
    (62, "nomic-ai/gpt4all", 77398, "MIT", "local-llm", "Local desktop models", "compat spoke", "https://github.com/nomic-ai/gpt4all"),
    (63, "mozilla-ai/llamafile", 25666, "NOASSERTION", "local-llm", "Single-file local LLM", "compat", "https://github.com/mozilla-ai/llamafile"),
    (64, "lm-sys/FastChat", 39515, "Apache-2.0", "local-llm", "FastChat serve", "compat", "https://github.com/lm-sys/FastChat"),
    (65, "xorbitsai/inference", 9504, "Apache-2.0", "local-llm", "Xinference multi-model", "compat", "https://github.com/xorbitsai/inference"),
    (66, "openai/openai-python", 31426, "Apache-2.0", "sdk", "Official OpenAI SDK", "HTTP contract", "https://github.com/openai/openai-python"),
    (67, "openai/openai-node", 11127, "Apache-2.0", "sdk", "Official OpenAI Node SDK", "HTTP contract", "https://github.com/openai/openai-node"),
    (68, "googleapis/python-genai", 3929, "Apache-2.0", "sdk", "Official Gemini SDK", "HTTP contract", "https://github.com/googleapis/python-genai"),
    (69, "anthropics/anthropic-sdk-python", 3842, "MIT", "sdk", "Official Anthropic SDK", "future spoke", "https://github.com/anthropics/anthropic-sdk-python"),
    (70, "vercel/ai", 26337, "NOASSERTION", "sdk", "Vercel AI SDK", "streaming later", "https://github.com/vercel/ai"),
    (71, "langfuse/langfuse", 33525, "NOASSERTION", "observability", "LLM traces and cost", "usage events", "https://github.com/langfuse/langfuse"),
    (72, "traceloop/openllmetry", 7387, "Apache-2.0", "observability", "OpenTelemetry for LLMs", "future traces", "https://github.com/traceloop/openllmetry"),
    (73, "chroma-core/chroma", 29119, "Apache-2.0", "memory", "Embedding DB", "asset search later", "https://github.com/chroma-core/chroma"),
    (74, "qdrant/qdrant", 34115, "Apache-2.0", "memory", "Vector search", "future", "https://github.com/qdrant/qdrant"),
    (75, "milvus-io/milvus", 45728, "Apache-2.0", "memory", "Vector DB", "future", "https://github.com/milvus-io/milvus"),
    (76, "weaviate/weaviate", 16745, "BSD-3-Clause", "memory", "Vector search", "future", "https://github.com/weaviate/weaviate"),
    (77, "HKUDS/LightRAG", 39062, "MIT", "memory", "Graph RAG", "future memory", "https://github.com/HKUDS/LightRAG"),
    (78, "pocketbase/pocketbase", 60760, "MIT", "backend", "Single-file backend", "alt to sqlite", "https://github.com/pocketbase/pocketbase"),
    (79, "minio/minio", 61382, "AGPL-3.0", "backend", "S3-compatible artifacts", "future object store", "https://github.com/minio/minio"),
    (80, "All-The-Vibes/ATV-Design", 5, "MIT", "byok-design", "Local-first BYOK design agent", "cousin, not vendored", "https://github.com/All-The-Vibes/ATV-Design"),
    (81, "1nkfox/open-design", 0, "Apache-2.0", "byok-design", "Skill-driven design harness", "skills idea", "https://github.com/1nkfox/open-design"),
    (82, "JustinPerea/nebula-nodes", 16, "AGPL-3.0", "byok-design", "Node media canvas + BYOK", "loom graph later", "https://github.com/JustinPerea/nebula-nodes"),
    (83, "manujajay/manudesign", 3, "MIT", "byok-design", "Studio + compose + canvas", "brand presets", "https://github.com/manujajay/manudesign"),
    (84, "binary-husky/gpt_academic", 71224, "GPL-3.0", "studio-ui", "Academic multimodal BYOK UI", "key UX", "https://github.com/binary-husky/gpt_academic"),
    (85, "chatchat-space/Langchain-Chatchat", 38563, "Apache-2.0", "studio-ui", "Local knowledge + models", "RAG later", "https://github.com/chatchat-space/Langchain-Chatchat"),
    (86, "Cinnamon/kotaemon", 25708, "Apache-2.0", "studio-ui", "RAG document UI", "refs", "https://github.com/Cinnamon/kotaemon"),
    (87, "opencv/opencv", 90539, "Apache-2.0", "vision", "Image operations", "local touch-edit", "https://github.com/opencv/opencv"),
    (88, "pytorch/pytorch", 102518, "NOASSERTION", "runtime", "Training / inference", "local workers", "https://github.com/pytorch/pytorch"),
    (89, "mrdoob/three.js", 114659, "MIT", "canvas", "3D web renderer", "future 3D board", "https://github.com/mrdoob/three.js"),
    (90, "mozilla/pdf.js", 53762, "Apache-2.0", "export", "PDF renderer", "export later", "https://github.com/mozilla/pdf.js"),
    (91, "niklasvh/html2canvas", 31913, "MIT", "export", "DOM to canvas", "board flatten", "https://github.com/niklasvh/html2canvas"),
    (92, "facebookresearch/segment-anything", 54738, "Apache-2.0", "vision", "Segment anything", "touch-edit mask", "https://github.com/facebookresearch/segment-anything"),
    (93, "ultralytics/ultralytics", 60839, "AGPL-3.0", "vision", "YOLO vision stack", "layout detect later", "https://github.com/ultralytics/ultralytics"),
    (94, "google-ai-edge/mediapipe", 36685, "Apache-2.0", "vision", "On-device vision", "optional", "https://github.com/google-ai-edge/mediapipe"),
    (95, "hiyouga/LlamaFactory", 74281, "Apache-2.0", "local-llm", "Fine-tune factory", "out of MVP", "https://github.com/hiyouga/LlamaFactory"),
    (96, "unslothai/unsloth", 74233, "Apache-2.0", "local-llm", "Fast fine-tune", "out of MVP", "https://github.com/unslothai/unsloth"),
    (97, "mlc-ai/mlc-llm", 23079, "Apache-2.0", "local-llm", "Compile LLMs for devices", "future", "https://github.com/mlc-ai/mlc-llm"),
    (98, "OpenRouterTeam/openrouter-examples", 372, "MIT", "gateway", "OpenRouter examples — we do not require their proxy", "compat mapping only", "https://github.com/OpenRouterTeam/openrouter-examples"),
    (99, "yoheinakajima/babyagi", 22355, "NOASSERTION", "agent", "Tiny task loop", "phase cap reminder", "https://github.com/yoheinakajima/babyagi"),
    (100, "TransformerOptimus/SuperAGI", 17658, "MIT", "agent", "Agent toolkit", "tool registry idea", "https://github.com/TransformerOptimus/SuperAGI"),
]


def main() -> None:
    assert len(ROWS) == 100, len(ROWS)
    names = [r[1] for r in ROWS]
    assert len(names) == len(set(names)), "duplicate repos"
    categories: dict[str, int] = {}
    projects = []
    for rank, repo, stars, license_, category, why, integrate_as, url in ROWS:
        categories[category] = categories.get(category, 0) + 1
        projects.append({
            "rank": rank,
            "repo": repo,
            "stars_approx": stars,
            "license": license_,
            "category": category,
            "why": why,
            "integrate_as": integrate_as,
            "url": url,
        })
    payload = {
        "title": "Atelier Helix TOP100",
        "captured_at": "2026-08-21",
        "architecture": "Helix",
        "rule": "Integrate patterns and official APIs. Do not vendor monorepos. No unofficial ChatGPT website clients.",
        "mvp_wire": [
            "BerriAI/litellm",
            "open-webui/open-webui",
            "Comfy-Org/ComfyUI",
            "excalidraw/excalidraw",
            "tldraw/tldraw",
            "fabricjs/fabric.js",
            "langchain-ai/langgraph",
            "567-labs/instructor",
            "openai/openai-python",
            "googleapis/python-genai",
            "ollama/ollama",
            "langfuse/langfuse",
            "invoke-ai/InvokeAI",
            "danny-avila/LibreChat",
            "All-The-Vibes/ATV-Design",
        ],
        "categories": categories,
        "projects": projects,
    }
    out = Path(__file__).with_name("top100.json")
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {len(projects)} -> {out}")


if __name__ == "__main__":
    main()
