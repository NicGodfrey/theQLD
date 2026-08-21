# Atelier → 成品可用：线上差距（主分析稿）

十路 Opus 军团正在对十个切片出独立 GAPS。本文是对照**线上** `atelier/helix` + `atelier/web` 与验收清单的主稿，军团回报后并入 `FLEET.md`。

**成品可用（v1，本地 BYOK）定义**：非开发者装好官方 API key 后，能独立完成「建项目 → 写 brief → 出图钉到画布 → 改一句再出一张 → 下载文件」，过程中看得见花费、失败有人话、数据不丢。不是 Lovart 全量对位。

## 现在已经能做的

- `python3 -m atelier` 起本地工作室；demo 无密钥也能钉 SVG。
- 项目 / 线程 / 消息 / 画布节点 / 用量账本（SQLite）。
- OpenAI / Gemini / Ollama spoke，官方主机约束（Gemini/OpenAI 有 `assert_official_host`）。
- thinking/fast、brand_kit JSON、密钥红acted 状态。
- 研究树里有几乎完整的下一版（SSE 画布、OpenAPI、68 spoke 测、Conductor 协议）。

## 阻断「给外人用」的缺口

| 严重度 | 差距 | 证据 | 最小修法 |
|---|---|---|---|
| Blocker | 生成前不报价、失败静默降级 demo | `conductor.py` 捕获 `SpokeError` 后仍 `build_spoke("demo")` | 失败必须显示「密钥无效/额度不足」，禁止悄悄换成 SVG 冒充成功 |
| Blocker | 无流式、weave 同步阻塞 UI | `POST /api/threads/:id/run` 一次返回 | 先加进度 JSON 或 SSE；研究 UI 已有协议 |
| Blocker | 无上传、无导出按钮 | live `web/app.js` 只有 Weave + 拖节点 | 加「下载此图」+ 拖放参考图 |
| Blocker | 安装路径不友好 | 必须在仓库根 `python3 -m atelier` | `pyproject` console_script + 一页向导 |
| Major | 画布无平移缩放 / 200 节点性能 | live board 绝对定位堆叠 | 接入研究 `06-board-ui` 或先做 camera |
| Major | 计划不可见、无 4 变体挑选 | Conductor 把 plan 埋进 assistant 文本 | 返回 `plan` 卡片；weave count=4 网格 |
| Major | 无局部编辑 / 真文字层 / 撤销 | 只有整图重织 | v1 可先做「基于上一张再提示」+ 节点删除 |
| Major | 预算闸只在账本、UI 不展示将花多少 | `usage.assert_budget` 不预估下一张图 | 点 Weave 前显示估费 |
| Major | 研究 API ≠ 线上 API | `/api/chat` SSE vs `/api/threads/:id/run` | 选定一条契约再接线 |
| Major | 测试太薄 | live 7 测 vs 研究 58 测，无 CI | 先移植 spoke fixture + 一条 API 烟测 |
| Major | key 失败被当成成功 | 见上 demo fallback | 同上 |
| Minor | 无删除项目/线程、无迁移 | `store.py` 只有 insert/update node | 加 delete + 备份说明 |
| Minor | 无视频/音频 | loom 线上几乎只有 SVG 写盘 | v1 可标「未交付」 |
| Minor | 站点挂在 theQLD 法律目录仓 | `atelier.html` 只是入口 | 文档写清「本地工具，不是 Pages 应用」 |
| Minor | Atelier 子树无 LICENSE | 根仓也无明确 Atelier 许可 | 加 MIT + 生成物版权归用户/模型条款 |

## 对照 M 验收（直播状态）

- M-1 项目画布：PARTIAL（能建项目/线程，无无限画布性能、无空态 2s 指标）。
- M-2 代理：PARTIAL（fast/thinking 有，无计划卡、无指代消解、无澄清问题）。
- M-3 出图：PARTIAL（双引擎代码在，无报价、无 4 宫格、无视频）。
- M-4 编辑：MISSING。
- M-5 Brand：PARTIAL（JSON textarea，无色板/字体/合规 ΔE）。
- M-6 导出与套餐：MISSING（无水印策略、无 PNG/PDF 导出 UI；账本有事件无「本回合费用」展示）。

Lovart 级 P2（多模型视频、3D、PSD 图层、团队、公开 API）全部是 **后置**，不挡 v1。

## 建议的 v1 收口顺序（技术）

1. 去掉「失败变 demo」；错误回到 dock。
2. 节点「下载」+ 参考图上传。
3. Weave 前估费（`usage.estimate_usd`）。
4. 统一 API：给 live server 补 `GET /api/providers`、上传、artifact `Content-Disposition` 文件名。
5. 把研究画布的 camera/upload 迁到 live `web/`（不必一次上 SSE）。
6. Conductor 把 `plan.weave` 展示成可勾选步骤。
7. `pyproject.toml` + `atelier` 命令 + README 五步向导。
8. 移植 `03-keyring-spokes` 的 redirect 禁用与 OpenAI `base_url` 拒绝。
9. GitHub Action：`python3 -m unittest atelier.tests.test_helix`。
10. 写清：ChatGPT Plus ≠ API；生成物按 OpenAI/Google 条款。

Opus 军团切片目录：`/tmp/atelier-opus/0{1..10}-*/GAPS.md`（完成后拷入本目录）。
