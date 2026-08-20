from __future__ import annotations

import json
import sys
import tempfile
import threading
import unittest
from http.client import HTTPConnection
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from server import make_server  # noqa: E402
from store import ScmStore, normalize_state, seed_state  # noqa: E402


class StoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "scm.sqlite"
        self.store = ScmStore(self.db)

    def tearDown(self) -> None:
        self.store.close()
        self.tmp.cleanup()

    def test_seed_dashboard(self) -> None:
        dash = self.store.dashboard()
        self.assertGreaterEqual(dash["products"], 3)
        self.assertGreater(dash["stockValue"], 0)
        self.assertTrue(any(item["sku"] == "LBL-A6-WHT" for item in dash["lowStock"]))

    def test_replace_mount(self) -> None:
        sample = json.loads((ROOT / "sample-local-export.json").read_text(encoding="utf-8"))
        state = self.store.replace(sample, source="unit-test")
        self.assertEqual(state["source"], "unit-test")
        self.assertEqual(len(state["products"]), 1)
        self.assertEqual(state["products"][0]["sku"], "LOCAL-SKU-001")

    def test_merge_keeps_existing_and_overwrites_ids(self) -> None:
        sample = json.loads((ROOT / "sample-local-export.json").read_text(encoding="utf-8"))
        self.store.merge(sample, source="merge-test")
        state = self.store.export()
        skus = {p["sku"] for p in state["products"]}
        self.assertIn("LOCAL-SKU-001", skus)
        self.assertIn("FAST-M8-40", skus)

    def test_adjust_stock_creates_movement(self) -> None:
        movement = self.store.adjust_stock("wh-bne", "prd-bolt-m8", 10, "receive", "ASN-1")
        self.assertEqual(movement["qty"], 10)
        stock = [
            row
            for row in self.store.export()["stock"]
            if row["warehouseId"] == "wh-bne" and row["productId"] == "prd-bolt-m8"
        ][0]
        self.assertEqual(stock["qty"], 2410)

    def test_rejects_bad_version(self) -> None:
        with self.assertRaises(ValueError):
            normalize_state({"version": 99, "suppliers": []})


class ApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        db = Path(self.tmp.name) / "scm.sqlite"
        self.httpd = make_server("127.0.0.1", 0, db)
        self.port = self.httpd.server_address[1]
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self) -> None:
        self.httpd.shutdown()
        self.httpd.server_close()
        self.tmp.cleanup()

    def _request(self, method: str, path: str, body: dict | None = None) -> tuple[int, dict | str]:
        conn = HTTPConnection("127.0.0.1", self.port, timeout=5)
        payload = json.dumps(body).encode("utf-8") if body is not None else None
        headers = {"Content-Type": "application/json"} if body is not None else {}
        conn.request(method, path, body=payload, headers=headers)
        response = conn.getresponse()
        raw = response.read().decode("utf-8")
        conn.close()
        try:
            return response.status, json.loads(raw)
        except json.JSONDecodeError:
            return response.status, raw

    def test_health_and_index(self) -> None:
        status, payload = self._request("GET", "/api/health")
        self.assertEqual(status, 200)
        self.assertEqual(payload["ok"], True)
        status, html = self._request("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn("供应链", html)

    def test_mount_endpoint_replaces_state(self) -> None:
        sample = json.loads((ROOT / "sample-local-export.json").read_text(encoding="utf-8"))
        status, payload = self._request(
            "POST",
            "/api/mount",
            {"mode": "replace", "source": "api-test", "data": sample},
        )
        self.assertEqual(status, 200)
        self.assertEqual(payload["ok"], True)
        self.assertEqual(len(payload["state"]["suppliers"]), 1)
        status, state = self._request("GET", "/api/state")
        self.assertEqual(status, 200)
        self.assertEqual(state["source"], "api-test")

    def test_create_supplier(self) -> None:
        status, payload = self._request(
            "POST",
            "/api/suppliers",
            {"name": "New Co", "email": "ops@newco.example"},
        )
        self.assertEqual(status, 201)
        self.assertEqual(payload["name"], "New Co")
        status, rows = self._request("GET", "/api/suppliers")
        self.assertGreaterEqual(len(rows), 3)


class SeedFixtureTests(unittest.TestCase):
    def test_seed_normalizes(self) -> None:
        state = normalize_state(seed_state())
        self.assertEqual(state["version"], 1)
        self.assertEqual(len(state["warehouses"]), 2)


if __name__ == "__main__":
    unittest.main()
