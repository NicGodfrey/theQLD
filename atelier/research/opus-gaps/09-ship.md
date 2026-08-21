# 09 · 安装交付 GAPS —— 「陌生人今天就想用 Atelier」

Opus#9 / 10。切片：**安装、启动、打包、首次运行 UX、交付形态**。
方法：只读 `/workspace`，实测在 `/tmp/atelier-opus/09-ship-gaps/clone`（`git clone /workspace`）里跑真服务、真 HTTP、真失败路径。**未修改 `/workspace` 任何文件。**

读过：`atelier/README.md`、`atelier.html`、`atelier/server.py`、`atelier/__main__.py`、`atelier/__init__.py`、`atelier/helix/{keyring,store,conductor,loom,usage,catalog}.py`、`atelier/helix/spokes/*`、`atelier/web/*`、`atelier/.gitignore`、根仓 `CNAME` / `404.md` / `index.html`。
不存在：`pyproject.toml`、`setup.py`、`requirements.txt`、`Makefile`、`LICENSE`、`CHANGELOG.md`、`.github/`、`.cursor/environment.json`、根 `README`、git tag。

---

## 0. 判决（TL;DR）

**代码能跑，产品不能交付。** 一个陌生人 clone 之后 90 秒内确实能看到画布和一张 demo SVG（stdlib-only，冷启动约 1s，demo weave 19ms——这些是真实优势）。但把 key 贴进去之后，他会经历三件足以让他关掉页面并且不再回来的事：

1. **key 不对 / 网络不通 / provider 挂了 → 界面说「成功」。** 服务器返回 `200`，dock 里写 `Route: openai / gpt-4o-mini · Pinned 1 artifact(s)`，画布上钉的是 demo SVG。spoke 里那句写得很好的人话错误（"OpenAI key missing. Set OPENAI_API_KEY…"）被 `except SpokeError` 吞掉扔了。用户学到的是「这工具会假装干活」，这比崩溃更致命。
2. **「你的 key 留在本机」这句承诺当前是假的。** 本地服务器有未授权任意文件读取（`GET /../../../.atelier/keyring.json` → `200` + 明文 key，实测已复现），且没有任何 Origin / token 校验（跨站 `text/plain` POST 直接 `201`）。对一个 BYOK 工具，这不是安全 backlog，这是**产品定义被推翻**。
3. **安装路径只有一条窄缝。** 必须 `cd` 到仓库根，必须叫 `python3 -m atelier`，`pip install` 不可能，`--help` 被忽略（直接起服务），端口占用/端口写错/端口没权限一律甩 Python traceback。

同时，**Atelier 现在不是一个可交付物**：它住在 `NicGodfrey/theQLD` 这个昆士兰法律目录站里（201 个 tracked 文件，88 个是律所站；clone 59M）。陌生人为了一个设计工作室，要下载一整个法律信息网站，然后被告知在仓库根跑一条命令。`theqld.com/atelier.html` 是一张营销页，给的是同一条命令，**没有 clone 指令、没有仓库链接、没有下载、没有平台说明**——而 GitHub Pages 永远跑不了这个后端。

**结论：v1 的工作量重心不在 Conductor 或画布，而在"交付面"。** 现在缺的不是功能，是"这东西是个软件产品"的那一层：一个包、一个命令、一个向导、一句人话错误、一个数据落点、一个版本号。

---

## 1. 「成品可用」对本地 BYOK 工具意味着什么（不是 SaaS）

主稿 `LIVE-DRAFT.md` 的定义（非开发者装好 key 后能走通 建项目→brief→出图→改一句再出→下载，看得见花费、失败有人话、数据不丢）是对的。我从**交付**角度把它补成可判定的十条，并标注现状。

> 关键区别：SaaS 可以用运营补 UX——客服、状态页、热修、灰度、状态监控。**本地工具没有运营。** 用户机器上那一份就是全部。首次运行的每一个失败都是永久失败：他不会提 issue，他会关掉终端。所以本地工具必须把"运营"编译进二进制：向导代替客服，doctor 代替状态页，人话错误代替工单，CHANGELOG 代替发布公告。
>
> 反过来，本地工具**可以合法地不做** SaaS 必做的事：没有多租户、没有登录、没有 HTTPS 证书、没有水平扩展、没有 SLA、没有遥测（而且**不该有**遥测）。省这些是正确的，不是偷懒。
>
> 但有一类东西两边都不能省，而且本地更严：**密钥安全**。SaaS 泄密是公司出事；本地泄密是用户自己的 OpenAI 账单被人刷，他没有客服可以打电话。本地工具对"key 不外流"的标准应当**高于** SaaS，因为受害者无处求偿。

