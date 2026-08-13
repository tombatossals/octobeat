// Build wrapper that avoids copying the dataset resources into the static
// export. `next build` with `output: "export"` copies everything in
// `public/` to `out/`, following symlinks — when `public/resources` is a
// symlink to a large dataset folder (hundreds of GB) that makes the build
// take forever and blow up the output size.
//
// Instead of copying the datasets, we:
//   1. temporarily remove `public/resources` (it is a symlink, so we just
//      remember its target and recreate it later);
//   2. run `next build`;
//   3. recreate `out/resources` as a symlink to the same target.
// The datasets are static files fetched at runtime, so a symlink works
// just as well as a copy.

import { execFileSync } from "node:child_process";
import { lstatSync, readlinkSync, rmSync, symlinkSync, unlinkSync } from "node:fs";
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
  let target = null;

  if (isSymlink(publicResources)) {
    target = readlinkSync(publicResources);

    // Next copies dotfiles too, so the symlink must leave the public dir
    // entirely. Removing it is safe: we recreate it with the same target
    // right after the build.
    unlinkSync(publicResources);
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
      symlinkSync(target, publicResources);
    }
  }
}

run().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
