#!/usr/bin/env python3
# Copyright (C) 2017 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import os
import platform
import subprocess
import sys

from shlex import quote
from shutil import copyfile

# NOTE - this script is adapted from (now deleted)
# perfetto_repo/tools/build_all_configs.py If this stops working, try
# perfetto_repo/tools/install-build-deps, and check build instructions
# at See build docs at
# https://perfetto.dev/docs/contributing/build-instructions
ANDROID_ARGS = (
    'target_os="android"',
    'monolithic_binaries=true',
    'is_debug=false'
)

ANDROID_BUILD_TARGETS = (
    'trace_processor_shell',
    'tracebox',
)

# List of each arch, with a tuple of:
# - perfetto-name (arg in perfetto build)
# - android-tag (used in final output path, used for binary disambig at apk build time)
ARCH_LIST = (
    ('arm', 'arm'),
    ('arm64', 'aarch64'),
    ('x64', 'x86_64'),
    ('x86', 'x86'),
)

# List of each proto to copy / check in. As imports in the top level
# protos are changed, this list will need to be updated.
PROTO_LIST = (
    'protos/perfetto/trace_processor/trace_processor.proto',
    'protos/perfetto/common/descriptor.proto',
    'protos/perfetto/metrics/perfetto_merged_metrics.proto',
    'protos/perfetto/trace_processor/metatrace_categories.proto',
)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--perfetto_checkout_path', help='Path to perfetto checkout', default = 'perfetto_repo')
  args = parser.parse_args()

  perfetto_dir = os.path.abspath(args.perfetto_checkout_path)

  out_base_dir = os.path.join(perfetto_dir, 'out')
  if not os.path.isdir(out_base_dir):
    os.mkdir(out_base_dir)

  gn = os.path.join(perfetto_dir, 'tools', 'gn')

  ### Protos
  print('\n\033[32mCopying Protos\033[0m')
  # use root as proto dir, as all protos have 'protos' prefix, so will be in protos dir
  out_proto_dir = ROOT_DIR
  # cleanup old protos
  subprocess.check_call(['rm', '-rf', 'protos'], cwd=ROOT_DIR)
  for src_path in PROTO_LIST:
    print(src_path)
    split_path_in_repo = src_path.split('/')
    src = os.path.join(perfetto_dir, *split_path_in_repo)
    dst = os.path.join(out_proto_dir, *split_path_in_repo)

    # Preserve tree when copying to support import paths
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    copyfile(src, dst)

  ### Binaries
  for arch, arch_tag in ARCH_LIST:
    config_name ='android_%s' % (arch)
    gn_args = ANDROID_ARGS + ('target_cpu="%s"' % arch,)

    print('\n\033[32mConfiguring %-20s[%s]\033[0m' % (config_name, ','.join(gn_args)))
    out_dir = os.path.join(perfetto_dir, 'out', config_name)
    if not os.path.isdir(out_dir):
      os.mkdir(out_dir)
    gn_cmd = (gn, 'gen', out_dir, '--args=%s' % (' '.join(gn_args)), '--check')
    print(' '.join(quote(c) for c in gn_cmd))
    subprocess.check_call(gn_cmd, cwd=perfetto_dir)

    print('\n\033[32mBuilding %-20s[%s]\033[0m' % (config_name, ','.join(ANDROID_BUILD_TARGETS)))
    ninja = os.path.join(perfetto_dir, 'tools', 'ninja')
    ninja_cmd = (ninja, '-C', '.') + ANDROID_BUILD_TARGETS
    subprocess.check_call(ninja_cmd, cwd=out_dir)

    print('\n\033[32mCopying + Stripping %s binaries\033[0m' % (config_name))
    for target in ANDROID_BUILD_TARGETS:
      out_file = os.path.join(ROOT_DIR, target, target + "_" + arch_tag)

      # copy out of perfetto out dir
      copyfile(os.path.join(out_dir, target), out_file)

      # Note that this does not support other OS types beside macos and linux
      system = platform.system().lower()
      if system == "darwin":
        platform_folder = "darwin-x86_64"
      else:
        platform_folder = "linux-x86_64"

      # strip it using ndk from perfetto checkout
      strip_path = os.path.join(
          perfetto_dir,
          "buildtools",
          "ndk",
          "toolchains",
          "llvm",
          "prebuilt",
          platform_folder,
          "bin",
          "llvm-strip")
      subprocess.check_call((strip_path, out_file))

if __name__ == '__main__':
  sys.exit(main())