| # | 交付验收（D-item） | 判定标准 | 现状 |
|---|---|---|---|
| D-1 | **一条命令可得** | 从"看到项目"到"服务在跑" ≤ 3 步、无需理解 Python 打包；`pipx install` / `uv tool install` / release zip 至少一条通 | **FAIL** — 只有 `cd 仓库根 && python3 -m atelier`；`pip install ./repo` 报 `Neither 'setup.py' nor 'pyproject.toml' found` |
| D-2 | **首次到第一张图 ≤ 5 分钟** | 含贴 key、验证 key、知道会花多少钱 | **PARTIAL** — demo 图 90 秒可得（好）；真 key 路径没有验证、没有预估、失败不报 |
| D-3 | **三平台可用且被写下来** | Windows / macOS / Linux 各有确切命令与已知坑 | **FAIL** — 文档零平台差异；`python3` 在 Windows 上不存在，`os.chmod(0600)` 在 Windows 上不保护任何东西 |
| D-4 | **失败可读** | 任何失败给一行人话 + 下一步动作，绝不 traceback、绝不假装成功 | **FAIL** — 静默降级 demo（200 OK）、`URLError` 未捕获（500 + 原始 urllib 文本）、端口三种错法全是 traceback |
| D-5 | **钱可见** | 点击前估费、点击后记账、失败明确"没花钱" | **PARTIAL** — 账本齐全，UI 只显示累计；`assert_budget` 是**事后**校验，第一次超预算的钱已经花完了，且抛 `BudgetExceeded` → 500 |
| D-6 | **数据可指认、可备份、可整删** | 用户知道数据在哪、怎么备份、怎么连 key 一起抹掉；移动目录不坏 | **FAIL** — 状态劈成两半（key 在 `~/.atelier`，作品在 `<仓库>/atelier/.runtime`）；artifacts 存**绝对路径**，重命名目录后整块画布 404；`.runtime` 被 gitignore，`git clean -xdf` 会删掉用户全部作品 |
| D-7 | **密钥不外流** | 本机服务不得把 keyring 交给任何未授权请求；任何非官方 host 出口必须显式同意 | **FAIL** — 任意文件读取已复现；无 Origin/token 校验；`openai_compat` 静默绕过 host 锁且 README 未提 |
| D-8 | **可自诊断** | 一个 `doctor` 子命令 + 一个日志文件，用户能自助 | **FAIL** — 无 doctor、无日志文件（只有 stderr）、无 `--help`、无 `--version` |
| D-9 | **版本可指认** | `--version` / `/api/health` / UI 角落一致；CHANGELOG；可回滚 | **FAIL** — `__version__ = "0.1.0"` 无人读取；`/api/health` 不含版本；无 CHANGELOG、无 tag、无 release |
| D-10 | **法律面完整** | LICENSE、生成物权属、"ChatGPT Plus ≠ API"、第三方条款 | **PARTIAL** — README 已写 Plus≠API（好）；**整仓无 LICENSE**（切片 10 主责） |

**十条里 6 个 FAIL、3 个 PARTIAL、0 个 PASS。** 这就是"能跑"和"能交付"之间的距离。

---

## 2. 首次运行实测：逐条证据

全部命令可复现，服务跑在 `/tmp` 的 clone 上，`ATELIER_HOME` / `ATELIER_RUNTIME` 指向 `/tmp`。

### 2.1 `python -m atelier` 与工作目录

| 场景 | 命令 | 观测 |
|---|---|---|
| 任意目录 | `cd /tmp && python3 -m atelier` | `/usr/bin/python3: No module named atelier` |
| **包目录里面**（最容易犯） | `cd theQLD/atelier && python3 -m atelier` | `No module named atelier` |
| 仓库根（唯一正确） | `cd theQLD && python3 -m atelier` | 起来了 |
| 直接跑文件 | `cd theQLD/atelier && python3 server.py` | 起来了（`server.py` 自己把 `REPO` 插进 `sys.path`），但 `python3 server.py` 没写在任何文档里 |

根因：`__main__.py` 与 `spokes/base.py` 用绝对导入 `from atelier.server import main` / `from atelier.helix.loom import demo_svg`，所以**包的父目录必须在 `sys.path`**，实际等价于"cwd 必须是仓库根"。README 那行 `python3 -m atelier` 前面缺的正是 `git clone … && cd theQLD`。

`server.py:15-19` 自己插 `sys.path` 是个"半修"：它让 `python3 server.py` 能跑，却让人误以为路径问题已解决。真正的修法是 console_script。

### 2.2 打包与安装

```
$ python3 -m pip install ./clone
ERROR: Directory './clone' is not installable. Neither 'setup.py' nor 'pyproject.toml' found.
```

后果：`pip install git+https://github.com/NicGodfrey/theQLD`、`pipx install`、`uv tool install`、`pip install -e .`、`python -m venv` 后一键装——**全部不可能**。唯一路径是 clone 整个律所站 + 手动 cd。

**唯一的好消息（要保住）**：shipping code 是**纯 stdlib**。实测 import 清单只有 `base64 dataclasses functools hashlib html http json mimetypes os pathlib re sqlite3 sys tempfile time typing unittest urllib uuid`。没有 numpy、没有 requests、没有 node。**这意味着 Atelier 可以做成"一个 pyproject + 零依赖"的 pipx 工具，install 故事可以极其干净。** 现在只是没人写那 20 行 TOML。

顺带：全部 `.py` 用 `ast.parse(feature_version=(3,9))` 均可解析，即语法层面 3.9 应当没问题——但**没有声明最低 Python 版本，也没有 CI 验证过 3.9/3.10**。macOS 自带 3.9、Debian oldstable 3.9，这是个必须写进 `requires-python` 并跑矩阵才敢说的事。

### 2.3 启动器（CLI）人话程度

| 输入 | 期望 | 实际 |
|---|---|---|
| `python3 -m atelier --help` | 用法说明 | **忽略参数，直接起服务**（最坏的一种：用户以为自己在看帮助，其实开了个监听端口） |
| `python3 -m atelier --version` | `0.1.0` | 同上，起服务 |
| 端口被别的程序占用 | 「8765 被占用，改用 8766？」 | `OSError: [Errno 98] Address already in use` + 8 行 traceback |
| `ATELIER_PORT=abc` | 「端口必须是数字」 | `ValueError: invalid literal for int() with base 10: 'abc'` |
| `ATELIER_PORT=80` | 「需要管理员权限，换个端口」 | `PermissionError: [Errno 13] Permission denied` |
| 启动成功 | 自动开浏览器 | 只打印 URL，用户得自己复制粘贴（Windows 双击 .py 的场景下 console 一闪而过，URL 都看不到） |

