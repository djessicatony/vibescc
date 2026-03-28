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

// ── Colors ──────────────────────────────────────────────────────────────
const c = {
  reset: "\x1b[0m",
  bold: "\x1b[1m",
  dim: "\x1b[2m",
  green: "\x1b[32m",
  red: "\x1b[31m",
};

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
  // Banner
  try {
    spawnSync("python3", [join(ROOT, "scripts", "banner.py"), "vibes"], {
      stdio: "inherit",
    });
  } catch {
    console.log(`\n  ${c.bold}vibescc${c.reset}\n`);
  }

  const packs = loadPacks();

  console.log(`  ${c.dim}Branded crab colors + spinner verbs for Claude Code${c.reset}`);
  console.log();

  // Pack list
  packs.forEach((p, i) => {
    console.log(`    ${c.bold}${i + 1}${c.reset}  ${p.name}`);
  });
  console.log();
  console.log(`    ${c.bold}a${c.reset}  all`);
  console.log();

  const choice = (await ask(`  → `)) || "a";

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
    console.log(`\n  ${c.red}Nothing selected.${c.reset}\n`);
    process.exit(1);
  }

  // Install
  console.log();
  mkdirSync(INSTALL_DIR, { recursive: true });
  cpSync(join(ROOT, "scripts"), join(INSTALL_DIR, "scripts"), { recursive: true });
  cpSync(join(ROOT, "packs"), join(INSTALL_DIR, "packs"), { recursive: true });

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
    console.log(`  ${c.green}+${c.reset} ${c.bold}${pack.slug}${c.reset}  ${c.dim}${pack.name}${c.reset}`);
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

  // Done
  console.log();
  console.log(`  ${c.green}${c.bold}Installed.${c.reset} Open a new tab and run:\n`);
  console.log(`    ${c.bold}${selected[0].slug}${c.reset}`);
  if (selected.length > 1) {
    console.log(`    ${c.dim}or: ${selected.slice(1).map(p => p.slug).join(", ")}${c.reset}`);
  }
  console.log();
}

// ── Uninstall ───────────────────────────────────────────────────────────
function uninstall() {
  const shellRc = getShellRc();
  if (existsSync(shellRc)) {
    const cleaned = readFileSync(shellRc, "utf8")
      .split("\n")
      .filter((line) => !line.includes("# vibes:"))
      .join("\n");
    writeFileSync(shellRc, cleaned.replace(/\n{3,}/g, "\n\n") + "\n");
  }

  if (existsSync(SETTINGS)) {
    try {
      const settings = JSON.parse(readFileSync(SETTINGS, "utf8"));
      delete settings.spinnerVerbs;
      writeFileSync(SETTINGS, JSON.stringify(settings, null, 2) + "\n");
    } catch {}
  }

  console.log(`\n  ${c.green}${c.bold}Uninstalled.${c.reset} Aliases and verbs removed.\n`);
}

// ── Entry ───────────────────────────────────────────────────────────────
if (process.argv[2] === "uninstall") {
  uninstall();
} else {
  main().catch(console.error);
}
