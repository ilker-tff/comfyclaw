#!/usr/bin/env node

import { createInterface } from "node:readline";
import { execSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, writeFileSync, cpSync, rmSync, readdirSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { homedir } from "node:os";

const __dirname = dirname(fileURLToPath(import.meta.url));
const DEFAULT_URL = "http://34.30.216.121";

// ── Skill registry ────────────────────────────────────────────────────────

// Generation skills
const GENERATION_SKILLS = [
  "comfyui-generate-image",
  "comfyui-portrait",
  "comfyui-landscape-batch",
  "comfyui-lora",
  "comfyui-img2img-remix",
  "comfyui-crop",
  "comfyui-crop-then-refine",
  "comfyui-animated-webp",
  "comfyui-video-clip",
  "comfyui-flux-multi-img2img",
  "comfyui-img2video",
  "comfyui-preview-image",
  "comfyui-preview-img2img",
  "comfyui-preview-character",
];

// Utility skills
const UTILITY_SKILLS = [
  "comfyui-upload-image",
  "comfyui-upload-video",
  "comfyui-download-image",
  "comfyui-download-video",
  "comfyui-progress",
  "comfyui-queue-status",
  "comfyui-server-status",
  "comfyui-validate-models",
  "comfyui-list-assets",
  "comfyui-delete-job",
];

// Reference-only (no env vars needed)
const REFERENCE_SKILLS = [
  "comfyui-workflow-examples",
];

const ALL_SKILLS = [...GENERATION_SKILLS, ...UTILITY_SKILLS, ...REFERENCE_SKILLS];
const SKILLS_WITH_ENV = [...GENERATION_SKILLS, ...UTILITY_SKILLS];

// ── Pretty output ──────────────────────────────────────────────────────────

const bold = (s) => `\x1b[1m${s}\x1b[0m`;
const green = (s) => `\x1b[32m${s}\x1b[0m`;
const red = (s) => `\x1b[31m${s}\x1b[0m`;
const yellow = (s) => `\x1b[33m${s}\x1b[0m`;
const dim = (s) => `\x1b[2m${s}\x1b[0m`;
const cyan = (s) => `\x1b[36m${s}\x1b[0m`;

// ── Readline helpers ───────────────────────────────────────────────────────

function ask(rl, question, defaultVal) {
  const prompt = defaultVal ? `${question} ${dim(`[${defaultVal}]`)}: ` : `${question}: `;
  return new Promise((resolve) => {
    rl.question(prompt, (answer) => resolve(answer.trim() || defaultVal || ""));
  });
}

function askHidden(rl, question) {
  return new Promise((resolve) => {
    const output = process.stdout;
    output.write(`${question}: `);

    const stdin = process.stdin;
    const wasRaw = stdin.isRaw;
    if (stdin.setRawMode) stdin.setRawMode(true);

    let password = "";
    const onData = (ch) => {
      const c = ch.toString("utf8");
      if (c === "\n" || c === "\r" || c === "\u0004") {
        if (stdin.setRawMode) stdin.setRawMode(wasRaw);
        stdin.removeListener("data", onData);
        output.write("\n");
        resolve(password);
      } else if (c === "\u0003") {
        process.exit(1);
      } else if (c === "\u007F" || c === "\b") {
        if (password.length > 0) {
          password = password.slice(0, -1);
          output.write("\b \b");
        }
      } else {
        password += c;
        output.write("*");
      }
    };
    stdin.resume();
    stdin.on("data", onData);
  });
}

// ── Connection test ────────────────────────────────────────────────────────

function testConnection(url, authHeader) {
  try {
    const result = execSync(
      `curl -s -o /dev/null -w "%{http_code}" -H "Authorization: ${authHeader}" "${url}/system_stats"`,
      { timeout: 10000, encoding: "utf8" }
    ).trim();
    return parseInt(result, 10);
  } catch {
    return 0;
  }
}

// ── Config update ──────────────────────────────────────────────────────────

function updateOpenclawConfig(comfyUrl, authHeader) {
  const configPath = join(homedir(), ".openclaw", "openclaw.json");
  let config = {};

  if (existsSync(configPath)) {
    try {
      config = JSON.parse(readFileSync(configPath, "utf8"));
    } catch {
      config = {};
    }
  }

  if (!config.skills) config.skills = {};
  if (!config.skills.entries) config.skills.entries = {};

  // Register each skill with shared env vars
  for (const skill of SKILLS_WITH_ENV) {
    config.skills.entries[skill] = {
      enabled: true,
      env: {
        COMFY_URL: comfyUrl,
        COMFY_AUTH_HEADER: authHeader,
      },
    };
  }

  // Reference skills — no env needed
  for (const skill of REFERENCE_SKILLS) {
    config.skills.entries[skill] = {
      enabled: true,
    };
  }

  const configDir = dirname(configPath);
  if (!existsSync(configDir)) mkdirSync(configDir, { recursive: true });

  writeFileSync(configPath, JSON.stringify(config, null, 2) + "\n");
  return configPath;
}

// ── Detect OpenClaw skills directory ────────────────────────────────────────

function findSkillsDir() {
  // 1. Try to find openclaw binary and resolve its package skills dir
  try {
    const openclawBin = execSync("which openclaw", { encoding: "utf8" }).trim();
    if (openclawBin) {
      let resolved;
      try {
        resolved = execSync(`readlink -f "${openclawBin}" 2>/dev/null || readlink "${openclawBin}" 2>/dev/null`, { encoding: "utf8" }).trim();
      } catch {
        resolved = openclawBin;
      }
      const parts = resolved.split("/");
      const nmIdx = parts.lastIndexOf("node_modules");
      if (nmIdx !== -1) {
        const pkgSkills = join(parts.slice(0, nmIdx + 1).join("/"), "openclaw", "skills");
        if (existsSync(pkgSkills)) return pkgSkills;
      }
      const binDir = dirname(resolved);
      const candidate = join(dirname(binDir), "lib", "node_modules", "openclaw", "skills");
      if (existsSync(candidate)) return candidate;
    }
  } catch { /* openclaw not in PATH */ }

  // 2. Fallback: check common locations
  const nvmBase = join(homedir(), ".nvm", "versions", "node");
  if (existsSync(nvmBase)) {
    try {
      const versions = readdirSync(nvmBase).sort().reverse();
      for (const v of versions) {
        const candidate = join(nvmBase, v, "lib", "node_modules", "openclaw", "skills");
        if (existsSync(candidate)) return candidate;
      }
    } catch { /* ignore */ }
  }

  const fallbacks = [
    join("/usr", "local", "lib", "node_modules", "openclaw", "skills"),
    join("/usr", "lib", "node_modules", "openclaw", "skills"),
  ];

  for (const fb of fallbacks) {
    if (existsSync(fb)) return fb;
  }

  // 3. Last resort: workspace dir
  return join(homedir(), ".openclaw", "workspace", "skills");
}

// ── Skill file copy ────────────────────────────────────────────────────────

function installSkillFiles() {
  const skillsSource = join(__dirname, "..", "skills");
  const sharedSource = join(skillsSource, "shared", "comfy_lib.py");
  const baseTarget = findSkillsDir();
  const installed = [];

  for (const skill of ALL_SKILLS) {
    const source = join(skillsSource, skill);
    if (!existsSync(source)) continue;

    const target = join(baseTarget, skill);
    mkdirSync(target, { recursive: true });
    cpSync(source, target, { recursive: true });
    installed.push(skill);
  }

  // Install shared library at _shared/comfy_lib.py
  const sharedTarget = join(baseTarget, "_shared");
  mkdirSync(sharedTarget, { recursive: true });
  cpSync(sharedSource, join(sharedTarget, "comfy_lib.py"));

  return { baseTarget, installed };
}

// ── Uninstall ──────────────────────────────────────────────────────────────

function uninstall() {
  console.log("");
  console.log(bold("  ComfyClaw — Uninstaller"));
  console.log("");

  const baseTarget = findSkillsDir();
  console.log(`  Skills dir: ${dim(baseTarget)}`);
  console.log("");
  const configPath = join(homedir(), ".openclaw", "openclaw.json");
  let removedCount = 0;

  // Remove all skill directories
  for (const skill of ALL_SKILLS) {
    const skillPath = join(baseTarget, skill);
    if (existsSync(skillPath)) {
      rmSync(skillPath, { recursive: true, force: true });
      console.log(`  Removed: ${dim(skill)}`);
      removedCount++;
    }
  }

  // Remove shared library
  const sharedPath = join(baseTarget, "_shared");
  if (existsSync(sharedPath)) {
    rmSync(sharedPath, { recursive: true, force: true });
  }

  // Also remove legacy skill names if present
  for (const legacy of ["comfyui-text2img"]) {
    const legacyPath = join(baseTarget, legacy);
    if (existsSync(legacyPath)) {
      rmSync(legacyPath, { recursive: true, force: true });
      console.log(`  Removed: ${dim(`${legacy} (legacy)`)}`);
      removedCount++;
    }
  }

  if (removedCount === 0) {
    console.log(dim("  No skill files found (already removed)."));
  }

  // Remove config entries
  if (existsSync(configPath)) {
    try {
      const config = JSON.parse(readFileSync(configPath, "utf8"));
      let removedEntries = 0;
      for (const skill of [...ALL_SKILLS, "comfyui-text2img"]) {
        if (config.skills?.entries?.[skill]) {
          delete config.skills.entries[skill];
          removedEntries++;
        }
      }
      if (removedEntries > 0) {
        writeFileSync(configPath, JSON.stringify(config, null, 2) + "\n");
        console.log(`  Removed ${removedEntries} config entries from: ${dim(configPath)}`);
      } else {
        console.log(dim("  No config entries found (already removed)."));
      }
    } catch {
      console.log(yellow("  Could not parse openclaw.json — skip config cleanup."));
    }
  }

  console.log("");
  console.log(green(bold("  ✓ Uninstalled.")));
  console.log(`  Run ${bold("openclaw gateway restart")} to apply.`);
  console.log("");
}

// ── Main ───────────────────────────────────────────────────────────────────

async function main() {
  const args = process.argv.slice(2);

  if (args.includes("uninstall") || args.includes("--uninstall") || args.includes("remove")) {
    uninstall();
    return;
  }

  console.log("");
  console.log(bold("  ComfyClaw — OpenClaw Installer"));
  console.log(dim(`  ${GENERATION_SKILLS.length} generation + ${UTILITY_SKILLS.length} utility + ${REFERENCE_SKILLS.length} reference skills`));
  console.log("");

  console.log(dim("  Generation skills:"));
  for (const skill of GENERATION_SKILLS) {
    console.log(dim(`    ${skill}`));
  }
  console.log(dim("  Utility skills:"));
  for (const skill of UTILITY_SKILLS) {
    console.log(dim(`    ${skill}`));
  }
  console.log(dim("  Reference:"));
  for (const skill of REFERENCE_SKILLS) {
    console.log(dim(`    ${skill}`));
  }
  console.log("");

  const rl = createInterface({ input: process.stdin, output: process.stdout });

  try {
    // 1. Server URL
    const comfyUrl = await ask(rl, "  ComfyUI server URL", DEFAULT_URL);

    // 2. Auth method
    const authMethod = await ask(rl, "  Auth method (1=username/password, 2=API key)", "2");

    let authHeader;

    if (authMethod === "2") {
      // API key auth
      rl.close();
      const apiKey = await askHidden(null, "  API key");
      if (!apiKey) {
        console.log(red("\n  Error: API key is required."));
        process.exit(1);
      }
      authHeader = `Bearer ${apiKey}`;
    } else {
      // Username/password auth
      const username = await ask(rl, "  Username");
      if (!username) {
        console.log(red("\n  Error: Username is required."));
        process.exit(1);
      }
      rl.close();
      const password = await askHidden(null, "  Password");
      if (!password) {
        console.log(red("\n  Error: Password is required."));
        process.exit(1);
      }
      authHeader = `Basic ${Buffer.from(`${username}:${password}`).toString("base64")}`;
    }

    // 3. Test connection
    console.log("");
    process.stdout.write(`  Testing connection to ${dim(comfyUrl)}... `);
    const status = testConnection(comfyUrl, authHeader);

    if (status === 200) {
      console.log(green("connected!"));
    } else if (status === 401 || status === 403) {
      console.log(red("auth failed."));
      console.log(red("  Check your credentials."));
      process.exit(1);
    } else if (status === 0) {
      console.log(yellow("unreachable."));
      console.log(yellow("  Saving config anyway — verify the URL is correct."));
    } else {
      console.log(yellow(`HTTP ${status}.`));
      console.log(yellow("  Saving config anyway."));
    }

    // 4. Install all skill files
    console.log("");
    process.stdout.write(`  Installing ${ALL_SKILLS.length} skills... `);
    const { baseTarget, installed } = installSkillFiles();
    console.log(green("done."));
    console.log("");

    const genInstalled = installed.filter((s) => GENERATION_SKILLS.includes(s));
    const utilInstalled = installed.filter((s) => UTILITY_SKILLS.includes(s));
    const refInstalled = installed.filter((s) => REFERENCE_SKILLS.includes(s));

    if (genInstalled.length) {
      console.log(`  ${cyan("Generation:")}`);
      for (const skill of genInstalled) console.log(`    ${green("✓")} ${skill}`);
    }
    if (utilInstalled.length) {
      console.log(`  ${cyan("Utility:")}`);
      for (const skill of utilInstalled) console.log(`    ${green("✓")} ${skill}`);
    }
    if (refInstalled.length) {
      console.log(`  ${cyan("Reference:")}`);
      for (const skill of refInstalled) console.log(`    ${green("✓")} ${skill}`);
    }

    // 5. Update config
    console.log("");
    process.stdout.write(`  Updating openclaw.json... `);
    const configPath = updateOpenclawConfig(comfyUrl, authHeader);
    console.log(green("done."));

    // 6. Done
    console.log("");
    console.log(green(bold(`  ✓ ${installed.length} skills installed successfully!`)));
    console.log("");
    console.log(`  Skills: ${dim(baseTarget)}`);
    console.log(`  Config: ${dim(configPath)}`);
    console.log("");
    console.log(`  Next: ${bold("openclaw gateway restart")} or ${bold("/new")} in chat`);
    console.log("");
    console.log(dim("  Try these:"));
    console.log(dim('    "Generate an image of a sunset over mountains"'));
    console.log(dim('    "Create a portrait and make it look like a watercolor"'));
    console.log(dim('    "Check server status"'));
    console.log(dim('    "Upload my photo and turn it into a video"'));
    console.log(dim('    "Give me 3 landscape options, I\'ll pick one to restyle"'));
    console.log("");
  } catch (err) {
    console.error(red(`\n  Error: ${err.message}`));
    process.exit(1);
  }
}

main();
