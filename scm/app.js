const STORAGE_KEY = "theqld.scm.v1";
const STATUS_LABELS = {
  active: "启用",
  inactive: "停用",
  draft: "草稿",
  sent: "已发出",
  partial: "部分到货",
  received: "已收货",
  cancelled: "已取消",
  allocated: "已预留",
  shipped: "已发运",
  delivered: "已送达",
  planned: "计划中",
  in_transit: "在途",
  receive: "入库",
  ship: "出库",
  adjust: "调整",
  reserve: "预留",
  release: "释放",
  inbound: "入库物流",
  outbound: "出库物流",
  purchase: "采购",
  sales: "销售",
};

const TITLES = {
  dashboard: ["总览", "库存健康、未结单据与低库存预警。"],
  suppliers: ["供应商", "维护供方主数据、交期与联系方式。"],
  products: ["物料", "SKU、成本、补货点与默认供应商。"],
  inventory: ["库存", "仓别现存量、预留量与盘点调整。"],
  "purchase-orders": ["采购单", "向供应商下单并跟踪收货状态。"],
  "sales-orders": ["销售单", "客户出库需求与预留。"],
  shipments: ["物流", "入出库运单、承运商与轨迹号。"],
  mount: ["挂载本地系统", "把本地供应链管理系统的 JSON 导出文件挂到本站。"],
};

function emptyState() {
  return {
    version: 1,
    source: "",
    exportedAt: new Date().toISOString(),
    suppliers: [],
    products: [],
    warehouses: [],
    stock: [],
    purchaseOrders: [],
    salesOrders: [],
    shipments: [],
    movements: [],
  };
}

function uid(prefix) {
  return `${prefix}-${Math.random().toString(16).slice(2, 10)}`;
}

const db = {
  api: false,
  state: emptyState(),
};

async function detectApi() {
  try {
    const res = await fetch("/api/health", { cache: "no-store" });
    db.api = res.ok;
  } catch {
    db.api = false;
  }
}

async function loadState() {
  if (db.api) {
    const res = await fetch("/api/state", { cache: "no-store" });
    db.state = await res.json();
    return;
  }
  const raw = localStorage.getItem(STORAGE_KEY);
  if (raw) {
    db.state = JSON.parse(raw);
    return;
  }
  const seed = await fetch("./sample-local-export.json").then((r) => r.json()).catch(() => null);
  db.state = seed || emptyState();
  persistLocal();
}

function persistLocal() {
  db.state.exportedAt = new Date().toISOString();
  localStorage.setItem(STORAGE_KEY, JSON.stringify(db.state));
}

async function saveState(next, mode = "replace") {
  if (db.api) {
    const res = await fetch("/api/mount", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode, source: next.source || "browser", data: next }),
    });
    const payload = await res.json();
    if (!res.ok) throw new Error(payload.error || "挂载失败");
    db.state = payload.state || next;
    return;
  }
  db.state = next;
  persistLocal();
}

function findName(list, id, fallback = "—") {
  return (list || []).find((row) => row.id === id)?.name || fallback;
}

function available(row) {
  return Number(row.qty || 0) - Number(row.reserved || 0);
}

