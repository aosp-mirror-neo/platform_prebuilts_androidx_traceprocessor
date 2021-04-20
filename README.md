# Trace Processor Shell

The source code for `trace_processor_shell` lives in `external/perfetto` in the AOSP source tree.

## Building stripped binaries

Check out the detailed build instructions [here](https://perfetto.dev/docs/contributing/build-instructions).

```bash
tools/gn args out/<out_folder>

# Use the following config
target_os = "android"
target_cpu = "arm" / "arm64" / "x64" # Depending on the platform
is_debug = false
monolithic_binaries = true

# Finally build the binaries
tools/ninja -C out/<out_folder>

# Strip Binaries
# You should have downloaded the NDK
# ndk_versio = 22.1.7171670
/path/to/sdk/ndk/<ndk_version>/toolchains/llvm/prebuilt/<platform/paths>/bin/strip <binary_name>
```
