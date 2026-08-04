# Perfetto Binaries

The source code for several perfetto binaries lives in the `external/perfetto`
project in the AOSP source tree. These binaries enable unbundled on-device perfetto
tracing, and on-device trace processing.

To download prebuilt, stripped binaries and proto files directly from the official Perfetto releases on GitHub:

```bash
./download_perfetto_binaries.py [--version <version>]
```

By default, the script queries the GitHub API to fetch and download the latest release. Alternatively, you can specify a specific version tag:

```bash
./download_perfetto_binaries.py --version v56.0
```

This script:
 - Downloads matching tracebox and trace_processor_shell binaries for all supported Android architectures (arm, arm64, x86, x64) from GitHub releases.
 - Downloads the corresponding version of proto files from GitHub raw contents.
 - Ensures permissions are correctly set to executable for the binaries.