function money(n) {
  return Number(n || 0).toLocaleString("zh-CN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function badge(status) {
  const warn = ["sent", "partial", "allocated", "planned", "in_transit", "inactive"].includes(status);
  const good = ["active", "received", "delivered"].includes(status);
  const bad = ["cancelled"].includes(status);
  const cls = bad ? "bad" : warn ? "warn" : good ? "good" : "";
  return `<span class="badge ${cls}">${STATUS_LABELS[status] || status || "—"}</span>`;
}

function routeName() {
  return (location.hash.replace(/^#\/?/, "") || "dashboard").split("?")[0];
}

function setActiveNav() {
  document.querySelectorAll(".rail nav a").forEach((a) => {
    a.classList.toggle("active", a.dataset.route === routeName());
  });
}

function download(filename, text) {
  const blob = new Blob([text], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

function dashboardView() {
  const s = db.state;
  const products = Object.fromEntries(s.products.map((p) => [p.id, p]));
  let stockValue = 0;
  const low = [];
  s.stock.forEach((row) => {
    const product = products[row.productId];
    if (!product) return;
    stockValue += Number(row.qty || 0) * Number(product.cost || 0);
    if (available(row) <= Number(product.reorderPoint || 0)) {
      low.push({ ...row, product });
    }
  });
  const openPo = s.purchaseOrders.filter((x) => ["draft", "sent", "partial"].includes(x.status)).length;
  const openSo = s.salesOrders.filter((x) => ["draft", "allocated", "shipped"].includes(x.status)).length;
  const transit = s.shipments.filter((x) => ["planned", "in_transit"].includes(x.status)).length;
  return `
    <div class="kpis">
      ${kpi(s.suppliers.length, "供应商")}
      ${kpi(s.products.length, "物料")}
      ${kpi(money(stockValue), "库存金额")}
      ${kpi(openPo, "未结采购")}
      ${kpi(openSo, "未结销售")}
      ${kpi(transit, "在途运单")}
    </div>
    <div class="grid-2">
      <div class="card">
        <h3>低库存</h3>
        <div class="table-wrap">${table(
          ["SKU", "物料", "仓", "可用", "补货点"],
          low.map((row) => [
            row.product.sku,
            row.product.name,
            findName(s.warehouses, row.warehouseId, row.warehouseId),
            available(row),
            row.product.reorderPoint,
          ])
        )}</div>
      </div>
      <div class="card">
        <h3>挂载来源</h3>
        <p>当前数据源：<strong>${s.source || (db.api ? "Cloud Agent SQLite" : "浏览器 localStorage")}</strong></p>
        <p class="muted">导出时间 ${s.exportedAt || "—"}</p>
        <p class="muted" style="margin-top:12px">把本地系统导出的 JSON 放到「挂载本地」页，即可覆盖或合并到这里。</p>
      </div>
    </div>
  `;
}

function kpi(value, label) {
  return `<div class="card"><div class="kpi-value">${value}</div><div class="kpi-label">${label}</div></div>`;
}

function table(headers, rows, actions = "") {
  if (!rows.length) return `<p class="muted">暂无数据</p>`;
  return `<table><thead><tr>${headers.map((h) => `<th>${h}</th>`).join("")}${actions ? "<th></th>" : ""}</tr></thead>
    <tbody>${rows
      .map(
        (cols, i) =>
          `<tr>${cols.map((c) => `<td>${c}</td>`).join("")}${
            actions ? `<td>${actions[i] || ""}</td>` : ""
          }</tr>`
      )
      .join("")}</tbody></table>`;
}

function listView(kind) {
  const s = db.state;
  const searchId = `${kind}-q`;
  const addLabel = {
    suppliers: "新增供应商",
    products: "新增物料",
    inventory: "库存调整",
    "purchase-orders": "新建采购单",
    "sales-orders": "新建销售单",
    shipments: "新建运单",
  }[kind];
  return `
    <div class="card">
      <div class="toolbar">
        <input class="search" id="${searchId}" placeholder="搜索...">
        <button type="button" data-add="${kind}">${addLabel}</button>
      </div>
      <div class="table-wrap" id="${kind}-table">${renderList(kind, "")}</div>
    </div>
  `;
}

function renderList(kind, q) {
  const s = db.state;
  const needle = q.trim().toLowerCase();
  const match = (parts) => !needle || parts.join(" ").toLowerCase().includes(needle);
  if (kind === "suppliers") {
    const rows = s.suppliers.filter((r) => match([r.name, r.contact, r.email, r.phone]));
    return table(
      ["名称", "联系人", "邮箱", "交期(天)", "状态"],
      rows.map((r) => [r.name, r.contact || "—", r.email || "—", r.leadDays ?? "—", badge(r.status)]),
      rows.map((r) => rowActions("suppliers", r.id))
    );
  }
  if (kind === "products") {
    const rows = s.products.filter((r) => match([r.sku, r.name, r.category]));
    return table(
      ["SKU", "名称", "分类", "单位", "成本", "补货点", "供应商", "状态"],
      rows.map((r) => [
        r.sku,
        r.name,
        r.category || "—",
        r.unit || "pcs",
        money(r.cost),
        r.reorderPoint ?? 0,
        findName(s.suppliers, r.supplierId),
        badge(r.status),
      ]),
      rows.map((r) => rowActions("products", r.id))
    );
  }
  if (kind === "inventory") {
    const products = Object.fromEntries(s.products.map((p) => [p.id, p]));
    const rows = s.stock.filter((r) => {
      const p = products[r.productId] || {};
      return match([p.sku, p.name, r.warehouseId]);
    });
    return table(
      ["仓", "SKU", "物料", "现有", "预留", "可用"],
      rows.map((r) => {
        const p = products[r.productId] || {};
        const cls = available(r) <= Number(p.reorderPoint || 0) ? "badge warn" : "badge good";
        return [
          findName(s.warehouses, r.warehouseId, r.warehouseId),
          p.sku || r.productId,
          p.name || "—",
          r.qty,
          r.reserved,
          `<span class="${cls}">${available(r)}</span>`,
        ];
      })
    );
  }
  if (kind === "purchase-orders") {
    const rows = s.purchaseOrders.filter((r) => match([r.number, r.supplierId]));
    return table(
      ["单号", "供应商", "收货仓", "行数", "状态", "创建"],
      rows.map((r) => [
        r.number,
        findName(s.suppliers, r.supplierId),
        findName(s.warehouses, r.warehouseId),
        (r.lines || []).length,
        badge(r.status),
        (r.createdAt || "").slice(0, 10),
      ]),
      rows.map((r) => rowActions("purchaseOrders", r.id))
    );
  }
  if (kind === "sales-orders") {
    const rows = s.salesOrders.filter((r) => match([r.number, r.customer]));
    return table(
      ["单号", "客户", "出库仓", "行数", "状态", "创建"],
      rows.map((r) => [
        r.number,
        r.customer || "—",
        findName(s.warehouses, r.warehouseId),
        (r.lines || []).length,
        badge(r.status),
        (r.createdAt || "").slice(0, 10),
      ]),
      rows.map((r) => rowActions("salesOrders", r.id))
    );
  }
  if (kind === "shipments") {
    const rows = s.shipments.filter((r) => match([r.number, r.carrier, r.tracking]));
    return table(
      ["运单号", "类型", "承运商", "轨迹号", "状态"],
      rows.map((r) => [
        r.number,
        STATUS_LABELS[r.type] || r.type,
        r.carrier || "—",
        r.tracking || "—",
        badge(r.status),
      ]),
      rows.map((r) => rowActions("shipments", r.id))
    );
  }
  return "";
}

function rowActions(kind, id) {
  return `<button type="button" class="ghost" data-edit="${kind}" data-id="${id}">编辑</button>
          <button type="button" class="ghost danger" data-del="${kind}" data-id="${id}">删</button>`;
}

function mountView() {
  const sample = JSON.stringify(
    {
      version: 1,
      source: "/path/to/your-local-scm",
      suppliers: [{ id: "sup-1", name: "本地供应商" }],
      products: [{ id: "prd-1", sku: "SKU-1", name: "本地物料", supplierId: "sup-1", cost: 1 }],
      warehouses: [{ id: "wh-1", code: "WH1", name: "本地仓" }],
      stock: [{ warehouseId: "wh-1", productId: "prd-1", qty: 10, reserved: 0 }],
    },
    null,
    2
  );
  return `
    <div class="stack">
      <div class="notice">
        当前 Cloud Agent 工作区是 <code>NicGodfrey/theQLD</code>，看不到你笔记本上的目录。
        把本地供应链系统按 <code>scm/schema.json</code> 导出 JSON，在这里挂载；或把项目推到 GitHub 后作为多仓环境加入。
        也可用 <code>scm/sample-local-export.json</code> 先试一遍。
      </div>
      <div class="grid-2">
        <div class="card mount-box">
          <h3>导入并挂载</h3>
          <label>模式
            <select id="mount-mode">
              <option value="replace">覆盖（替换现有数据）</option>
              <option value="merge">合并（按 id 覆盖同名记录）</option>
            </select>
          </label>
          <p class="muted">选择本地导出文件，或把 JSON 粘贴到下面。</p>
          <input id="mount-file" type="file" accept="application/json,.json">
          <textarea id="mount-json" placeholder='{"version":1,...}'></textarea>
          <div class="modal-actions">
            <button type="button" class="ghost" id="load-sample">填入示例</button>
            <button type="button" id="mount-btn">挂载到本系统</button>
          </div>
          <p id="mount-msg" class="muted"></p>
        </div>
        <div class="card">
          <h3>导出约定</h3>
          <p class="muted">本地系统只需吐出这个结构。字段可缺省，服务端会补全 id 与状态。</p>
          <pre>${escapeHtml(sample)}</pre>
          <p class="muted">API：<code>POST /api/mount</code>，body 为 <code>{"mode":"replace"|"merge","data":{...}}</code></p>
        </div>
      </div>
    </div>
  `;
}

function escapeHtml(text) {
  return text.replace(/[&<>]/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[ch]));
}

function options(list, selected, label = (x) => x.name, value = (x) => x.id) {
  return list
    .map((item) => `<option value="${value(item)}" ${value(item) === selected ? "selected" : ""}>${label(item)}</option>`)
    .join("");
}

function openModal(title, fields, onSubmit) {
  const modal = document.getElementById("modal");
  const form = document.getElementById("modal-form");
  form.innerHTML = `<h3>${title}</h3>${fields}
    <div class="modal-actions">
      <button type="button" class="ghost" data-close>取消</button>
      <button type="submit">保存</button>
    </div>`;
  modal.hidden = false;
  form.onsubmit = async (event) => {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(form).entries());
    await onSubmit(data);
    modal.hidden = true;
    await render();
  };
}

function field(name, label, value = "", type = "text") {
  return `<label>${label}<input name="${name}" type="${type}" value="${value ?? ""}"></label>`;
}

function selectField(name, label, html) {
  return `<label>${label}<select name="${name}">${html}</select></label>`;
}

function getItem(kind, id) {
  return (db.state[kind] || []).find((row) => row.id === id) || {};
}

async function upsertCollection(kind, item) {
  const next = structuredClone(db.state);
  const list = next[kind];
  const idx = list.findIndex((row) => row.id === item.id);
  if (idx >= 0) list[idx] = { ...list[idx], ...item };
  else list.push(item);
  next.source = next.source || (db.api ? "api" : "browser");
  await saveState(next, "replace");
}

async function removeCollection(kind, id) {
  const next = structuredClone(db.state);
  next[kind] = next[kind].filter((row) => row.id !== id);
  await saveState(next, "replace");
}

function addHandlers() {
  const kind = routeName();
  const search = document.getElementById(`${kind}-q`);
  if (search) {
    search.addEventListener("input", () => {
      document.getElementById(`${kind}-table`).innerHTML = renderList(kind, search.value);
    });
  }
  document.querySelectorAll("[data-add]").forEach((btn) => btn.addEventListener("click", () => startCreate(btn.dataset.add)));
  document.querySelectorAll("[data-edit]").forEach((btn) =>
    btn.addEventListener("click", () => startEdit(btn.dataset.edit, btn.dataset.id))
  );
  document.querySelectorAll("[data-del]").forEach((btn) =>
    btn.addEventListener("click", async () => {
      if (!confirm("删除这条记录？")) return;
      await removeCollection(btn.dataset.del, btn.dataset.id);
      await render();
    })
  );
  const mountBtn = document.getElementById("mount-btn");
  if (mountBtn) {
    document.getElementById("load-sample").onclick = async () => {
      const sample = await fetch("./sample-local-export.json").then((r) => r.json());
      document.getElementById("mount-json").value = JSON.stringify(sample, null, 2);
    };
    document.getElementById("mount-file").onchange = async (event) => {
      const file = event.target.files[0];
      if (!file) return;
      document.getElementById("mount-json").value = await file.text();
    };
    mountBtn.onclick = async () => {
      const msg = document.getElementById("mount-msg");
      try {
        const parsed = JSON.parse(document.getElementById("mount-json").value);
        const mode = document.getElementById("mount-mode").value;
        parsed.source = parsed.source || "local-json";
        await saveState(parsed, mode);
        msg.textContent = "挂载成功。";
        location.hash = "#/dashboard";
      } catch (err) {
        msg.textContent = err.message || String(err);
      }
    };
  }
}

function startCreate(kind) {
  if (kind === "suppliers") return editSupplier();
  if (kind === "products") return editProduct();
  if (kind === "inventory") return adjustStock();
  if (kind === "purchase-orders") return editPurchase();
  if (kind === "sales-orders") return editSales();
  if (kind === "shipments") return editShipment();
}

function startEdit(kind, id) {
  if (kind === "suppliers") return editSupplier(getItem("suppliers", id));
  if (kind === "products") return editProduct(getItem("products", id));
  if (kind === "purchaseOrders") return editPurchase(getItem("purchaseOrders", id));
  if (kind === "salesOrders") return editSales(getItem("salesOrders", id));
  if (kind === "shipments") return editShipment(getItem("shipments", id));
}

function editSupplier(item = {}) {
  openModal(
    item.id ? "编辑供应商" : "新增供应商",
    field("name", "名称", item.name || "") +
      field("contact", "联系人", item.contact || "") +
      field("email", "邮箱", item.email || "") +
      field("phone", "电话", item.phone || "") +
      field("address", "地址", item.address || "") +
      field("leadDays", "交期(天)", item.leadDays ?? 7, "number") +
      selectField("status", "状态", options([{ id: "active", name: "启用" }, { id: "inactive", name: "停用" }], item.status || "active")),
    (data) => upsertCollection("suppliers", { ...item, ...data, id: item.id || uid("sup"), leadDays: Number(data.leadDays || 0) })
  );
}

function editProduct(item = {}) {
  openModal(
    item.id ? "编辑物料" : "新增物料",
    field("sku", "SKU", item.sku || "") +
      field("name", "名称", item.name || "") +
      field("category", "分类", item.category || "") +
      field("unit", "单位", item.unit || "pcs") +
      field("cost", "成本", item.cost ?? 0, "number") +
      field("reorderPoint", "补货点", item.reorderPoint ?? 0, "number") +
      selectField("supplierId", "默认供应商", options(db.state.suppliers, item.supplierId)) +
      selectField("status", "状态", options([{ id: "active", name: "启用" }, { id: "inactive", name: "停用" }], item.status || "active")),
    (data) =>
      upsertCollection("products", {
        ...item,
        ...data,
        id: item.id || uid("prd"),
        cost: Number(data.cost || 0),
        reorderPoint: Number(data.reorderPoint || 0),
      })
  );
}

function adjustStock() {
  openModal(
    "库存调整",
    selectField("warehouseId", "仓库", options(db.state.warehouses)) +
      selectField("productId", "物料", options(db.state.products, "", (p) => `${p.sku} ${p.name}`)) +
      field("qty", "增减数量（可负）", 0, "number") +
      field("ref", "备注", ""),
    async (data) => {
      const qty = Number(data.qty || 0);
      if (db.api) {
        const res = await fetch("/api/stock/adjust", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ ...data, qty, type: "adjust" }),
        });
        const payload = await res.json();
        if (!res.ok) throw new Error(payload.error || "调整失败");
        await loadState();
        return;
      }
      const next = structuredClone(db.state);
      let row = next.stock.find((s) => s.warehouseId === data.warehouseId && s.productId === data.productId);
      if (!row) {
        row = { warehouseId: data.warehouseId, productId: data.productId, qty: 0, reserved: 0 };
        next.stock.push(row);
      }
      row.qty = Number(row.qty) + qty;
      next.movements.push({
        id: uid("mv"),
        at: new Date().toISOString(),
        type: "adjust",
        productId: data.productId,
        warehouseId: data.warehouseId,
        qty,
        ref: data.ref || "",
      });
      await saveState(next);
    }
  );
}

