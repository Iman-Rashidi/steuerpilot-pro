# Third-party notices

## paprun

SteuerPilot Pro uses the `paprun` BMF payroll program-flow interpreter as a pinned Rust dependency in its browser-side WebAssembly tax adapter. The interpreter is distributed under the MIT License. Its source is pinned to commit `cdf564daec7f617d54181eb8b14232e48a59dd7a` in `wasm/Cargo.toml`.

MIT License

Copyright (c) 2026 Manuel Busch

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


## BMF Lohnsteuer PAP 2026

The unmodified `data/bmf/Lohnsteuer2026.xml` is the BMF's published 2026 payroll tax program-flow XML. The BMF data portal entry was updated/published on 12 November 2025 and lists the dataset under CC BY-ND 4.0. See `data/bmf/README.md` for attribution and source URLs. The XML itself retains its embedded technical stand date of 23 October 2025; this provenance detail is deliberately not concealed.
