# Vendored Lizard Provenance

- Upstream: https://github.com/terryyin/lizard
- Version: `1.24.0`
- Source revision: `308b1c3efd8c1c69bcc3eb82deeaec64fd3662ec`
- Vendored: `2026-10-01`
- Runtime: Python 3.8 or later
- Purpose: CodePulse runs `lizard.py` as a local subprocess for multi-language Cyclomatic Complexity measurement. It does not install or import a system `lizard` package.

This directory contains the upstream runtime files required by `lizard.py`: `lizard_ext/` and `lizard_languages/`. Do not remove either package or replace this bundle with only `lizard.py`.

`LICENSE.txt` is copied from the upstream release and must remain with the source. Preserve copyright and license notices in the vendored source files. The upstream release-level license is MIT; `lizard.py` also carries an Apache-2.0 header. Retain both notices when updating the bundle.

## Update Procedure

1. Download a tagged upstream release, never the moving `master` branch.
2. Replace `lizard.py`, `lizard_ext/`, `lizard_languages/`, and `LICENSE.txt` as one unit.
3. Update the version and source revision above.
4. Run `python lizard.py --version` and the CodePulse validator before committing.

`pathspec` is optional upstream functionality and is not vendored. When it is unavailable, Lizard cannot fully interpret `.gitignore`; CodePulse must record that coverage limitation when it affects the analyzed scope.