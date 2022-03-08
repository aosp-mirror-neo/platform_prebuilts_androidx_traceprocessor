# Trace Processor Shell

The source code for `trace_processor_shell` lives in `external/perfetto` in the AOSP source tree.

## Building stripped binaries

Checkout the [AOSP](https://g3doc.corp.google.com/company/teams/android/developing/index.md?cl=head) source tree.

```bash
cd <root of AOSP checkout>
source build/envsetup.sh
# Pick lunch targets
# AARCH64
lunch flame-userdebug
# ARM32
tapas

# Finally build the binaries
mmma external/perfetto

# Copy Outputs to prebuilts
# aarch64, arm32 are the suffixes being used.
# <xxx> = generic for aosp_arm

cp <aosp_root>/out/target/product/<xxx>/system/bin/trace_processor_shell <androidx-root>/prebuilts/androidx/traceprocessor/trace_processor_shell/trace_processor_shell_<suffix>
```