还有：`server.py` 在**模块导入期**就 `APP = App()`（第 54 行），于是 `import atelier.server` 这个动作本身就会建 `~/.atelier/`、建 `.runtime/`、建 sqlite、插入 "Atelier Studio" 示例项目。任何 import 期异常（磁盘满、目录只读、sqlite 锁）都变成 import traceback 而不是可处理的启动错误。

### 2.4 密钥体验（没有向导）

- **没有向导。** 首屏是完整工作室：Projects / Threads / Keys / Brand kit / Conductor 全部铺开。新用户不知道先干哪个，也不知道"不贴 key 也能玩 demo"。
- **没有验证。** `POST /api/keys` 只写盘，不试调。`/api/keys` 的 `configured: true` 只表示"有个字符串"，不表示能用。实测：`OPENAI_API_KEY=sk-bogus-not-a-real-key` → 状态栏显示绿的 `openai:env`。
- **没有删除。** `Keyring.delete()` 存在，但 server 没有 `do_DELETE`，UI 也没有按钮。想删 key 只能手工编辑 `~/.atelier/keyring.json`。
- **有个用不了的 provider。** `/api/keys` 返回 5 个 provider 含 `anthropic`（`ENV_MAP` 里有），但 `build_spoke()` 没有 anthropic 分支 → 选它等于选 demo。UI 下拉框也不列它。用户看到 anthropic 状态位却无处使用。
- **文档写了一个不生效的开关。** README 表格写 `Ollama | OLLAMA_HOST | 127.0.0.1`。但 `keyring.ENV_MAP["ollama"] = "OLLAMA_HOST"` 是走 **`get_secret()`** 的，`get_base_url()` 只读 keyring 文件里的 `base_url`。所以 `export OLLAMA_HOST=http://localhost:11434` 的效果是"把它当成密钥"，**不会改变请求地址**。
- **有个没写进文档的绕过口。** UI Keys 下拉里的 `OpenAI-compatible` → `build_spoke("openai_compat")` → `OpenAISpoke._url()` 跳过 `assert_official_host`（`openai_spoke.py:32-33`），任意 base_url 都接受。README 通篇没提 `openai_compat`。一个以"只发往官方 host"为卖点的工具，在 UI 里放了一个没有任何警示文案的任意出口。
- **keyring 落盘时序**：`_save()` 先 `write_text()` 再 `os.chmod(0600)` —— 存在一个明文 `0644` 的窗口；且 `path.parent.mkdir()` 用默认权限（`0755`），`~/.atelier` 目录本身对同机其他用户可读。Windows 上 `os.chmod` 对 ACL 基本无效（`OSError` 被 `except OSError: pass` 静静吞掉），即 **Windows 上 keyring 实质是明文无保护文件**，而 README 承诺 "mode 0600"。

### 2.5 失败路径（交付层最贵的 bug）

**A. 静默降级：失败被当成成功。** `conductor.py:158-164`：
```python
try:
    image_spoke = build_spoke(plan["route"].get("provider") or provider, self.keyring)
    woven = image_spoke.image(item_prompt, model=image_model)
except SpokeError:
    image_spoke = build_spoke("demo", self.keyring)
    woven = image_spoke.image(item_prompt, model="demo-svg")
```
实测（**完全没有 key**，provider=openai，mode=thinking）：
```
HTTP 200
message:
  Helix thinking · clinic poster
  Route: openai / gpt-4o-mini          <-- 谎报路由
  Pinned 1 artifact(s) onto the board.
  Critique: Thinking pass stored the plan; critic skipped (provider unavailable).
artifact provider/model: [('demo', 'demo-svg')]     <-- 实际是 demo
```
`fast` 模式下连 "provider unavailable" 那半句提示都没有——**零线索**。响应里也没有 `error` / `degraded` / `fallback` 字段可供前端识别。同一条路径覆盖：key 缺失、key 过期、余额不足、429、模型名写错、Ollama 没开（实测 ollama 未启动 → `Ollama unreachable` → 静默 demo，200）。

这是整个仓库**最贵的一行代码**：它把所有可诊断的 BYOK 故障，转换成"这工具生成质量很差"的用户结论。

**B. 断网 / 代理 / VPN → 500 + 原始 traceback 文本。** `openai_spoke._post` 和 `gemini_spoke._post` 只 catch `HTTPError`，**不 catch `URLError`**（只有 `ollama_spoke` catch 了）。实测：
```
$ (http_proxy 指向死端口) spoke.chat(...)
UNHANDLED urllib.error.URLError : <urlopen error [Errno 111] Connection refused>
```
`URLError` 不是 `SpokeError`，`conductor` 的 `except (SpokeError, ValueError, JSONDecodeError)` 抓不到 → 冒到 `server.py:210` 的 `except Exception` → dock 状态栏显示 `<urlopen error [Errno -2] Name or service not known>`。咖啡馆 captive portal、公司代理、飞机上——首次运行最常见的环境——得到的就是这句。

**C. 预算闸是事后的。** `usage.record()` 在**调用之后**才 `assert_budget()`，所以第一笔超预算支出必然已经发生；`BudgetExceeded` 是 `RuntimeError` 而非 `SpokeError`，冒到 server → 500。用户看到的是"报错了"，而不是"你今天的 $10 用完了"。默认 `ATELIER_DAILY_BUDGET=10` / `ATELIER_THREAD_BUDGET=2` 在**模块导入期**读取，README 完全没写这两个变量——用户会在毫不知情的情况下撞上一个隐形上限，然后看到 500。