function editPurchase(item = {}) {
  const firstProduct = db.state.products[0] || {};
  const firstLine = (item.lines && item.lines[0]) || { productId: firstProduct.id || "", qty: 1, unitCost: firstProduct.cost || 0 };
  openModal(
    item.id ? "编辑采购单" : "新建采购单",
    field("number", "单号", item.number || `PO-${Date.now()}`) +
      selectField("supplierId", "供应商", options(db.state.suppliers, item.supplierId)) +
      selectField("warehouseId", "收货仓", options(db.state.warehouses, item.warehouseId)) +
      selectField("productId", "物料", options(db.state.products, firstLine.productId, (p) => `${p.sku} ${p.name}`)) +
      field("qty", "数量", firstLine.qty ?? 1, "number") +
      field("unitCost", "单价", firstLine.unitCost ?? 0, "number") +
      selectField(
        "status",
        "状态",
        options(
          ["draft", "sent", "partial", "received", "cancelled"].map((id) => ({ id, name: STATUS_LABELS[id] })),
          item.status || "draft"
        )
      ),
    (data) =>
      upsertCollection("purchaseOrders", {
        ...item,
        id: item.id || uid("po"),
        number: data.number,
        supplierId: data.supplierId,
        warehouseId: data.warehouseId,
        status: data.status,
        createdAt: item.createdAt || new Date().toISOString(),
        expectedAt: item.expectedAt || "",
        lines: [{ productId: data.productId, qty: Number(data.qty || 0), unitCost: Number(data.unitCost || 0) }],
      })
  );
}

