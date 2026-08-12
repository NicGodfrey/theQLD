# MERIDIAN Product Studio

10 款可商用浏览器成品，覆盖：

1. **Flow Create** — AI 创作工作流  
2. **Flow Market** — AI 营销工作流  
3. **Flow Content** — AI 内容工作流  
4. **Flow Ops** — AI 用户运营工作流  
5. **Lovara** — Lovart-class AI 设计代理  
6. **Proxy Gate** — AI API 反代网关  
7. **Proxy Router** — 多模型反代路由  
8. **Proxy Tunnel** — 本地模型反代隧道  
9. **Canvas Studio** — AI 创意画布  
10. **Agent Factory** — 工作流 × 反代编排工厂  

## 本地打开

静态即可运行，无需构建：

```bash
cd meridian
python3 -m http.server 5173
```

浏览器访问 `http://127.0.0.1:5173/`。

数据保存在 `localStorage`；网关/路由可导出 Nginx、Compose、Caddy、Traefik 配置。