**D. 空 brief 泄露 prompt 脚手架。** 用户第一次点 Weave 时输入框常常是空的。实测 `prompt=""`：
```
message: 'Helix fast · Mode=fast. Preferred provider=demo model=demo-conductor.\nBrief:\n\nRoute: demo / demo-conductor...'
```
`DemoSpoke.chat` 的 brief 抽取在空输入下退回整段 user content，把内部 prompt 模板直接印到用户脸上。也没有"请先写点什么"的前端校验——空 brief 照样出图、照样记账。

### 2.6 绑定 / HTTPS / 本地服务安全（与切片 02 交叉，但直接影响交付）

默认 `127.0.0.1:8765`，这是**对的**，应当保留。真问题在于这个 loopback 服务假设了"loopback 就是可信的"：

- **未授权任意文件读取（已复现）。** `server.py:153-156` 的兜底 `candidate = WEB / path.lstrip("/")` 没有做路径归一化/前缀校验：
  ```
  GET /../server.py                  -> 200  (源码)
  GET /../helix/keyring.py           -> 200  (源码)
  GET /../../../../../../etc/passwd  -> 200  root:x:0:0:root:/root:/bin/bash …
  GET /../../../home5/keyring.json   -> 200  {"providers":{"openai":{"key":"sk-live-SECRET-TESTVALUE"…
  ```
  最后一条是关键：**只要相对层数对得上，`~/.atelier/keyring.json` 的明文内容就能被任何能连上这个端口的东西取走**。`/api/keys` 那边小心地做了脱敏（`public_status()` 只给 `sk-…-key` 提示），静态兜底路径把它整个绕过了。
- **无 Origin / 无 token / 无 CSRF 防护。** `_read_json` 不看 Content-Type，所以浏览器的"简单请求"（`text/plain` 表单 POST，无预检）可以直接打进来。实测跨站形态：
  ```
  POST /api/projects  -H 'Content-Type: text/plain' -H 'Origin: https://evil.example'
  -> 201 {"id":"…","name":"csrf-made-this"}
  ```
  响应体因为没有 `Access-Control-Allow-Origin`，跨站脚本读不到——所以这是**盲写**：任意网站可以在用户跑着 Atelier 时创建项目/线程、覆写 `/api/keys`（改 provider 的 `base_url`）、以及只要猜到/诱导出 thread id 就能触发 `run` 花用户的钱。配合 DNS rebinding，读也一起沦陷（能读 `/api/keys` 的 hint、能读整个画布、能走上面那条任意文件读取）。
- **`ATELIER_HOST` 是个没有护栏的悬崖。** `ATELIER_HOST=0.0.0.0` 无警告、无鉴权、无文档。而 Docker 场景**必须**设它。于是"想在容器里跑"这个完全合理的动作，等于把上面那条任意文件读取暴露到局域网。
- **HTTPS：v1 正确的答案是"不做"**，但必须**写下来为什么**——loopback 上 TLS 只会带来自签证书警告、浏览器信任弹窗、证书过期支持成本，安全收益接近零。需要远程访问的人给 SSH 隧道配方（`ssh -L 8765:127.0.0.1:8765 host`），不要给 `--host 0.0.0.0`。

### 2.7 数据落点 / 崩溃恢复

- **状态劈成两半**：key 在 `~/.atelier/keyring.json`，作品在 `<仓库>/atelier/.runtime/{helix.sqlite,artifacts/}`。没有一处遵循 XDG（`XDG_DATA_HOME` / `%LOCALAPPDATA%` / `~/Library/Application Support`）。
- **作品住在 git 工作区里，会被例行 git 操作删掉。** `.runtime/` 在 `.gitignore` 里，所以 `git clean -xdf`（每一份 Python 排障指南都会让你跑的命令）会**删掉用户所有项目、画布和图**。重新 clone 也一样归零。
- **两个 clone = 两个数据库。** 用户把仓库放到别处再跑一次，会发现"我的项目不见了"，实际是另一个 sqlite。
- **artifacts 在 DB 里存绝对路径 → 移动目录即整块画布损坏（已复现）。**
  ```
  重命名 clone -> clone-moved，在新路径起服务：
  GET /api/artifacts/64540a09…  -> HTTP 404
  DB 里存的是: /tmp/.../clone/atelier/.runtime/artifacts/64540a09….svg   （旧路径）
  文件其实就在: /tmp/.../clone-moved/atelier/.runtime/artifacts/64540a09….svg
  ```
  即：改个文件夹名、从 `~/Downloads` 挪到 `~/Projects`、Dropbox/OneDrive 同步到另一台机、Windows 盘符变化、WSL↔Windows 路径切换——画布全变空白图，而且看不出为什么。应存 `artifacts/<id>.<ext>` 相对路径，出盘时再拼。
- **sqlite 没有 WAL、没有 busy_timeout。** `ThreadingHTTPServer` + 单个 `check_same_thread=False` 连接共享给所有线程，并发 weave 撞上 `database is locked` 的概率非真零；`executescript(SCHEMA)` 只有 `CREATE TABLE IF NOT EXISTS`，**没有 schema 版本、没有迁移**——下一版加一列，老用户的库要么崩要么静默不一致。
- **无优雅关闭**：只 catch `KeyboardInterrupt`（`SIGINT`）。`SIGTERM`（关终端、系统重启、`kill`）时直接死，无 `server_close()`、无 `memory.close()`。
- **无备份 / 无导出 / 无"整删"说明**：README 没有一节告诉用户数据在哪、怎么备份、怎么把 key 和作品彻底抹掉。对本地工具，这一节和安装那一节同等重要。

