#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");

const here = __dirname;
const extract = spawnSync(process.execPath, [path.join(here, "extract_directory.js")], {
  cwd: path.resolve(here, ".."),
  encoding: "utf8",
});
assert.strictEqual(extract.status, 0, extract.stderr || extract.stdout);

const catalog = JSON.parse(fs.readFileSync(path.join(here, "directory.json"), "utf8"));
assert.ok(catalog.entryCount >= 18, `expected 18+ entries, got ${catalog.entryCount}`);
assert.strictEqual(catalog.entries.length, catalog.entryCount);

const ids = new Set(catalog.entries.map((entry) => entry.id));
for (const required of ["ATSIWLSNQ", "ATSILS", "suncoast", "LAWRIGHT"]) {
  assert.ok(ids.has(required), `missing ${required}`);
}

const suncoast = catalog.entries.find((entry) => entry.id === "suncoast");
assert.ok(suncoast.email.includes("@"));
assert.ok(suncoast.categories.includes("FAMILY"));

const cqclc = catalog.entries.find((entry) => entry.id === "central_qld_clc");
assert.ok(cqclc, "missing central_qld_clc");
assert.ok(cqclc.address.includes("Quay"));
assert.ok(cqclc.phones.some((phone) => phone.number.includes("4922")));
assert.ok(fs.existsSync(path.join(here, "directory.brief.md")));

process.stdout.write(`ok: ${catalog.entryCount} directory entries extracted\n`);
