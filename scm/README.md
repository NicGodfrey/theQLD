# 供应链管理系统挂载点

把本地供应链系统挂到 `theQLD` 站点上的入口。GitHub Pages 打开 `scm/index.html` 即可用；Cloud Agent / 本机可再跑无依赖 sidecar。

## 为什么不能直接看到你的本地目录

当前 Cloud Agent 只克隆了 [NicGodfrey/theQLD](https://github.com/NicGodfrey/theQLD)。笔记本上的项目不会自动出现在 `/workspace`。

## 三种挂载方式

### 1. JSON 导出（立刻可用）

本地系统按 `schema.json` 导出，然后：

- 浏览器：打开 `/scm/#/mount`，选文件或粘贴 JSON，覆盖或合并。
- API：

```bash
python3 scm/server.py --port 8787
curl -X POST http://127.0.0.1:8787/api/mount \
  -H 'Content-Type: application/json' \
  -d '{"mode":"replace","source":"my-local-scm","data":'"$(cat /path/to/export.json)"'}'
```

`scm/sample-local-export.json` 是最小合法样例。

### 2. 把本地项目拷进本仓库

```bash
mkdir -p scm/local
rsync -a --exclude .git /path/to/your-scm/ scm/local/
```

站点仍走 `scm/` 这一层协议；`scm/local/` 留给原系统源码。

### 3. Cloud Agent 多仓库环境

把本地系统推到 GitHub，在 [Cloud Agents Environments](https://cursor.com/dashboard/cloud-agents) 里和 `theQLD` 一起勾选。`repositoryDependencies` 只会扩大 token，不会自动 checkout。

## 本机启动 sidecar

```bash
python3 scm/server.py --host 127.0.0.1 --port 8787
```

打开 http://127.0.0.1:8787/ 。数据落在 `scm/data/scm.sqlite`。

## 测试

```bash
python3 -m unittest scm.tests.test_server
```
