#!/usr/bin/env node

import { execSync, spawnSync } from "child_process";
import { existsSync, mkdirSync, cpSync, readFileSync, writeFileSync, readdirSync, readlinkSync } from "fs";
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
  yellow: "\x1b[33m",
  red: "\x1b[31m",
  cyan: "\x1b[36m",
};

const info = (msg) => console.log(`${c.green}▸${c.reset} ${msg}`);
const warn = (msg) => console.log(`${c.yellow}▸${c.reset} ${msg}`);

// ── Banner ──────────────────────────────────────────────────────────────
function showBanner() {
  try {
    spawnSync("python3", [join(ROOT, "scripts", "banner.py"), "vibescc"], {
      stdio: "inherit",
    });
  } catch {
    console.log(`\n  ${c.bold}VIBESCC${c.reset}\n`);
  }
  console.log(`  ${c.dim}branded Claude Code${c.reset}\n`);
}

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
  showBanner();

  const packs = loadPacks();

  // Show packs
  console.log("  Pick what to install:\n");
  packs.forEach((p, i) => {
    console.log(
      `    ${c.bold}${i + 1})${c.reset}  ${p.slug}  ${c.dim}(${p.name}, ${p.colors.body})${c.reset}`
    );
  });
  console.log(`\n    ${c.bold}a)${c.reset}  all of the above\n`);

  const choice = (await ask(`  Choice [a]: `)) || "a";

  // Parse selection
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
    console.log(`${c.red}Nothing selected.${c.reset}`);
    process.exit(1);
  }

  console.log();

  // ── Copy files to ~/.vibescc ────────────────────────────────────────
  info(`Installing to ${c.bold}${INSTALL_DIR}${c.reset}`);
  mkdirSync(INSTALL_DIR, { recursive: true });
  cpSync(join(ROOT, "scripts"), join(INSTALL_DIR, "scripts"), { recursive: true });
  cpSync(join(ROOT, "packs"), join(INSTALL_DIR, "packs"), { recursive: true });

  // ── Shell rc ────────────────────────────────────────────────────────
  const shellRc = getShellRc();
  if (!existsSync(shellRc)) writeFileSync(shellRc, "");
  let rcContent = readFileSync(shellRc, "utf8");

  // Remove old vibescc aliases
  rcContent = rcContent
    .split("\n")
    .filter((line) => !line.includes("# vibes:"))
    .join("\n");

  const launcher = join(INSTALL_DIR, "scripts", "vibescc-launch.py");

  for (const pack of selected) {
    // Show banner for each pack
    try {
      spawnSync("python3", [join(ROOT, "scripts", "banner.py"), pack.slug], {
        stdio: "inherit",
      });
    } catch {}

    // Add alias
    const packDir = join(INSTALL_DIR, "packs", pack.slug);
    const alias = `alias ${pack.slug}='python3 ${launcher} --config ${packDir}' # vibes:${pack.slug}`;
    rcContent += `\n${alias}`;

    info(`Installed ${c.bold}${pack.name}${c.reset} → type ${c.bold}${pack.slug}${c.reset} to launch`);
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

  // ── Done ────────────────────────────────────────────────────────────
  console.log();
  console.log(`${c.green}${c.bold}Done!${c.reset} Open a new terminal tab, then:\n`);
  for (const pack of selected) {
    console.log(`  ${c.bold}${pack.slug}${c.reset}              launch with branded crab`);
  }
  console.log(
    `\n  All claude flags work: ${c.bold}--resume${c.reset}, ${c.bold}--dangerously-skip-permissions${c.reset}, etc.`
  );
  console.log(`  Switch verbs: ${c.bold}yc --verbs looksmaxxing${c.reset}`);
  console.log(`\n  To uninstall: ${c.bold}bunx vibes uninstall${c.reset}\n`);
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
    info("Removed aliases from " + shellRc);
  }

  if (existsSync(SETTINGS)) {
    try {
      const settings = JSON.parse(readFileSync(SETTINGS, "utf8"));
      delete settings.spinnerVerbs;
      writeFileSync(SETTINGS, JSON.stringify(settings, null, 2) + "\n");
      info("Removed spinner verbs");
    } catch {}
  }

  console.log(`\n${c.green}${c.bold}Done!${c.reset} All vibescc aliases and verbs removed.\n`);
}

// ── Entry ───────────────────────────────────────────────────────────────
if (process.argv[2] === "uninstall") {
  uninstall();
} else {
  main().catch(console.error);
}