### 2.8 日志

`Handler.log_message` 把每条访问写 stderr（格式还不错），除此之外**没有日志**：没有文件、没有轮转、没有 `--verbose/--quiet`、没有 request id、没有把 spoke 失败原因记下来（那句人话错误被 catch 掉后连日志都没进）。用户来报"图不对"，没有任何东西可以让他贴给你。Windows 上双击启动更是连 stderr 都看不见。

最小可用组合：`~/.atelier/logs/atelier.log`（`RotatingFileHandler`，5MB×3）+ 启动时打印日志路径 + **所有 spoke 失败无论是否降级都记一条**（记 provider/model/HTTP 状态/耗时，**绝不记 key**）。

### 2.9 桌面 / 托盘

完全没有。对本地工具，"是不是一个应用"很大程度由此判定：图标、双击启动、菜单栏/托盘图标显示"正在跑/端口/停止"、退出即真退出。

**v1 的正确答案不是 Electron**（+150MB、要签名、要公证、要自动更新，全都是本地工具最不该背的成本）。正确答案是三个小文件 + 一行代码：
- `webbrowser.open()`：启动即开浏览器（一行，收益最大）。
- macOS `Atelier.command`、Windows `atelier.bat`、Linux `atelier.desktop`：双击就跑，且**保持窗口不闪退**（Windows 上 `cmd /k` 或结尾 `pause`）。
- 可选 P2：`pywebview`（stdlib 之外的第一个依赖，要慎重）或 Chrome `--app=` 模式给个"像应用"的窗口。
- 托盘（`pystray`）是 P2，不挡 v1。

### 2.10 GitHub Pages 与"交付形态"

- `theqld.com` 由 Pages 提供（`CNAME` = `theqld.com`，`404.md` 带 Jekyll front matter，无 `_config.yml`、无 `.nojekyll`）。**Pages 是纯静态，永远跑不了 `server.py`。**
- `atelier.html` 面向的正是"从网上看到 Atelier 的陌生人"，但它只给了 `python3 -m atelier` 和 `# open http://127.0.0.1:8765`。**缺 clone 命令、缺 GitHub 链接、缺三平台说明、缺 Python 版本要求、缺一键复制按钮。** 一个非开发者在这页上无路可走。
- 页内链接指向 `atelier/ARCHITECTURE.md` 与 `atelier/integrations/TOP100.md`。这些 `.md` 没有 front matter，Jekyll 会原样拷出去 → 浏览器里是**一堆原始 markdown 文本**，不是渲染页面。
- 没有 `_config.yml` 的 `exclude`，所以整个 `atelier/` 子树（含所有 `.py`、`research/` 全部报告、`data/top100.json`）都会作为静态文件发布到 `theqld.com/atelier/…`。代码开源不算泄露，但这意味着**律所目录站和设计工作室共用一个发布面**——任何一边的改动都会重发另一边。
- 本地 UI 自身：`web/index.html` 是 `<html lang="zh-CN">`，而 README / 站点是英文；无 favicon（浏览器每次请求 `/favicon.ico` → 落到 API 兜底返回 `{"error":"not found"}`，并在日志里刷 404）。

正确的交付形态（按侵入性递增）：
1. **仓库内先自洽**：`pyproject.toml` + `atelier` 命令 + 一页 README 向导 + `atelier.html` 改成"三平台复制块 + 仓库链接 + 版本号"。
2. **GitHub Release**：打 `v0.1.0` tag，附 zip + `pipx install git+…@v0.1.0` 指令。零基础设施。
3. **拆仓**（P2，切片 10 交叉）：`NicGodfrey/atelier` 独立仓，theQLD 只留一张宣传页外链过去。59M 的法律站不该是设计工具的下载包。

---

## 3. 缺口清单（严重度 / 证据 / 最小修法）