function editSales(item = {}) {
  const firstProduct = db.state.products[0] || {};
  const firstLine = (item.lines && item.lines[0]) || { productId: firstProduct.id || "", qty: 1, unitPrice: 0 };
  openModal(
    item.id ? "编辑销售单" : "新建销售单",
    field("number", "单号", item.number || `SO-${Date.now()}`) +
      field("customer", "客户", item.customer || "") +
      selectField("warehouseId", "出库仓", options(db.state.warehouses, item.warehouseId)) +
      selectField("productId", "物料", options(db.state.products, firstLine.productId, (p) => `${p.sku} ${p.name}`)) +
      field("qty", "数量", firstLine.qty ?? 1, "number") +
      field("unitPrice", "单价", firstLine.unitPrice ?? 0, "number") +
      selectField(
        "status",
        "状态",
        options(
          ["draft", "allocated", "shipped", "delivered", "cancelled"].map((id) => ({ id, name: STATUS_LABELS[id] })),
          item.status || "draft"
        )
      ),
    (data) =>
      upsertCollection("salesOrders", {
        ...item,
        id: item.id || uid("so"),
        number: data.number,
        customer: data.customer,
        warehouseId: data.warehouseId,
        status: data.status,
        createdAt: item.createdAt || new Date().toISOString(),
        lines: [{ productId: data.productId, qty: Number(data.qty || 0), unitPrice: Number(data.unitPrice || 0) }],
      })
  );
}

