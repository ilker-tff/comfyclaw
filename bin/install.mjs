#!/usr/bin/env node

import { createInterface } from "node:readline";
import { execSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, writeFileSync, cpSync, rmSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { homedir } from "node:os";

const __dirname = dirname(fileURLToPath(import.meta.url));
const SKILL_NAME = "comfyui-text2img";
const DEFAULT_URL = "http://34.30.216.121";

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

  config.skills.entries[SKILL_NAME] = {
    enabled: true,
    env: {
      COMFY_URL: comfyUrl,
      COMFY_AUTH_HEADER: authHeader,
    },
  };

  // Ensure directory exists
  const configDir = dirname(configPath);
  if (!existsSync(configDir)) mkdirSync(configDir, { recursive: true });

  writeFileSync(configPath, JSON.stringify(config, null, 2) + "\n");
  return configPath;
}

// ── Skill file copy ────────────────────────────────────────────────────────

function installSkillFiles() {
  const source = join(__dirname, "..", "skill");
  const targets = [
    join(homedir(), ".openclaw", "workspace", "skills", SKILL_NAME),
    join(homedir(), ".openclaw", "skills", SKILL_NAME),
  ];

  // Install to workspace/skills (highest precedence)
  const target = targets[0];
  mkdirSync(target, { recursive: true });
  cpSync(source, target, { recursive: true });
  return target;
}

// ── Uninstall ──────────────────────────────────────────────────────────────

function uninstall() {
  console.log("");
  console.log(bold("  ComfyUI Text2Img — Uninstaller"));
  console.log("");

  const skillPath = join(homedir(), ".openclaw", "workspace", "skills", SKILL_NAME);
  const configPath = join(homedir(), ".openclaw", "openclaw.json");

  // Remove skill files
  if (existsSync(skillPath)) {
    rmSync(skillPath, { recursive: true, force: true });
    console.log(`  Removed skill files: ${dim(skillPath)}`);
  } else {
    console.log(dim("  Skill files not found (already removed)."));
  }

  // Remove config entry
  if (existsSync(configPath)) {
    try {
      const config = JSON.parse(readFileSync(configPath, "utf8"));
      if (config.skills?.entries?.[SKILL_NAME]) {
        delete config.skills.entries[SKILL_NAME];
        writeFileSync(configPath, JSON.stringify(config, null, 2) + "\n");
        console.log(`  Removed config entry: ${dim(configPath)}`);
      } else {
        console.log(dim("  Config entry not found (already removed)."));
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
  console.log(bold("  ComfyUI Text2Img — OpenClaw Skill Installer"));
  console.log(dim("  Generate images from text using Stable Diffusion"));
  console.log("");

  const rl = createInterface({ input: process.stdin, output: process.stdout });

  try {
    // 1. Server URL
    const comfyUrl = await ask(rl, "  ComfyUI server URL", DEFAULT_URL);

    // 2. Username
    const username = await ask(rl, "  Username");
    if (!username) {
      console.log(red("\n  Error: Username is required."));
      process.exit(1);
    }

    // Close readline so we can handle raw stdin for password
    rl.close();

    // 3. Password (hidden input)
    const password = await askHidden(null, "  Password");
    if (!password) {
      console.log(red("\n  Error: Password is required."));
      process.exit(1);
    }

    // 4. Encode
    const authHeader = `Basic ${Buffer.from(`${username}:${password}`).toString("base64")}`;

    // 5. Test connection
    console.log("");
    process.stdout.write(`  Testing connection to ${dim(comfyUrl)}... `);
    const status = testConnection(comfyUrl, authHeader);

    if (status === 200) {
      console.log(green("connected!"));
    } else if (status === 401) {
      console.log(red("auth failed."));
      console.log(red("  Check your username and password."));
      process.exit(1);
    } else if (status === 0) {
      console.log(yellow("unreachable."));
      console.log(yellow("  Saving config anyway — verify the URL is correct."));
    } else {
      console.log(yellow(`HTTP ${status}.`));
      console.log(yellow("  Saving config anyway."));
    }

    // 6. Install skill files
    process.stdout.write(`  Installing skill files... `);
    const skillPath = installSkillFiles();
    console.log(green("done."));

    // 7. Update config
    process.stdout.write(`  Updating openclaw.json... `);
    const configPath = updateOpenclawConfig(comfyUrl, authHeader);
    console.log(green("done."));

    // 8. Done
    console.log("");
    console.log(green(bold("  ✓ Installed successfully!")));
    console.log("");
    console.log(`  Skill:  ${dim(skillPath)}`);
    console.log(`  Config: ${dim(configPath)}`);
    console.log("");
    console.log(`  Next: ${bold("openclaw gateway restart")} or ${bold("/new")} in chat`);
    console.log(`  Then ask your bot: ${dim('"Generate an image of a sunset over mountains"')}`);
    console.log("");
  } catch (err) {
    console.error(red(`\n  Error: ${err.message}`));
    process.exit(1);
  }
}

main();
