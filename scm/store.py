"""SQLite-backed supply-chain store used by the mount API."""

from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DEFAULT_DB = ROOT / "data" / "scm.sqlite"
SCHEMA_VERSION = 1

COLLECTIONS = (
    "suppliers",
    "products",
    "warehouses",
    "stock",
    "purchaseOrders",
    "salesOrders",
    "shipments",
    "movements",
)

_STATUSES = {
    "suppliers": {"active", "inactive"},
    "products": {"active", "inactive"},
    "warehouses": {"active", "inactive"},
    "purchaseOrders": {"draft", "sent", "partial", "received", "cancelled"},
    "salesOrders": {"draft", "allocated", "shipped", "delivered", "cancelled"},
    "shipments": {"planned", "in_transit", "delivered", "cancelled"},
    "movements": {"receive", "ship", "adjust", "reserve", "release"},
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:10]}"


def empty_state() -> dict[str, Any]:
    state: dict[str, Any] = {"version": SCHEMA_VERSION, "source": "", "exportedAt": utc_now()}
    for name in COLLECTIONS:
        state[name] = []
    return state


def normalize_state(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("mount payload must be a JSON object")
    version = payload.get("version", SCHEMA_VERSION)
    if version != SCHEMA_VERSION:
        raise ValueError(f"unsupported dump version: {version}")
    state = empty_state()
    state["source"] = str(payload.get("source") or "")
    state["exportedAt"] = str(payload.get("exportedAt") or utc_now())
    for name in COLLECTIONS:
        items = payload.get(name, [])
        if items is None:
            items = []
        if not isinstance(items, list):
            raise ValueError(f"{name} must be an array")
        state[name] = [normalize_item(name, item) for item in items]
    return state


def normalize_item(kind: str, item: Any) -> dict[str, Any]:
    if not isinstance(item, dict):
        raise ValueError(f"{kind} entries must be objects")
    handlers = {
        "suppliers": _supplier,
        "products": _product,
        "warehouses": _warehouse,
        "stock": _stock,
        "purchaseOrders": _purchase_order,
        "salesOrders": _sales_order,
        "shipments": _shipment,
        "movements": _movement,
    }
    return handlers[kind](item)


def _text(item: dict[str, Any], key: str, default: str = "") -> str:
    value = item.get(key, default)
    if value is None:
        return default
    return str(value).strip()


def _num(item: dict[str, Any], key: str, default: float = 0) -> float:
    value = item.get(key, default)
    if value in (None, ""):
        return default
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{key} must be a number") from exc


def _int(item: dict[str, Any], key: str, default: int = 0) -> int:
    return int(_num(item, key, default))


def _status(kind: str, item: dict[str, Any], default: str, field: str = "status") -> str:
    status = _text(item, field, default) or default
    allowed = _STATUSES[kind]
    if status not in allowed:
        raise ValueError(f"{kind}.{field} must be one of {sorted(allowed)}")
    return status


def _id(item: dict[str, Any], prefix: str) -> str:
    return _text(item, "id") or new_id(prefix)


def _supplier(item: dict[str, Any]) -> dict[str, Any]:
    name = _text(item, "name")
    if not name:
        raise ValueError("supplier.name is required")
    return {
        "id": _id(item, "sup"),
        "name": name,
        "contact": _text(item, "contact"),
        "email": _text(item, "email"),
        "phone": _text(item, "phone"),
        "address": _text(item, "address"),
        "leadDays": _int(item, "leadDays", 7),
        "status": _status("suppliers", item, "active"),
    }


def _product(item: dict[str, Any]) -> dict[str, Any]:
    name = _text(item, "name")
    sku = _text(item, "sku")
    if not name or not sku:
        raise ValueError("product.sku and product.name are required")
    return {
        "id": _id(item, "prd"),
        "sku": sku,
        "name": name,
        "category": _text(item, "category", "未分类"),
        "unit": _text(item, "unit", "pcs"),
        "supplierId": _text(item, "supplierId"),
        "cost": round(_num(item, "cost"), 4),
        "reorderPoint": _int(item, "reorderPoint"),
        "status": _status("products", item, "active"),
    }


def _warehouse(item: dict[str, Any]) -> dict[str, Any]:
    name = _text(item, "name")
    code = _text(item, "code")
    if not name or not code:
        raise ValueError("warehouse.code and warehouse.name are required")
    return {
        "id": _id(item, "wh"),
        "code": code,
        "name": name,
        "location": _text(item, "location"),
        "status": _status("warehouses", item, "active"),
    }


def _stock(item: dict[str, Any]) -> dict[str, Any]:
    warehouse_id = _text(item, "warehouseId")
    product_id = _text(item, "productId")
    if not warehouse_id or not product_id:
        raise ValueError("stock.warehouseId and stock.productId are required")
    return {
        "warehouseId": warehouse_id,
        "productId": product_id,
        "qty": round(_num(item, "qty"), 4),
        "reserved": round(_num(item, "reserved"), 4),
    }


def _lines(item: dict[str, Any], cost_key: str) -> list[dict[str, Any]]:
    lines = item.get("lines") or []
    if not isinstance(lines, list):
        raise ValueError("order.lines must be an array")
    out = []
    for line in lines:
        if not isinstance(line, dict):
            raise ValueError("order line must be an object")
        product_id = _text(line, "productId")
        if not product_id:
            raise ValueError("order line.productId is required")
        out.append(
            {
                "productId": product_id,
                "qty": round(_num(line, "qty"), 4),
                cost_key: round(_num(line, cost_key), 4),
            }
        )
    return out


def _purchase_order(item: dict[str, Any]) -> dict[str, Any]:
    supplier_id = _text(item, "supplierId")
    warehouse_id = _text(item, "warehouseId")
    if not supplier_id or not warehouse_id:
        raise ValueError("purchaseOrder.supplierId and warehouseId are required")
    number = _text(item, "number") or f"PO-{utc_now()[:10].replace('-', '')}"
    return {
        "id": _id(item, "po"),
        "number": number,
        "supplierId": supplier_id,
        "warehouseId": warehouse_id,
        "status": _status("purchaseOrders", item, "draft"),
        "createdAt": _text(item, "createdAt") or utc_now(),
        "expectedAt": _text(item, "expectedAt"),
        "lines": _lines(item, "unitCost"),
    }


def _sales_order(item: dict[str, Any]) -> dict[str, Any]:
    warehouse_id = _text(item, "warehouseId")
    if not warehouse_id:
        raise ValueError("salesOrder.warehouseId is required")
    number = _text(item, "number") or f"SO-{utc_now()[:10].replace('-', '')}"
    return {
        "id": _id(item, "so"),
        "number": number,
        "customer": _text(item, "customer", "未命名客户"),
        "warehouseId": warehouse_id,
        "status": _status("salesOrders", item, "draft"),
        "createdAt": _text(item, "createdAt") or utc_now(),
        "lines": _lines(item, "unitPrice"),
    }


def _shipment(item: dict[str, Any]) -> dict[str, Any]:
    kind = _text(item, "type", "outbound")
    if kind not in {"inbound", "outbound"}:
        raise ValueError("shipment.type must be inbound or outbound")
    order_type = _text(item, "orderType")
    if order_type and order_type not in {"purchase", "sales"}:
        raise ValueError("shipment.orderType must be purchase or sales")
    number = _text(item, "number") or f"SH-{utc_now()[:10].replace('-', '')}"
    return {
        "id": _id(item, "sh"),
        "number": number,
        "type": kind,
        "orderId": _text(item, "orderId"),
        "orderType": order_type,
        "carrier": _text(item, "carrier"),
        "tracking": _text(item, "tracking"),
        "status": _status("shipments", item, "planned"),
        "shippedAt": _text(item, "shippedAt"),
        "deliveredAt": _text(item, "deliveredAt"),
    }


def _movement(item: dict[str, Any]) -> dict[str, Any]:
    product_id = _text(item, "productId")
    warehouse_id = _text(item, "warehouseId")
    if not product_id or not warehouse_id:
        raise ValueError("movement.productId and warehouseId are required")
    return {
        "id": _id(item, "mv"),
        "at": _text(item, "at") or utc_now(),
        "type": _status("movements", item, "adjust", field="type"),
        "productId": product_id,
        "warehouseId": warehouse_id,
        "qty": round(_num(item, "qty"), 4),
        "ref": _text(item, "ref"),
    }


def seed_state() -> dict[str, Any]:
    sup_a = "sup-qld-steel"
    sup_b = "sup-pack-co"
    prd_a = "prd-bolt-m8"
    prd_b = "prd-carton"
    prd_c = "prd-label"
    wh_a = "wh-bne"
    wh_b = "wh-cns"
    po = "po-demo-1001"
    so = "so-demo-2001"
    sh = "sh-demo-3001"
    now = utc_now()
    return {
        "version": SCHEMA_VERSION,
        "source": "theQLD-scm-seed",
        "exportedAt": now,
        "suppliers": [
            {
                "id": sup_a,
                "name": "Queensland Steel Works",
                "contact": "Alex Chen",
                "email": "alex@qldsteel.example",
                "phone": "+61 7 3000 1100",
                "address": "Eagle Farm, Brisbane",
                "leadDays": 10,
                "status": "active",
            },
            {
                "id": sup_b,
                "name": "Pacific Pack Co",
                "contact": "Mina Patel",
                "email": "mina@pacificpack.example",
                "phone": "+61 7 3000 2200",
                "address": "Portsmith, Cairns",
                "leadDays": 5,
                "status": "active",
            },
        ],
        "products": [
            {
                "id": prd_a,
                "sku": "FAST-M8-40",
                "name": "M8x40 Hex Bolt",
                "category": "紧固件",
                "unit": "pcs",
                "supplierId": sup_a,
                "cost": 0.42,
                "reorderPoint": 500,
                "status": "active",
            },
            {
                "id": prd_b,
                "sku": "PKG-CTN-12",
                "name": "12-pack Carton",
                "category": "包装",
                "unit": "pcs",
                "supplierId": sup_b,
                "cost": 1.15,
                "reorderPoint": 200,
                "status": "active",
            },
            {
                "id": prd_c,
                "sku": "LBL-A6-WHT",
                "name": "A6 Shipping Label",
                "category": "耗材",
                "unit": "roll",
                "supplierId": sup_b,
                "cost": 8.9,
                "reorderPoint": 30,
                "status": "active",
            },
        ],
        "warehouses": [
            {
                "id": wh_a,
                "code": "BNE-01",
                "name": "Brisbane DC",
                "location": "Brisbane, QLD",
                "status": "active",
            },
            {
                "id": wh_b,
                "code": "CNS-01",
                "name": "Cairns Forwarding",
                "location": "Cairns, QLD",
                "status": "active",
            },
        ],
        "stock": [
            {"warehouseId": wh_a, "productId": prd_a, "qty": 2400, "reserved": 120},
            {"warehouseId": wh_a, "productId": prd_b, "qty": 860, "reserved": 40},
            {"warehouseId": wh_a, "productId": prd_c, "qty": 18, "reserved": 0},
            {"warehouseId": wh_b, "productId": prd_b, "qty": 120, "reserved": 0},
        ],
        "purchaseOrders": [
            {
                "id": po,
                "number": "PO-2026-1001",
                "supplierId": sup_a,
                "warehouseId": wh_a,
                "status": "sent",
                "createdAt": now,
                "expectedAt": now,
                "lines": [{"productId": prd_a, "qty": 1000, "unitCost": 0.4}],
            }
        ],
        "salesOrders": [
            {
                "id": so,
                "number": "SO-2026-2001",
                "customer": "Gold Coast CLC Store",
                "warehouseId": wh_a,
                "status": "allocated",
                "createdAt": now,
                "lines": [
                    {"productId": prd_b, "qty": 40, "unitPrice": 2.5},
                    {"productId": prd_c, "qty": 2, "unitPrice": 12.0},
                ],
            }
        ],
        "shipments": [
            {
                "id": sh,
                "number": "SH-OUT-3001",
                "type": "outbound",
                "orderId": so,
                "orderType": "sales",
                "carrier": "Australia Post",
                "tracking": "AP123456789AU",
                "status": "planned",
                "shippedAt": "",
                "deliveredAt": "",
            }
        ],
        "movements": [
            {
                "id": "mv-seed-1",
                "at": now,
                "type": "receive",
                "productId": prd_a,
                "warehouseId": wh_a,
                "qty": 2400,
                "ref": "SEED",
            }
        ],
    }


class ScmStore:
    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = Path(db_path or DEFAULT_DB)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_db()

    def close(self) -> None:
        with self._lock:
            self._conn.close()

    def _init_db(self) -> None:
        with self._lock:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS snapshot (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    payload TEXT NOT NULL
                )
                """
            )
            row = self._conn.execute("SELECT payload FROM snapshot WHERE id = 1").fetchone()
            if row is None:
                self._write_unlocked(seed_state())

    def _write_unlocked(self, state: dict[str, Any]) -> dict[str, Any]:
        state = normalize_state(state)
        state["exportedAt"] = utc_now()
        self._conn.execute(
            "INSERT INTO snapshot(id, payload) VALUES (1, ?) ON CONFLICT(id) DO UPDATE SET payload = excluded.payload",
            (json.dumps(state, ensure_ascii=False),),
        )
        self._conn.commit()
        return state

    def export(self) -> dict[str, Any]:
        with self._lock:
            row = self._conn.execute("SELECT payload FROM snapshot WHERE id = 1").fetchone()
            return json.loads(row["payload"])

    def replace(self, payload: Any, source: str | None = None) -> dict[str, Any]:
        state = normalize_state(payload)
        if source:
            state["source"] = source
        with self._lock:
            return self._write_unlocked(state)

    def merge(self, payload: Any, source: str | None = None) -> dict[str, Any]:
        incoming = normalize_state(payload)
        with self._lock:
            current = json.loads(
                self._conn.execute("SELECT payload FROM snapshot WHERE id = 1").fetchone()["payload"]
            )
            merged = empty_state()
            merged["source"] = source or incoming.get("source") or current.get("source") or ""
            for name in COLLECTIONS:
                if name == "stock":
                    index = {
                        (row["warehouseId"], row["productId"]): row
                        for row in current.get("stock", [])
                    }
                    for row in incoming.get("stock", []):
                        index[(row["warehouseId"], row["productId"])] = row
                    merged["stock"] = list(index.values())
                    continue
                index = {row["id"]: row for row in current.get(name, [])}
                for row in incoming.get(name, []):
                    index[row["id"]] = row
                merged[name] = list(index.values())
            return self._write_unlocked(merged)

    def dashboard(self) -> dict[str, Any]:
        state = self.export()
        stock_value = 0.0
        low_stock = []
        products = {p["id"]: p for p in state["products"]}
        for row in state["stock"]:
            product = products.get(row["productId"])
            if not product:
                continue
            available = row["qty"] - row["reserved"]
            stock_value += row["qty"] * float(product.get("cost") or 0)
            if available <= float(product.get("reorderPoint") or 0):
                low_stock.append(
                    {
                        "productId": product["id"],
                        "sku": product["sku"],
                        "name": product["name"],
                        "warehouseId": row["warehouseId"],
                        "available": available,
                        "reorderPoint": product["reorderPoint"],
                    }
                )
        open_po = [po for po in state["purchaseOrders"] if po["status"] in {"draft", "sent", "partial"}]
        open_so = [so for so in state["salesOrders"] if so["status"] in {"draft", "allocated", "shipped"}]
        in_transit = [sh for sh in state["shipments"] if sh["status"] in {"planned", "in_transit"}]
        return {
            "suppliers": len(state["suppliers"]),
            "products": len(state["products"]),
            "warehouses": len(state["warehouses"]),
            "openPurchaseOrders": len(open_po),
            "openSalesOrders": len(open_so),
            "inTransitShipments": len(in_transit),
            "stockValue": round(stock_value, 2),
            "lowStock": low_stock,
            "source": state.get("source") or "",
            "exportedAt": state.get("exportedAt") or "",
        }

    def upsert(self, kind: str, item: dict[str, Any]) -> dict[str, Any]:
        if kind not in COLLECTIONS or kind == "stock":
            raise ValueError(f"cannot upsert {kind}")
        normalized = normalize_item(kind, item)
        with self._lock:
            state = json.loads(
                self._conn.execute("SELECT payload FROM snapshot WHERE id = 1").fetchone()["payload"]
            )
            rows = [row for row in state[kind] if row["id"] != normalized["id"]]
            rows.append(normalized)
            state[kind] = rows
            self._write_unlocked(state)
            return normalized

    def delete(self, kind: str, item_id: str) -> bool:
        if kind not in COLLECTIONS or kind in {"stock", "movements"}:
            raise ValueError(f"cannot delete {kind}")
        with self._lock:
            state = json.loads(
                self._conn.execute("SELECT payload FROM snapshot WHERE id = 1").fetchone()["payload"]
            )
            before = len(state[kind])
            state[kind] = [row for row in state[kind] if row["id"] != item_id]
            self._write_unlocked(state)
            return len(state[kind]) != before

    def adjust_stock(
        self,
        warehouse_id: str,
        product_id: str,
        qty: float,
        movement_type: str = "adjust",
        ref: str = "",
    ) -> dict[str, Any]:
        if movement_type not in _STATUSES["movements"]:
            raise ValueError("invalid movement type")
        with self._lock:
            state = json.loads(
                self._conn.execute("SELECT payload FROM snapshot WHERE id = 1").fetchone()["payload"]
            )
            found = False
            for row in state["stock"]:
                if row["warehouseId"] == warehouse_id and row["productId"] == product_id:
                    row["qty"] = round(float(row["qty"]) + float(qty), 4)
                    found = True
                    break
            if not found:
                state["stock"].append(
                    {
                        "warehouseId": warehouse_id,
                        "productId": product_id,
                        "qty": round(float(qty), 4),
                        "reserved": 0,
                    }
                )
            movement = normalize_item(
                "movements",
                {
                    "type": movement_type,
                    "productId": product_id,
                    "warehouseId": warehouse_id,
                    "qty": qty,
                    "ref": ref,
                },
            )
            state["movements"].append(movement)
            self._write_unlocked(state)
            return movement
