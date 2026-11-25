<!-- SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0 -->
# Dependency licences

Status: M6, 2026-11-25. Generated from the installed environment of this session: Python packages from the `.venv` created by `uv sync --frozen --all-groups --all-extras` (`*.dist-info/METADATA`: `License-Expression`, otherwise the licence classifiers), npm packages from `demo/node_modules/*/package.json` after `npm ci --prefer-offline`, and, for platform-specific optional binaries that npm did not install on this machine, the `license` field of `demo/package-lock.json`. Licence fields were read as declared by each package; their full licence texts were not reviewed.

## Summary

- Python: 14 distributions (7 runtime, the rest test-only). npm: 84 lockfile packages (3 runtime: react, react-dom, scheduler; the rest build or test tools, of which 31 are platform-specific binaries not installed here).
- Every declared licence is one of MIT, BSD-2-Clause, BSD-3-Clause, 0BSD, ISC, Apache-2.0, PSF-2.0, MPL-2.0, or a combination of these with Zlib and CC0-1.0 (numpy's compound expression). **No dependency is flagged**: none is copyleft beyond the file-level MPL-2.0, none is unknown, and none is non-commercial.
- MPL-2.0 (file-level copyleft) applies to `hypothesis` (test-only) and to `lightningcss` and its platform binaries (build-only, used by Vite for CSS). Neither is shipped in the demo bundle or imported by the study code, and neither is redistributed by this repository (`.venv/` and `node_modules/` are git-ignored). This is a reading of the declared licence, not legal advice.
- numpy declares `BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0`, which covers bundled components; all are permissive.
- The demo's own `package.json` declares `SEE LICENSE IN ../LICENSE` (the project's custom licence).

## Full list

