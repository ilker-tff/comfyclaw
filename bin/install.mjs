#!/usr/bin/env node

import { createInterface } from "node:readline";
import { execSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, writeFileSync, cpSync, rmSync, readdirSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { homedir } from "node:os";

const __dirname = dirname(fileURLToPath(import.meta.url));
const DEFAULT_URL = "http://34.30.216.121";

// New unified skills (v3)
const SKILLS = [
  "comfyui-generate",
  "comfyui-edit",
  "comfyui-video",
  "comfyui-workflow",
];

// Legacy skills (for uninstall cleanup — includes v1, v2, and v2.5 skills)
const LEGACY_SKILLS = [
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
  "comfyui-workflow-examples",
  "comfyui-text2img",
];

// ── Pretty output ──────────────────────────────────────────────────────────

const bold = (s) => `\x1b[1m${s}\x1b[0m`;
const green = (s) => `\x1b[32m${s}\x1b[0m`;
const red = (s) => `\x1b[31m${s}\x1b[0m`;
const yellow = (s) => `\x1b[33m${s}\x1b[0m`;
const dim = (s) => `\x1b[2m${s}\x1b[0m`;

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

  // Remove legacy skill entries
  for (const skill of LEGACY_SKILLS) {
    delete config.skills.entries[skill];
  }

  // Register each new skill with shared env vars
  for (const skill of SKILLS) {
    config.skills.entries[skill] = {
      enabled: true,
      env: {
        COMFY_URL: comfyUrl,
        COMFY_AUTH_HEADER: authHeader,
      },
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

  // 3. Last resort
  return join(homedir(), ".openclaw", "workspace", "skills");
}

// ── Skill file copy ────────────────────────────────────────────────────────

function installSkillFiles() {
  const skillsSource = join(__dirname, "..", "skills");
  const baseTarget = findSkillsDir();
  const installed = [];

  // Install new unified skills
  for (const skill of SKILLS) {
    const source = join(skillsSource, skill);
    if (!existsSync(source)) continue;

    const target = join(baseTarget, skill);
    mkdirSync(target, { recursive: true });
    cpSync(source, target, { recursive: true });
    installed.push(skill);
  }

  // Copy shared library to _shared/
  const sharedSource = join(skillsSource, "shared");
  const sharedTarget = join(baseTarget, "_shared");
  mkdirSync(sharedTarget, { recursive: true });
  cpSync(join(sharedSource, "comfy_lib.py"), join(sharedTarget, "comfy_lib.py"));

  // Copy shared/ directory (catalog.py, catalog.json, learning.py) into the skills dir
  const sharedSkillsTarget = join(baseTarget, "shared");
  mkdirSync(sharedSkillsTarget, { recursive: true });
  cpSync(sharedSource, sharedSkillsTarget, { recursive: true });

  // Copy workflows/ directory
  const workflowsSource = join(skillsSource, "workflows");
  if (existsSync(workflowsSource)) {
    const workflowsTarget = join(baseTarget, "workflows");
    mkdirSync(workflowsTarget, { recursive: true });
    cpSync(workflowsSource, workflowsTarget, { recursive: true });
  }

  // Remove legacy skill directories
  for (const skill of LEGACY_SKILLS) {
    const legacyPath = join(baseTarget, skill);
    if (existsSync(legacyPath)) {
      rmSync(legacyPath, { recursive: true, force: true });
    }
  }

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

  // Remove all skill directories (new + legacy)
  for (const skill of [...SKILLS, ...LEGACY_SKILLS]) {
    const skillPath = join(baseTarget, skill);
    if (existsSync(skillPath)) {
      rmSync(skillPath, { recursive: true, force: true });
      console.log(`  Removed: ${dim(skill)}`);
      removedCount++;
    }
  }

  // Remove shared libraries and workflows
  for (const dir of ["_shared", "shared", "workflows"]) {
    const dirPath = join(baseTarget, dir);
    if (existsSync(dirPath)) {
      rmSync(dirPath, { recursive: true, force: true });
      console.log(`  Removed: ${dim(dir)}`);
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
      for (const skill of [...SKILLS, ...LEGACY_SKILLS]) {
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
  console.log(dim("  4 unified skills: generate, edit, video, workflow"));
  console.log("");

  const rl = createInterface({ input: process.stdin, output: process.stdout });

  try {
    // 1. Server URL
    const comfyUrl = await ask(rl, "  ComfyUI server URL", DEFAULT_URL);

    // Close readline so we can handle raw stdin for API key
    rl.close();

    // 2. API Key (hidden input)
    const apiKey = await askHidden(null, "  API Key");
    if (!apiKey) {
      console.log(red("\n  Error: API Key is required."));
      process.exit(1);
    }

    // 3. Build auth header
    const authHeader = `Bearer ${apiKey}`;

    // 4. Test connection
    console.log("");
    process.stdout.write(`  Testing connection to ${dim(comfyUrl)}... `);
    const status = testConnection(comfyUrl, authHeader);

    if (status === 200) {
      console.log(green("connected!"));
    } else if (status === 401 || status === 403) {
      console.log(red("auth failed."));
      console.log(red("  Check your API key."));
      process.exit(1);
    } else if (status === 0) {
      console.log(yellow("unreachable."));
      console.log(yellow("  Saving config anyway — verify the URL is correct."));
    } else {
      console.log(yellow(`HTTP ${status}.`));
      console.log(yellow("  Saving config anyway."));
    }

    // 5. Install all skill files
    console.log("");
    process.stdout.write(`  Installing ${SKILLS.length} skills... `);
    const { baseTarget, installed } = installSkillFiles();
    console.log(green("done."));

    for (const skill of installed) {
      console.log(`    ${green("✓")} ${skill}`);
    }

    // 6. Update config
    console.log("");
    process.stdout.write(`  Updating openclaw.json... `);
    const configPath = updateOpenclawConfig(comfyUrl, authHeader);
    console.log(green("done."));

    // 7. Done
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
    console.log(dim('    "Create a portrait of a fantasy warrior"'));
    console.log(dim('    "Generate a landscape and crop it to widescreen"'));
    console.log(dim('    "Make a short video clip of ocean waves"'));
    console.log(dim('    "List available ComfyUI workflows"'));
    console.log("");
  } catch (err) {
    console.error(red(`\n  Error: ${err.message}`));
    process.exit(1);
  }
}

main();
