#!/usr/bin/env python3
# Copyright (C) 2026 The Android Open Source Project
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

import argparse
import json
import os
import shutil
import sys
import urllib.request
import urllib.error
import zipfile

# List of each arch, with a tuple of:
# - perfetto-name (arg in perfetto build / download zip name)
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
    'protos/perfetto/common/descriptor.proto',
    'protos/perfetto/metrics/perfetto_merged_metrics.proto',
    'protos/perfetto/perfetto_sql/structured_query.proto',
    'protos/perfetto/trace_processor/metatrace_categories.proto',
    'protos/perfetto/trace_processor/trace_processor.proto',
    'protos/perfetto/trace_summary/file.proto',
    'protos/perfetto/trace_summary/v2_metric.proto',
)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_latest_release_version():
    url = "https://api.github.com/repos/google/perfetto/releases/latest"
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data["tag_name"]
    except Exception as e:
        raise RuntimeError(
            f"Failed to fetch latest release version from GitHub: {e}.\n"
            f"Please specify a version explicitly using --version."
        )


def download_file(url, output_path):
    print(f"Downloading {url} -> {output_path}...")
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    try:
        with urllib.request.urlopen(req) as response, open(output_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
    except urllib.error.URLError as e:
        raise RuntimeError(f"Failed to download {url}: {e}")


def download_and_extract_binaries(version, arch, arch_tag, root_dir):
    zip_url = f"https://github.com/google/perfetto/releases/download/{version}/android-{arch}.zip"
    temp_zip_path = os.path.join(root_dir, f"temp_{arch}.zip")
    try:
        download_file(zip_url, temp_zip_path)
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
            for binary in ['tracebox', 'trace_processor_shell']:
                # The path inside zip is e.g. "android-arm64/tracebox"
                zip_member_path = f"android-{arch}/{binary}"
                out_dir = os.path.join(root_dir, binary)
                os.makedirs(out_dir, exist_ok=True)

                # Output filename is e.g. "tracebox/tracebox_aarch64"
                out_file_path = os.path.join(out_dir, f"{binary}_{arch_tag}")

                # Extract the binary file content
                print(f"Extracting {zip_member_path} from zip to {out_file_path}...")
                with zip_ref.open(zip_member_path) as member_file, open(out_file_path, 'wb') as target_file:
                    shutil.copyfileobj(member_file, target_file)
    finally:
        if os.path.exists(temp_zip_path):
            os.remove(temp_zip_path)


def download_protos(version, root_dir):
    print("Downloading proto files...")
    protos_dir = os.path.join(root_dir, 'protos')
    if os.path.exists(protos_dir):
        print(f"Removing old protos directory: {protos_dir}")
        shutil.rmtree(protos_dir)

    for proto_path in PROTO_LIST:
        url = f"https://raw.githubusercontent.com/google/perfetto/{version}/{proto_path}"
        dst_path = os.path.join(root_dir, proto_path)
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        download_file(url, dst_path)


def main():
    parser = argparse.ArgumentParser(
        description="Download Perfetto tracebox and trace_processor_shell binaries, and proto files."
    )
    parser.add_argument(
        '--version', '-v',
        help="Perfetto release tag to download (e.g. 'v56.0'). Defaults to fetching the latest release."
    )
    args = parser.parse_args()

    version = args.version
    if not version:
        print("No version specified. Fetching latest release version from GitHub...")
        version = get_latest_release_version()
    print(f"Using Perfetto version: {version}")

    # Download binaries for each architecture
    for arch, arch_tag in ARCH_LIST:
        print(f"\nProcessing binaries for architecture: {arch} ({arch_tag})")
        download_and_extract_binaries(version, arch, arch_tag, ROOT_DIR)

    # Download proto files
    print("\nProcessing proto files")
    download_protos(version, ROOT_DIR)

    print("\nSuccessfully updated Perfetto prebuilt binaries and proto files!")


if __name__ == '__main__':
    sys.exit(main())
