// Build wrapper that avoids copying the dataset resources into the static
// export. `next build` with `output: "export"` copies everything in
// `public/` to `out/`, following symlinks — when `public/resources` is a
// symlink to a large dataset folder (hundreds of GB) that makes the build
// take forever and blow up the output size.
//
// Instead of copying the datasets, we:
//   1. temporarily move `public/resources` out of `public/` so Next skips
//      it (Next copies dotfiles too, so it must leave the public dir);
//   2. run `next build`;
//   3. recreate `out/resources` as a symlink to the same target.
// The datasets are static files fetched at runtime, so a symlink works
// just as well as a copy.

import { execFileSync } from "node:child_process";
import { lstatSync, mkdtempSync, readlinkSync, renameSync, rmSync, symlinkSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const appDir = dirname(dirname(fileURLToPath(import.meta.url)));
const publicResources = join(appDir, "public", "resources");
const outResources = join(appDir, "out", "resources");
const nextBin = join(appDir, "node_modules", ".bin", "next");

function isSymlink(path) {
  try {
    return lstatSync(path).isSymbolicLink();
  } catch {
    return false;
  }
}

async function run() {
  let stash = null;
  let target = null;

  if (isSymlink(publicResources)) {
    target = readlinkSync(publicResources);

    // Move the symlink outside `public/` (and outside `out/`) so Next
    // never touches it. A per-run temp dir keeps interrupted builds safe.
    stash = mkdtempSync(join(tmpdir(), "octobeat-resources-"));
    renameSync(publicResources, join(stash, "resources"));
    console.log(`Hid ${publicResources} (symlink → ${target})`);
  }

  try {
    execFileSync(nextBin, ["build"], {
      cwd: appDir,
      stdio: "inherit",
    });
  } finally {
    if (target) {
      // Next may have copied a stale `out/resources` from a previous run.
      rmSync(outResources, { recursive: true, force: true });

      symlinkSync(target, outResources);
      console.log(`Linked ${outResources} → ${target}`);

      // Restore the original public symlink for the dev server.
      renameSync(join(stash, "resources"), publicResources);
      rmSync(stash, { recursive: true, force: true });
    }
  }
}

run().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