| Ecosystem | Package | Version | Declared licence | Role |
|---|---|---|---|---|
| Python | attrs | 26.1.0 | MIT | runtime |
| Python | jsonschema | 4.26.0 | MIT | runtime |
| Python | jsonschema-specifications | 2025.9.1 | MIT | runtime |
| Python | numpy | 2.5.4 | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 | runtime |
| Python | referencing | 0.37.0 | MIT | runtime |
| Python | rpds-py | 2026.9.1 | MIT | runtime |
| Python | typing_extensions | 4.16.0 | PSF-2.0 | runtime |
| Python | hypothesis | 6.170.15 | MPL-2.0 | test (dev group) |
| Python | iniconfig | 2.3.1 | MIT | test (dev group) |
| Python | packaging | 26.3 | Apache-2.0 OR BSD-2-Clause | test (dev group) |
| Python | pluggy | 1.7.0 | MIT License | test (dev group) |
| Python | Pygments | 2.21.0 | BSD-2-Clause | test (dev group) |
| Python | pytest | 9.2.0 | MIT | test (dev group) |
| Python | sortedcontainers | 2.4.0 | Apache Software License | test (dev group) |
| npm | @rolldown/binding-darwin-arm64 | 1.2.19 | MIT | build (optional) |
| npm | fsevents | 2.3.3 | MIT | build (optional) |
| npm | lightningcss-darwin-arm64 | 1.33.0 | MPL-2.0 | build (optional) |
| npm | @emnapi/core | 2.0.0-beta.2 | MIT | build (platform-specific optional binary; licence from package-lock.json) |
| npm | @emnapi/runtime | 2.0.0-beta.2 | MIT | build (platform-specific optional binary; licence from package-lock.json) |
| npm | @emnapi/wasi-threads | 2.2.0 | MIT | build (platform-specific optional binary; licence from package-lock.json) |
| npm | @napi-rs/wasm-runtime | 1.2.6 | MIT | build (platform-specific optional binary; licence from package-lock.json) |
| npm | @rolldown/binding-android-arm-eabi | 1.2.19 | MIT | build (platform-specific optional binary; licence from package-lock.json) |
| npm | @rolldown/binding-android-arm64 | 1.2.19 | MIT | build (platform-specific optional binary; licence from package-lock.json) |
| npm | @rolldown/binding-darwin-x64 | 1.2.19 | MIT | build (platform-specific optional binary; licence from package-lock.json) |
| npm | @rolldown/binding-freebsd-x64 | 1.2.19 | MIT | build (platform-specific optional binary; licence from package-lock.json) |
| npm | @rolldown/binding-linux-arm-gnueabihf | 1.2.19 | MIT | build (platform-specific optional binary; licence from package-lock.json) |
| npm | @rolldown/binding-linux-arm64-gnu | 1.2.19 | MIT | build (platform-specific optional binary; licence from package-lock.json) |
| npm | @rolldown/binding-linux-arm64-musl | 1.2.19 | MIT | build (platform-specific optional binary; licence from package-lock.json) |
| npm | @rolldown/binding-linux-ppc64-gnu | 1.2.19 | MIT | build (platform-specific optional binary; licence from package-lock.json) |
| npm | @rolldown/binding-linux-s390x-gnu | 1.2.19 | MIT | build (platform-specific optional binary; licence from package-lock.json) |
| npm | @rolldown/binding-linux-x64-gnu | 1.2.19 | MIT | build (platform-specific optional binary; licence from package-lock.json) |
| npm | @rolldown/binding-linux-x64-musl | 1.2.19 | MIT | build (platform-specific optional binary; licence from package-lock.json) |
| npm | @rolldown/binding-openharmony-arm64 | 1.2.19 | MIT | build (platform-specific optional binary; licence from package-lock.json) |
| npm | @rolldown/binding-wasm32-wasi | 1.2.19 | MIT | build (platform-specific optional binary; licence from package-lock.json) |
| npm | @rolldown/binding-win32-arm64-msvc | 1.2.19 | MIT | build (platform-specific optional binary; licence from package-lock.json) |
| npm | @rolldown/binding-win32-x64-msvc | 1.2.19 | MIT | build (platform-specific optional binary; licence from package-lock.json) |
| npm | @tybys/wasm-util | 0.10.5 | MIT | build (platform-specific optional binary; licence from package-lock.json) |
| npm | lightningcss-android-arm64 | 1.33.0 | MPL-2.0 | build (platform-specific optional binary; licence from package-lock.json) |
| npm | lightningcss-darwin-x64 | 1.33.0 | MPL-2.0 | build (platform-specific optional binary; licence from package-lock.json) |
| npm | lightningcss-freebsd-x64 | 1.33.0 | MPL-2.0 | build (platform-specific optional binary; licence from package-lock.json) |
| npm | lightningcss-linux-arm-gnueabihf | 1.33.0 | MPL-2.0 | build (platform-specific optional binary; licence from package-lock.json) |
| npm | lightningcss-linux-arm64-gnu | 1.33.0 | MPL-2.0 | build (platform-specific optional binary; licence from package-lock.json) |
| npm | lightningcss-linux-arm64-musl | 1.33.0 | MPL-2.0 | build (platform-specific optional binary; licence from package-lock.json) |
| npm | lightningcss-linux-x64-gnu | 1.33.0 | MPL-2.0 | build (platform-specific optional binary; licence from package-lock.json) |
| npm | lightningcss-linux-x64-musl | 1.33.0 | MPL-2.0 | build (platform-specific optional binary; licence from package-lock.json) |
| npm | lightningcss-win32-arm64-msvc | 1.33.0 | MPL-2.0 | build (platform-specific optional binary; licence from package-lock.json) |
| npm | lightningcss-win32-x64-msvc | 1.33.0 | MPL-2.0 | build (platform-specific optional binary; licence from package-lock.json) |
| npm | tslib | 2.9.1 | 0BSD | build (platform-specific optional binary; licence from package-lock.json) |
| npm | @jridgewell/sourcemap-codec | 1.6.0 | MIT | build and test |
| npm | @oxc-project/types | 0.156.0 | MIT | build and test |
| npm | @rolldown/pluginutils | 1.1.1 | MIT | build and test |
| npm | @standard-schema/spec | 1.1.0 | MIT | build and test |
| npm | @types/chai | 5.2.3 | MIT | build and test |
| npm | @types/deep-eql | 4.0.2 | MIT | build and test |
| npm | @types/estree | 1.0.11 | MIT | build and test |
| npm | @types/react | 19.3.0 | MIT | build and test |
| npm | @types/react-dom | 19.3.0 | MIT | build and test |
| npm | @vitejs/plugin-react | 6.1.2 | MIT | build and test |
| npm | @vitest/expect | 4.1.12 | MIT | build and test |
| npm | @vitest/mocker | 4.1.12 | MIT | build and test |
| npm | @vitest/pretty-format | 4.1.12 | MIT | build and test |
| npm | @vitest/runner | 4.1.12 | MIT | build and test |
| npm | @vitest/snapshot | 4.1.12 | MIT | build and test |
| npm | @vitest/spy | 4.1.12 | MIT | build and test |
| npm | @vitest/utils | 4.1.12 | MIT | build and test |
| npm | assertion-error | 2.0.1 | MIT | build and test |
| npm | chai | 6.3.0 | MIT | build and test |
| npm | convert-source-map | 2.0.0 | MIT | build and test |
| npm | csstype | 3.2.4 | MIT | build and test |
| npm | detect-libc | 2.1.2 | Apache-2.0 | build and test |
| npm | es-module-lexer | 2.3.2 | MIT | build and test |
| npm | estree-walker | 3.0.3 | MIT | build and test |
| npm | expect-type | 1.4.0 | Apache-2.0 | build and test |
| npm | fdir | 6.5.0 | MIT | build and test |
| npm | lightningcss | 1.33.0 | MPL-2.0 | build and test |
| npm | magic-string | 0.30.21 | MIT | build and test |
| npm | nanoid | 3.3.20 | MIT | build and test |
| npm | obug | 2.2.1 | MIT | build and test |
| npm | pathe | 2.0.3 | MIT | build and test |
| npm | picocolors | 1.1.1 | ISC | build and test |
| npm | picomatch | 4.0.7 | MIT | build and test |
| npm | postcss | 8.5.33 | MIT | build and test |
| npm | rolldown | 1.2.19 | MIT | build and test |
| npm | siginfo | 2.0.0 | ISC | build and test |
| npm | source-map-js | 1.2.4 | BSD-3-Clause | build and test |
| npm | stackback | 0.0.2 | MIT | build and test |
| npm | std-env | 4.3.0 | MIT | build and test |
| npm | tinybench | 2.9.0 | MIT | build and test |
| npm | tinyexec | 1.4.0 | MIT | build and test |
| npm | tinyglobby | 0.2.17 | MIT | build and test |
| npm | tinyrainbow | 3.2.0 | MIT | build and test |
| npm | typescript | 5.9.3 | Apache-2.0 | build and test |
| npm | vite | 8.3.5 | MIT | build and test |
| npm | vitest | 4.1.12 | MIT | build and test |
| npm | why-is-node-running | 2.3.0 | MIT | build and test |
| npm | react | 19.3.1 | MIT | runtime (shipped in the demo bundle) |
| npm | react-dom | 19.3.1 | MIT | runtime (shipped in the demo bundle) |
| npm | scheduler | 0.28.0 | MIT | runtime (shipped in the demo bundle) |