| 严重度 | 缺口 | 证据 | 最小修法 |
|---|---|---|---|
| **Blocker** | 失败静默降级 demo，谎报 `Route: openai/...`，HTTP 200 | `conductor.py:158-164`；实测无 key 出 demo 图报成功 | 降级必须显式：响应加 `degraded: {reason, provider, message}`，dock 用黄条显示 spoke 原文；或按开关默认**不降级**直接报错 |
| **Blocker** | 本地服务任意文件读取，可取走明文 keyring | `server.py:153-156`；实测 `/etc/passwd` 200、`keyring.json` 200 | 归一化 `resolve()` 后校验 `WEB` 前缀 + 白名单静态文件；拒绝含 `..` 的路径 |
| **Blocker** | 无 Origin/token 校验，跨站盲写可花用户的钱 | 实测跨站 `text/plain` POST → 201 | 启动生成一次性 token 放进 URL/cookie；所有写操作校验 `Origin`/`Sec-Fetch-Site`；`_read_json` 强制 JSON Content-Type |
| **Blocker** | 无 `pyproject.toml`，pip/pipx/uv 全不可用；必须在仓库根 cd | `pip install ./clone` 报错；`cd /tmp && python3 -m atelier` → No module named | `pyproject.toml` + `[project.scripts] atelier = "atelier.cli:main"`（零依赖，纯 stdlib，好写） |
| **Blocker** | 无 CLI：`--help/--version` 被忽略并起服务；端口三种错法全 traceback | 实测 `--help` 直接监听；`Errno 98/13`、`ValueError` | `argparse`：`--host/--port/--open/--no-open/--data-dir/--version/doctor`；端口占用自动 +1 重试并提示；所有启动错误一行人话 |
| **Blocker** | artifacts 存绝对路径，移动目录后画布整块 404 | 实测重命名 clone → artifact 404，文件仍在 | DB 存相对路径 `artifacts/<id>.<ext>`，读时与 `data_dir` 拼接；一次性迁移脚本 |
| **Major** | 作品存在 git 工作区，`git clean -xdf` / 重新 clone 即全丢；key 与作品分处两地 | `.gitignore` 含 `.runtime/`；`server.runtime_dir()` 默认 `ROOT/.runtime` | 默认落 `~/.atelier/`（或 XDG / `%LOCALAPPDATA%`），`--data-dir` 可覆盖；检测到旧 `.runtime` 就提示搬迁 |
| **Major** | `URLError` 未捕获 → 断网/代理场景 500 + 原始 urllib 文本 | 实测 `UNHANDLED urllib.error.URLError` | 三个 spoke 的 `_post` 统一 catch `URLError`/`socket.timeout`/`ssl.SSLError` → `SpokeError("无法连上 api.openai.com：检查网络或代理")` |
| **Major** | 无密钥向导、无 key 验证、无删除、状态"绿"不代表可用 | UI 首屏铺开全部面板；`POST /api/keys` 只写盘；无 `do_DELETE` | 首次运行走 3 步向导（选 provider → 贴 key → **实调一次最便宜的 models 列表验证** → 显示估费）；加 `POST /api/keys/test`、`DELETE /api/keys/{p}` |
| **Major** | 无 Windows/macOS 说明；Windows 上 `python3` 不存在、`chmod 0600` 无效但 README 承诺 0600 | 文档零平台内容；`keyring._save` 的 `except OSError: pass` | README 三平台块（`py -3 -m atelier` / `python3` / venv）；Windows 上改用 ACL 或至少**明确告知"此平台文件权限不受保护"** |
| **Major** | 无日志文件、无 verbose、失败原因不落盘 | 仅 `log_message` → stderr | `~/.atelier/logs/atelier.log` 轮转；无论降级与否都记 spoke 失败；启动打印日志路径；绝不记 key |
| **Major** | 预算闸事后校验且抛 500；两个预算变量无文档 | `usage.record` 先调后校验；`BudgetExceeded` 非 SpokeError | 点 Weave 前用 `estimate_usd` 预检并在 UI 显示"本次约 $0.04"；超限返回 402 + 人话，不是 500 |
| **Major** | 无版本可指认：`__version__` 无人读、health 无版本、无 CHANGELOG、无 tag | `__init__.py:3`；`/api/health` 返回 `{ok,name,architecture}` | health 加 `version`；UI 角落显示；`CHANGELOG.md`（Keep a Changelog）；打 `v0.1.0` |
| **Major** | Pages 页对陌生人不可用；`.md` 链接给原始文本；整个 atelier 子树被发布 | `atelier.html:29-33`；无 `_config.yml`/`.nojekyll` | atelier.html 加"三平台复制块 + GitHub 链接 + 版本 + 明确写'这是本地工具，不在本页运行'"；`_config.yml` 里 `exclude: [atelier/]` 或把文档链接换成 GitHub blob URL |
| **Major** | 无 doctor：用户无法自助定位"为什么不出图" | 无此命令 | `atelier doctor`：Python 版本 / 端口可用 / data_dir 可写 / key 状态 / **到官方 host 的连通性与延迟** / 磁盘余量 / 数据库完整性 |
| **Minor** | `import atelier.server` 就建目录建库插示例数据 | `server.py:54` 模块级 `APP = App()` | 改成 `main()` 里惰性构造；便于测试与 doctor |
| **Minor** | `ATELIER_HOST=0.0.0.0` 无鉴权无警告，Docker 场景必踩 | `server.py:226` | 非回环绑定必须显式 `--allow-remote` + 强制 token + 启动大字警告 |
| **Minor** | sqlite 无 WAL/busy_timeout、无 schema 版本与迁移；无 SIGTERM 优雅关闭 | `store.py:86-89`；`main()` 只 catch KeyboardInterrupt | `PRAGMA journal_mode=WAL; busy_timeout=5000`；`user_version` + 迁移表；`signal` 处理 |
| **Minor** | README 未记录 `ATELIER_HOST/PORT/RUNTIME/HOME/DAILY_BUDGET/THREAD_BUDGET` | 实测代码里 6 个，README 里 0 个 | 一张环境变量全表（名/默认/作用/是否影响花钱） |
| **Minor** | `OLLAMA_HOST` 被当 secret，不改变请求地址（文档与行为不符） | `keyring.ENV_MAP` vs `get_base_url()` | `get_base_url("ollama")` 读 `OLLAMA_HOST`；README 改成 `OLLAMA_BASE_URL` 语义 |
| **Minor** | `anthropic` 在 `/api/keys` 露头但无 spoke → 选它=demo | `keyring.ENV_MAP` vs `build_spoke()` | 要么接上 spoke（研究树 `03-keyring-spokes/spokes_anthropic.py` 已有且有测试），要么从 `ENV_MAP` 摘掉 |
| **Minor** | `openai_compat` 静默绕过官方 host 锁，README 未提 | `openai_spoke.py:32-33` | UI 该项加红色警示"你的 key 会发往你填的地址"；README 单独一节；`doctor` 里报告当前是否启用 |
| **Minor** | 空 brief 泄露 prompt 脚手架、照样出图记账 | 实测 `prompt=""` 的 message | 前端禁用空 Weave；`DemoSpoke` 修 brief 抽取 |
| **Minor** | keyring 落盘有 0644 窗口；`~/.atelier` 目录 0755 | `keyring._save`、`__init__` 的 mkdir | 先 `os.open(…, 0o600)` 再写（或写临时文件 chmod 后 rename）；目录 `mkdir(mode=0o700)` |
| **Minor** | 无 LICENSE（整仓）、无生成物权属说明 | `find -iname LICENSE*` 空 | 切片 10 主责；交付上必须在 v1 之前落 |
| **Minor** | 无 CI | 无 `.github/` | 一条 workflow 跑 `python -m unittest atelier.tests.test_helix`（现 7 测全绿）+ 3.9/3.11/3.13 矩阵 + Windows runner |
| **Minor** | 本地 UI `lang="zh-CN"` 与英文文案不一致；无 favicon（每次 404 刷日志） | `web/index.html:2` | 定一个语言策略；加 favicon 与静态白名单 |

