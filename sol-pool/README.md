# GPT5.6 sol 10 槽网关原型

本机第一阶段实现：固定 10 个逻辑槽位，对外名称均为 **GPT5.6 sol**。每个外部会话只能绑定其中一个槽；会话断开或租约超时后，槽位重置并清空运行时上下文。对话、推理过程和计费事件先落盘再返回。

当前使用确定性假模型，用来验证隔离、重置、幂等和计费，不调用真实上游。

## 启动

```bash
cd sol-pool
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m sol_pool
```

如果当前环境没有 `python3-venv`，也可以：

```bash
cd sol-pool
pip3 install -r requirements.txt
PYTHONPATH=. python3 -m sol_pool
```

- API：http://127.0.0.1:8787/v1/health
- 演示页：http://127.0.0.1:8787/demo/
- 默认 API key：`dev-key`

环境变量：

- `SOL_POOL_API_KEY`
- `SOL_POOL_DATA_DIR`（默认 `./data`）
- `SOL_POOL_LEASE_SECONDS`（默认 `30`，超时即重置）

## 调用约定

1. 用 API key 创建会话，得到 `access_token` 和 `worker_id`。
2. 之后该会话只能调用绑定的 worker。
3. 定期 `POST /v1/sessions/{id}/heartbeat`；停止心跳后槽位重置。
4. `DELETE /v1/sessions/{id}` 立即重置。创建、发消息、结束都必须带 `Idempotency-Key`。

```bash
KEY=dev-key
SID_KEY=$(python3 -c 'import uuid; print(uuid.uuid4())')

curl -sS -X POST http://127.0.0.1:8787/v1/sessions \
  -H "Authorization: Bearer $KEY" \
  -H "Idempotency-Key: $SID_KEY" \
  -H "Content-Type: application/json" \
  -d '{}'
```

创建会话的 JSON 字段是 `worker_id`（1–10，可省略表示自动分配）。

假模型测试命令：

- `WRITE:secret` 写入当前槽沙箱
- `READ_NOTE` 读取当前槽沙箱
- `READ_FILE:../...` 应被拒绝

## 测试

```bash
cd sol-pool
.venv/bin/pytest -q
```

## 范围

已覆盖：10 槽容量、1:1 绑定、沙箱隔离、断线/超时重置、幂等、JSONL 哈希链记录、按次计费事件。

未覆盖：公网入口、真实 GPT-5.6 sol 上游、WORM 对象锁、按供应商账单对账。
