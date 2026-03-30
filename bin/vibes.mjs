#!/usr/bin/env node

import { spawnSync } from "child_process";
import { existsSync, mkdirSync, cpSync, readFileSync, writeFileSync, readdirSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";
import { createInterface } from "readline";
import { homedir } from "os";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");
const HOME = homedir();
const INSTALL_DIR = join(HOME, ".vibes");
const SETTINGS = join(HOME, ".claude", "settings.json");

// ── Brand color: violet ─────────────────────────────────────────────────
const V = "\x1b[38;2;167;139;250m"; // #A78BFA
const R = "\x1b[0m";
const B = "\x1b[1m";
const D = "\x1b[2m";
const G = "\x1b[32m";
const RED = "\x1b[31m";

const line = (w = 60) => `${V}${"─".repeat(w)}${R}`;
const check = (msg) => console.log(`  ${G}✓${R} ${msg}`);

// ── Detect shell rc ─────────────────────────────────────────────────────
function getShellRc() {
  const shell = process.env.SHELL || "";
  if (shell.includes("zsh") || process.platform === "darwin") {
    return join(HOME, ".zshrc");
  }
  return join(HOME, ".bashrc");
}

// ── Read packs ──────────────────────────────────────────────────────────
function loadPacks() {
  const packsDir = join(ROOT, "packs");
  return readdirSync(packsDir, { withFileTypes: true })
    .filter((d) => d.isDirectory())
    .map((d) => {
      const packJson = JSON.parse(
        readFileSync(join(packsDir, d.name, "pack.json"), "utf8")
      );
      return { slug: d.name, ...packJson };
    })
    .sort((a, b) => a.slug.localeCompare(b.slug));
}

// ── Prompt ──────────────────────────────────────────────────────────────
function ask(question) {
  const rl = createInterface({ input: process.stdin, output: process.stdout });
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      rl.close();
      resolve(answer.trim());
    });
  });
}

// ── Install ─────────────────────────────────────────────────────────────
async function main() {
  console.log();
  console.log(`  ${line()}`);
  try {
    spawnSync("python3", [join(ROOT, "scripts", "banner.py"), "vibes"], {
      stdio: "inherit",
    });
  } catch {
    console.log(`  ${V}${B} VIBESCC ${R}`);
  }
  console.log(`  ${D}Branded Claude Code${R}`);
  console.log(`  ${line()}`);
  console.log();

  const packs = loadPacks();

  packs.forEach((p, i) => {
    console.log(`    ${V}${B}${i + 1}${R}  ${p.name}`);
  });
  console.log();
  console.log(`    ${V}${B}a${R}  Install all`);
  console.log();

  const choice = (await ask(`  ${V}→${R} `)) || "a";

  let selected;
  if (choice.toLowerCase() === "a") {
    selected = packs;
  } else {
    const nums = choice.split(/[,\s]+/).map(Number);
    selected = nums
      .filter((n) => n >= 1 && n <= packs.length)
      .map((n) => packs[n - 1]);
  }

  if (selected.length === 0) {
    console.log(`\n  ${RED}Nothing selected.${R}\n`);
    process.exit(1);
  }

  console.log();
  console.log(`  ${line()}`);
  console.log();

  // Copy files
  mkdirSync(INSTALL_DIR, { recursive: true });
  cpSync(join(ROOT, "scripts"), join(INSTALL_DIR, "scripts"), { recursive: true });
  cpSync(join(ROOT, "packs"), join(INSTALL_DIR, "packs"), { recursive: true });

  // Shell rc
  const shellRc = getShellRc();
  if (!existsSync(shellRc)) writeFileSync(shellRc, "");
  let rcContent = readFileSync(shellRc, "utf8");

  rcContent = rcContent
    .split("\n")
    .filter((line) => !line.includes("# vibes:"))
    .join("\n");

  const launcher = join(INSTALL_DIR, "scripts", "vibescc-launch.py");

  for (const pack of selected) {
    const packDir = join(INSTALL_DIR, "packs", pack.slug);
    const alias = `alias ${pack.slug}='python3 ${launcher} --config ${packDir}' # vibes:${pack.slug}`;
    rcContent += `\n${alias}`;
    check(`${B}${pack.slug}${R} ${D}→ ${pack.name}${R}`);
  }

  // Write verbs from last selected pack
  const lastPack = selected[selected.length - 1];
  if (existsSync(SETTINGS)) {
    try {
      const settings = JSON.parse(readFileSync(SETTINGS, "utf8"));
      settings.spinnerVerbs = { mode: "replace", verbs: lastPack.verbs };
      writeFileSync(SETTINGS, JSON.stringify(settings, null, 2) + "\n");
    } catch {}
  }

  writeFileSync(shellRc, rcContent.replace(/\n{3,}/g, "\n\n") + "\n");

  console.log();
  console.log(`  ${line()}`);
  console.log();
  console.log(`  ${G}${B}Installed.${R} Open a new tab and run:`);
  console.log();
  console.log(`    ${V}${B}${selected[0].slug}${R}`);
  if (selected.length > 1) {
    console.log(`    ${D}or: ${selected.slice(1).map(p => p.slug).join(", ")}${R}`);
  }
  console.log();
}

// ── Uninstall ───────────────────────────────────────────────────────────
function uninstall() {
  console.log();
  console.log(`  ${line()}`);
  console.log(`  ${V}${B} VIBESCC ${R}${D} Uninstall${R}`);
  console.log(`  ${line()}`);
  console.log();

  const shellRc = getShellRc();
  if (existsSync(shellRc)) {
    const cleaned = readFileSync(shellRc, "utf8")
      .split("\n")
      .filter((line) => !line.includes("# vibes:"))
      .join("\n");
    writeFileSync(shellRc, cleaned.replace(/\n{3,}/g, "\n\n") + "\n");
    check("Removed aliases");
  }

  if (existsSync(SETTINGS)) {
    try {
      const settings = JSON.parse(readFileSync(SETTINGS, "utf8"));
      delete settings.spinnerVerbs;
      writeFileSync(SETTINGS, JSON.stringify(settings, null, 2) + "\n");
      check("Removed spinner verbs");
    } catch {}
  }

  console.log();
  console.log(`  ${G}${B}Done.${R} Aliases and verbs removed.`);
  console.log();
}

// ── Entry ───────────────────────────────────────────────────────────────
if (process.argv[2] === "uninstall") {
  uninstall();
} else {
  main().catch(console.error);
}