---

## 4. 排序：交付 / UX 收口顺序

排序原则：**先把"用户会误解成功"的东西修掉，再修"用户进不来"的东西，最后修"用户回不来"的东西。** 每项给验收判据。

### P0 —— 没有这些，任何推广都是负资产

1. **诚实的失败**（改 `conductor.py` + `server.py` 错误面 + 三个 spoke catch `URLError`）
   验收：无 key 点 openai → dock 显示「OpenAI key 未配置：到 Settings 粘贴 platform.openai.com 的 key。本次未花费。」画布**不**出现假 SVG；断网 → 「连不上 api.openai.com，检查网络/代理」；两条都不出现 traceback、不出现 200 假成功。
2. **本地服务不再交出密钥**（静态路径归一化 + 写操作 Origin/token 校验 + `_read_json` 强制 Content-Type）
   验收：`GET /../../../.atelier/keyring.json` → 404；跨站 `text/plain` POST → 403；一条回归测试钉住这两条。
3. **`pyproject.toml` + `atelier` 命令**（零依赖，`requires-python` 待 CI 定）
   验收：`pipx install git+https://github.com/NicGodfrey/theQLD` 后，在**任意目录** `atelier` 起服务；`atelier --version` 打 `0.1.0`。
4. **人话启动器**（`argparse` + 端口自适应 + `webbrowser.open`）
   验收：`atelier --help` 只打帮助不监听；8765 被占 → 「8765 被占用，改用 8766」并继续；`ATELIER_PORT=abc`、`--port 80` 各给一行人话；启动自动开浏览器（`--no-open` 可关）。
5. **数据落点统一 + 相对路径 artifacts + 迁移提示**
   验收：默认写 `~/.atelier/`（可 `--data-dir` 覆盖）；把整个数据目录 `mv` 到别处再起服务，画布图片全部照常显示；仓库里跑 `git clean -xdf` 之后用户数据仍在。
6. **首次运行密钥向导 + key 验证**（`POST /api/keys/test`）
   验收：全新机器上，非开发者在 5 分钟内完成 贴 key → 看到「已验证 ✓ 本次约 $0.04」→ 出一张真图 → 下载到本地；贴一个坏 key 立刻看到「这个 key 无效（401）」而不是绿灯。

### P1 —— 决定"他会不会第二天再打开一次"

7. **README 重写为交付文档**：五步向导（clone/install → 起服务 → 贴 key → 出第一张图 → 数据在哪）；三平台命令块；环境变量全表；**数据/备份/彻底卸载**一节；"ChatGPT Plus ≠ API"保留并加粗；`openai_compat` 风险单节。
   验收：一个没读过代码的人只照 README 能走通全程；README 里出现的每个变量都在代码里存在，代码里的每个变量都在 README 里出现。
8. **`atelier doctor`**。验收：故意破坏（占端口 / 坏 key / data_dir 只读 / 断网）四种情况，doctor 各自明确指出问题与修法。
9. **日志**：`~/.atelier/logs/atelier.log` 轮转 + spoke 失败必记 + `--verbose/--quiet` + 启动打印路径。
   验收：复现一次失败后，用户能从日志里贴出一段足以定位的内容，且其中**不含 key**。
10. **点击前估费 + 超限 402**。验收：Weave 按钮旁常驻「本次约 $X」；撞预算给 402 + 人话 + 「调高上限」的具体做法。
11. **版本与变更**：health/UI/CLI 三处版本一致 + `CHANGELOG.md` + `v0.1.0` tag + GitHub Release（附 zip）。
    验收：用户能回答"我在用哪个版本"，并能读到这版改了什么。
12. **Pages 页与交付形态**：`atelier.html` 换成三平台复制块 + 仓库/Release 链接 + 版本 + 「本地工具，不在本页运行」；`.md` 链接改指 GitHub；`_config.yml` 决定 atelier 子树是否发布。
    验收：从 theqld.com 出发的陌生人不需要问任何人就能装上。
13. **崩溃与恢复**：WAL + busy_timeout + schema `user_version` + SIGTERM 优雅关闭 + 启动时数据库完整性自检（坏了就备份并重建，不静默）。
14. **CI**：unittest + Python 矩阵 + Windows runner（顺手确定 `requires-python`）。

### P2 —— 抛光，不挡 v1

