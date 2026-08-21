# Opus 军团：成品差距分析

十路 `claude-opus-5-thinking-high` 对照 **当时** 的 live Helix。报告写于 20 轮自进化落地之前，按快照阅读。

| # | 切片 | 报告 | 20 轮之后 |
|---|---|---|---|
| 01 | 产品对位 | [01-product.md](01-product.md) | 快照 @ `1bfa56d`；R4–R7 后又关了下载/上传父级/镜头/计划卡 |
| 02 | BYOK / 安全 / 额度 | [02-security.md](02-security.md) | 无跳转 + 估费 402；**本轮补** 路径穿越 / `file://` / keyring 0600 / Host |
| 03 | API 三方错位 | [03-api.md](03-api.md) | 见 `evolve/CONTRACT.md` |
| 04 | Conductor | [04-conductor.md](04-conductor.md) | fail-closed；研究 Conductor 仍未整包移植 |
| 05 | 媒资 Loom | [05-media.md](05-media.md) | 下载后缀已修；宽高比仍缺 |
| 06 | 前端 UX | [06-frontend.md](06-frontend.md) | 镜头已上；**不要**整包换 research Board |
| 07 | Memory | [07-memory.md](07-memory.md) | WAL + 请求锁；无完整迁移器 |
| 08 | 测试 / CI | [08-test.md](08-test.md) | `test_evolve` + workflow 已上 |
| 09 | 安装交付 | [09-ship.md](09-ship.md) | `__main__.py` 任意 cwd |
| 10 | 许可 / 集成 | [10-license.md](10-license.md) | `atelier/LICENSE`；catalog boundary 未改 |

主稿：[`LIVE-DRAFT.md`](LIVE-DRAFT.md)

**仍不要做：** 把 `research/fable5/06-board-ui` 直接换成 live web（契约仍是 `/api/chat`）。