function editShipment(item = {}) {
  openModal(
    item.id ? "编辑运单" : "新建运单",
    field("number", "运单号", item.number || `SH-${Date.now()}`) +
      selectField("type", "类型", options([{ id: "inbound", name: "入库物流" }, { id: "outbound", name: "出库物流" }], item.type || "outbound")) +
      field("carrier", "承运商", item.carrier || "") +
      field("tracking", "轨迹号", item.tracking || "") +
      selectField(
        "status",
        "状态",
        options(
          ["planned", "in_transit", "delivered", "cancelled"].map((id) => ({ id, name: STATUS_LABELS[id] })),
          item.status || "planned"
        )
      ),
    (data) => upsertCollection("shipments", { ...item, ...data, id: item.id || uid("sh") })
  );
}

async function render() {
  const route = routeName();
  const [title, sub] = TITLES[route] || TITLES.dashboard;
  document.getElementById("page-title").textContent = title;
  document.getElementById("page-sub").textContent = sub;
  document.getElementById("mode-badge").textContent = db.api ? "API + SQLite" : "浏览器存储";
  setActiveNav();
  const view = document.getElementById("view");
  if (route === "dashboard") view.innerHTML = dashboardView();
  else if (route === "mount") view.innerHTML = mountView();
  else view.innerHTML = listView(route);
  addHandlers();
}

document.getElementById("modal").addEventListener("click", (event) => {
  if (event.target.id === "modal" || event.target.dataset.close !== undefined) {
    document.getElementById("modal").hidden = true;
  }
});

document.getElementById("export-btn").onclick = () => {
  download(`scm-export-${new Date().toISOString().slice(0, 10)}.json`, JSON.stringify(db.state, null, 2));
};
document.getElementById("reload-btn").onclick = async () => {
  await loadState();
  await render();
};
window.addEventListener("hashchange", render);

(async function init() {
  await detectApi();
  await loadState();
  if (!location.hash) location.hash = "#/dashboard";
  else await render();
})();