15. **双击启动**：`Atelier.command` / `atelier.bat`（不闪退）/ `atelier.desktop` + 图标 + favicon。
16. **托盘/菜单栏**（`pystray`）、`--app` 窗口模式或 `pywebview`。明确记录"**不做 Electron**"及理由。
17. **HTTPS：明确不做**，改为文档化 SSH 隧道；`--host` 非回环时强制 `--allow-remote` + token + 警告。
18. **`atelier --check-update`**（读 GitHub Releases，纯提示，不自动装）；单实例锁；`atelier stop`。
19. Windows keyring ACL 加固（DPAPI 或 OS keychain）；macOS Keychain / Linux Secret Service 可选后端。

---

## 5. 明确**不做**（v1 的正确省略）

写下来，免得被当成缺口反复提：
- **不做 Electron / Tauri 桌面壳**：+150MB、代码签名、公证、自动更新，全部是本地零依赖工具最不该背的成本。浏览器就是我们的 UI 容器。
- **不做 HTTPS / 证书**：loopback 上 TLS 的收益≈0，成本是自签警告与过期支持工单。
- **不做登录 / 多用户 / 云同步 / 遥测**：这是产品定义的一部分，不是待办。
- **不做安装包签名与商店上架**（Homebrew tap / winget 是 P2 之后的事）。
- **不做自动更新**：最多做"有新版"提示。

---

## 6. 交叉切片移交

- **切片 02（安全/额度）**：任意文件读取与无 Origin 校验两条已有可复现 PoC（见 §2.6），请以你那边的威胁模型为准收口；`openai_compat` 的 host-lock 绕过、keyring 落盘时序、Windows chmod 失效也归你。
- **切片 03（API 错位）**：`degraded` 字段、`402` 预算、`DELETE /api/keys`、`POST /api/keys/test`、artifact 相对路径、`/api/health` 带 version——这些是我这边要求的契约变更，请并进你的 API 定稿。
- **切片 06（前端 UX）**：首次运行向导、空 brief 校验、黄条降级提示、点击前估费、版本角标。
- **切片 07（Memory）**：绝对路径、WAL、schema 版本与迁移、数据目录搬迁。
- **切片 08（测试/CI）**：`requires-python` 需要你的矩阵结论；请把"traversal 拒绝"、"跨站 POST 拒绝"、"无 key 时 run 不返回假成功"三条做成回归测试。
- **切片 10（许可/集成）**：LICENSE 缺失、拆仓（`NicGodfrey/atelier`）、Pages 发布面。

---

## 附录 A · 复现命令

```bash
# 全部在 /tmp，不动 /workspace
mkdir -p /tmp/atelier-opus/09-ship-gaps && cd /tmp/atelier-opus/09-ship-gaps
git clone -q https://github.com/NicGodfrey/theQLD clone   # 实测用的是 /workspace 本地 clone
export ATELIER_HOME=$PWD/home ATELIER_PORT=8793

cd /tmp && python3 -m atelier                    # -> No module named atelier
cd clone/atelier && python3 -m atelier           # -> No module named atelier
cd clone && python3 -m atelier                   # -> 唯一可行
python3 -m pip install ./clone                   # -> Neither 'setup.py' nor 'pyproject.toml' found
ATELIER_PORT=abc python3 -m atelier              # -> ValueError traceback
ATELIER_PORT=80  python3 -m atelier              # -> PermissionError traceback
python3 -m atelier --help                        # -> 忽略参数，直接监听

# 静默降级（无 key，provider=openai）
curl -s -XPOST localhost:8793/api/threads/$TID/run -H 'Content-Type: application/json' \
  -d '{"prompt":"clinic poster","mode":"thinking","provider":"openai"}'
# -> 200, "Route: openai / gpt-4o-mini", artifact provider=demo

# 任意文件读取（需绕过 curl 的路径归一化，用裸 socket）
python3 - <<'PY'
import socket
s=socket.create_connection(("127.0.0.1",8793),3)
s.sendall(b"GET /../../../../../../etc/passwd HTTP/1.1\r\nHost: x\r\nConnection: close\r\n\r\n")
print(s.recv(300).decode(errors="replace"))
PY

# 跨站盲写
curl -s -XPOST -H 'Content-Type: text/plain' -H 'Origin: https://evil.example' \
  -d '{"name":"csrf-made-this"}' localhost:8793/api/projects   # -> 201

# 绝对路径导致画布损坏
mv clone clone-moved && cd clone-moved && python3 -m atelier &
curl -o /dev/null -w '%{http_code}\n' localhost:8794/api/artifacts/$AID   # -> 404，文件其实在
```

## 附录 B · 现状事实表（供其它切片引用）

| 事实 | 值 |
|---|---|
| 第三方依赖 | **0**（纯 stdlib，21 个标准模块） |
| 语法最低可解析版本 | 3.9（`ast.feature_version` 检查；运行时未验证，未声明） |
| tracked 文件 | 201（其中 `atelier/` 113，theQLD 站点 88） |
| clone 体积 | 59M（`atelier/` 自身 1.7M） |
| 冷启动 | ~1s；demo weave ~19ms；bogus-key 降级 ~0.38s |
| 测试 | 7 个 unittest，全绿（研究树里另有 58 个未接线） |
| shipping code 环境变量 | `ATELIER_HOST` `ATELIER_PORT` `ATELIER_RUNTIME` `ATELIER_HOME` `ATELIER_DAILY_BUDGET` `ATELIER_THREAD_BUDGET` + provider keys |
| README 记录的 ATELIER_* 变量 | 0 / 6 |
| 版本 / tag / CHANGELOG / LICENSE / CI | `0.1.0`（无人读取） / 无 / 无 / 无 / 无 |
