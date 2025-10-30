import { spawn } from 'child_process';
import { existsSync, mkdirSync, copyFileSync, writeFileSync } from 'fs';
import { join } from 'path';

/**
 * Simple runner to execute Foundry tests for LLM-generated code.
 *
 * Usage examples:
 *   - tsx scripts/runFoundryTests.ts --project ./foundry
 *   - tsx scripts/runFoundryTests.ts --project ./foundry --code-file ./generated/Generated.t.sol
 *
 * Requirements:
 *   - Foundry installed (`forge` in PATH). See: https://book.getfoundry.sh/getting-started/installation
 *   - Project structure at `--project` with `foundry.toml`, `src/`, and `test/` folders
 *     If missing, this script will scaffold a minimal structure.
 */

type CLIOptions = {
  project: string;
  codeFile?: string;
  verbose: boolean;
};

function parseArgs(argv: string[]): CLIOptions {
  const opts: CLIOptions = { project: './foundry', verbose: false };
  for (let i = 2; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === '--project' && argv[i + 1]) {
      opts.project = argv[++i];
    } else if (arg === '--code-file' && argv[i + 1]) {
      opts.codeFile = argv[++i];
    } else if (arg === '--verbose') {
      opts.verbose = true;
    }
  }
  return opts;
}

function ensureFoundryProjectStructure(project: string) {
  const srcDir = join(project, 'src');
  const testDir = join(project, 'test');
  if (!existsSync(project)) mkdirSync(project, { recursive: true });
  if (!existsSync(srcDir)) mkdirSync(srcDir, { recursive: true });
  if (!existsSync(testDir)) mkdirSync(testDir, { recursive: true });
  const foundryToml = join(project, 'foundry.toml');
  if (!existsSync(foundryToml)) {
    writeFileSync(
      foundryToml,
      `[profile.default]\nsrc = "src"\nout = "out"\ntest = "test"\nlibs = ["lib"]\n`,
      'utf-8'
    );
  }
}

function checkForgeInstalled(): Promise<void> {
  return new Promise((resolve, reject) => {
    const child = spawn('forge', ['--version'], { shell: true });
    let stderr = '';
    child.stderr.on('data', (d) => (stderr += d.toString()));
    child.on('close', (code) => {
      if (code === 0) return resolve();
      reject(new Error(`forge not found or failed to run. stderr: ${stderr}`));
    });
  });
}

async function runFoundryTests(opts: CLIOptions) {
  ensureFoundryProjectStructure(opts.project);

  // If a code file is provided, copy it to test/Generated.t.sol
  if (opts.codeFile) {
    const target = join(opts.project, 'test', 'Generated.t.sol');
    try {
      copyFileSync(opts.codeFile, target);
      console.log(`Copied test file to ${target}`);
    } catch (err) {
      console.error(`Failed to copy code-file: ${(err as Error).message}`);
      process.exit(1);
    }
  }

  await checkForgeInstalled().catch((err) => {
    console.error('Foundry (forge) is required. Install from https://book.getfoundry.sh/getting-started/installation');
    console.error(err.message);
    process.exit(1);
  });

  console.log(`Running forge tests in project: ${opts.project}`);
  const args = ['test', '-C', opts.project];
  if (opts.verbose) args.push('-vvv');
  const child = spawn('forge', args, { shell: true });
  child.stdout.on('data', (d) => process.stdout.write(d));
  child.stderr.on('data', (d) => process.stderr.write(d));
  child.on('close', (code) => {
    if (code === 0) {
      console.log('Forge tests completed successfully');
      process.exit(0);
    } else {
      console.error(`Forge tests failed with exit code ${code}`);
      process.exit(code || 1);
    }
  });
}

// Entry point
(async () => {
  const opts = parseArgs(process.argv);
  await runFoundryTests(opts);
})();