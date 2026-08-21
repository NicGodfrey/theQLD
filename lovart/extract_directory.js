#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const vm = require("vm");

const repoRoot = path.resolve(__dirname, "..");
const constructPath = path.join(repoRoot, "js", "directoryConstruct.js");
const commonPath = path.join(repoRoot, "js", "commonFuncs.js");
const outJson = path.join(__dirname, "directory.json");
const outBrief = path.join(__dirname, "directory.brief.md");

function stripHtml(value) {
  return String(value || "")
    .replace(/<br\s*\/?>/gi, "\n")
    .replace(/<[^>]+>/g, "")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/[ \t]+\n/g, "\n")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

function phonesOf(phone) {
  if (!phone || phone === "NONE") {
    return [];
  }
  if (typeof phone === "string") {
    return [{ label: "Phone", number: phone }];
  }
  if (!Array.isArray(phone)) {
    return [];
  }
  if (Array.isArray(phone[0])) {
    const numbers = phone[0];
    const labels = Array.isArray(phone[1]) ? phone[1] : [];
    return numbers.map((number, i) => ({
      label: labels[i] || "Phone",
      number,
    }));
  }
  return phone
    .filter((value) => typeof value === "string" && value)
    .map((number) => ({ label: "Phone", number }));
}

const sandbox = {
  console: { log() {}, warn() {}, error() {} },
  Array,
  Object,
  String,
  Number,
  Boolean,
  JSON,
  Math,
};
vm.createContext(sandbox);
vm.runInContext(fs.readFileSync(commonPath, "utf8"), sandbox, { filename: "commonFuncs.js" });
vm.runInContext(fs.readFileSync(constructPath, "utf8"), sandbox, { filename: "directoryConstruct.js" });

const rawDict = sandbox.dict;
const categoriesDict = sandbox.categoriesDict;
const entries = Object.entries(rawDict).map(([id, entry]) => ({
  id,
  name: entry.name,
  logo: entry.imgPath || "",
  about: stripHtml(entry.about),
  website: entry.url === "NONE" ? "" : entry.url || "",
  email: entry.email || "",
  phones: phonesOf(entry.rawPhone || entry.phone),
  address: entry.addressDisp || "",
  addressMap: entry.addressLink || "",
  factSheet: entry.fsURL ? `factSheets/${entry.fsURL}.html` : "",
  categories: entry.categories || [],
  aboutLong: stripHtml(entry.aboutFS),
  howTheyHelp: stripHtml(entry.howHelpFS),
  howToApply: stripHtml(entry.applyText),
  social: {
    facebook: entry.fb || "",
    linkedin: entry.linkedin || "",
    twitter: entry.twitter || "",
    instagram: entry.insta || "",
  },
}));

entries.sort((a, b) => a.name.localeCompare(b.name));

const catalog = {
  title: "The Queensland Legal Directory",
  sourceSite: "https://theqld.com/legalDirectory.html",
  repo: "https://github.com/NicGodfrey/theQLD",
  exportedAt: new Date().toISOString(),
  entryCount: entries.length,
  categories: categoriesDict,
  entries,
};

fs.writeFileSync(outJson, JSON.stringify(catalog, null, 2) + "\n");

const byCategory = {};
for (const [code, label] of Object.entries(categoriesDict)) {
  byCategory[code] = { code, label, entries: [] };
}
for (const entry of entries) {
  for (const code of entry.categories) {
    if (!byCategory[code]) {
      byCategory[code] = { code, label: code, entries: [] };
    }
    byCategory[code].entries.push(entry.name);
  }
}

const briefLines = [
  `# ${catalog.title}`,
  "",
  `- Source: ${catalog.sourceSite}`,
  `- Entries: ${catalog.entryCount}`,
  `- Exported: ${catalog.exportedAt}`,
  "",
  "## Organisations",
  "",
];

for (const entry of entries) {
  const phone = entry.phones.map((p) => (p.label && p.label !== "Phone" ? `${p.label}: ${p.number}` : p.number)).join(" / ");
  briefLines.push(`### ${entry.name}`);
  briefLines.push(`- ID: ${entry.id}`);
  briefLines.push(`- Areas: ${entry.categories.join(", ")}`);
  if (entry.website) briefLines.push(`- Website: ${entry.website}`);
  if (entry.email) briefLines.push(`- Email: ${entry.email}`);
  if (phone) briefLines.push(`- Phone: ${phone}`);
  if (entry.address) briefLines.push(`- Address: ${entry.address}`);
  briefLines.push(`- ${entry.about}`);
  briefLines.push("");
}

briefLines.push("## By legal area");
briefLines.push("");
for (const group of Object.values(byCategory)) {
  briefLines.push(`- **${group.label}** (${group.code}): ${group.entries.join("; ") || "(none)"}`);
}
briefLines.push("");

fs.writeFileSync(outBrief, briefLines.join("\n"));
process.stdout.write(`Wrote ${catalog.entryCount} entries to ${path.relative(repoRoot, outJson)}\n`);
