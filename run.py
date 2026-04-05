#!/usr/bin/env python3
"""
Benchmark System for Python Frameworks with Docker Cache

Execution modes:
  ./run.py                        # Full benchmark across all versions
  ./run.py --validate-only        # Build + quick validation only
  ./run.py --use-good-versions    # Benchmark only on validated versions
  ./run.py --force-rebuild        # Force rebuild even if image exists

Flags:
  --validate-only, --build-only   Build images and validate with a quick test
  --use-good-versions             Use versions from good_versions.json
  --force-rebuild                 Rebuild all images
  --help, -h                      Show this help message

Recommended workflow:
  1. ./run.py --validate-only          # Validate all versions (fast)
  2. ./run.py --use-good-versions      # Full benchmark on validated versions only
"""
import subprocess
import shutil
import re
import json
import sys
import time
import requests
from pathlib import Path
from util.python_lib_info import get_versions

# Show help if requested
if "--help" in sys.argv or "-h" in sys.argv:
    print(__doc__)
    sys.exit(0)
import sys

# Dictionary: framework -> list of desired versions

# BANNED = ["blacksheep", "quart", "sanic", "emmett"]
FRAMEWORKS_NAMES = [
    "aiohttp",
    "blacksheep",
    "quart",
    "sanic",
    "emmett",
    "baize",
    "muffin",
    "starlette",
    "django",
    "falcon",
    "tornado",
    "fastapi",
]
# FRAMEWORKS_NAMES = ['fastapi']
FRAMEWORKS = {}

# Execution options
FORCE_REBUILD = "--force-rebuild" in sys.argv
VALIDATE_ONLY = "--validate-only" in sys.argv or "--build-only" in sys.argv
USE_GOOD_VERSIONS = "--use-good-versions" in sys.argv

NETWORK = "data"
ROOT_DIR = Path(__file__).parent.resolve()
BASE_FRAMEWORKS_DIR = ROOT_DIR / "frameworks"
RESULTS_DIR = ROOT_DIR / "results"


def parse_rounds() -> int:
    if "--rounds" in sys.argv:
        idx = sys.argv.index("--rounds")
        try:
            value = int(sys.argv[idx + 1])
            if value < 1:
                raise ValueError
            return value
        except (IndexError, ValueError):
            print("❌ --rounds requires a positive integer. Ex: --rounds 5")
            sys.exit(1)
    return 1


ROUNDS = parse_rounds()


def run(cmd, **kwargs):
    print(f"» Running: {cmd}")
    subprocess.run(cmd, shell=True, check=True, **kwargs)


def run_output(cmd, **kwargs):
    """Runs a command and returns its output"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, **kwargs)
    return result.returncode == 0, result.stdout.strip()


def ensure_docker_network(network_name):
    try:
        subprocess.run(
            ["docker", "network", "inspect", network_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        print(f"Docker network '{network_name}' already exists.")
    except subprocess.CalledProcessError:
        print(f"Creating Docker network '{network_name}'...")
        run(f"docker network create {network_name}")


def image_exists(image_name):
    """Checks whether a Docker image exists locally"""
    success, _ = run_output(f"docker image inspect {image_name}")
    return success


def get_next_execution_number() -> int:
    """Detects the last execution number and returns the next one."""
    existing = [
        d
        for d in ROOT_DIR.iterdir()
        if d.is_dir() and re.match(r"^results_exc_(\d+)$", d.name)
    ]
    if not existing:
        return 1
    last = max(int(re.search(r"(\d+)$", d.name).group(1)) for d in existing)
    return last + 1


def validate_framework(framework_name, version):
    """Validates whether the framework responds correctly to a quick request"""
    versioned_name = f"{framework_name}_{version.replace('.', '_')}"
    container_name = f"validate_{versioned_name}"

    print(f"  🧪 Validating {framework_name} v{version}...")

    try:
        # Remove old container if it exists
        run_output(f"docker rm -f {container_name}")

        # Start container
        run(
            f"docker run -d -p 8080:8080 --name {container_name} {framework_name}_app:{version}",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Wait for initialization
        max_attempts = 10
        for attempt in range(max_attempts):
            time.sleep(1)
            try:
                response = requests.get("http://localhost:8080/html", timeout=2)
                if response.status_code == 200:
                    print(f"  ✅ {framework_name} v{version} validated successfully!")
                    run_output(f"docker stop -t 2 {container_name}")
                    run_output(f"docker rm {container_name}")
                    return True
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                continue

        print(f"  ❌ {framework_name} v{version} did not respond within {max_attempts}s")
        run_output(f"docker stop -t 2 {container_name}")
        run_output(f"docker rm {container_name}")
        return False

    except Exception as e:
        print(f"  ❌ Error validating {framework_name} v{version}: {e}")
        run_output(f"docker stop -t 2 {container_name}")
        run_output(f"docker rm {container_name}")
        return False


def prepare_versioned_framework(base_name, version):
    """Modifies requirements.txt to use the specified version"""
    path_dir = BASE_FRAMEWORKS_DIR / base_name
    req_file = path_dir / "requirements.txt"

    lines = req_file.read_text().splitlines()
    base_pattern = re.compile(rf"^\s*{re.escape(base_name)}\s*==")
    new_lines = [line for line in lines if not base_pattern.match(line)]
    new_lines.append(f"{base_name}=={version}")
    req_file.write_text("\n".join(new_lines) + "\n")


def run_benchmark(framework_name, version, validate_only=False, exc_dir: Path = None):
    versioned_name = f"{framework_name}_{version.replace('.', '_')}"
    image_name = f"{framework_name}_app:{version}"

    print("=" * 60)
    print(
        f"🚀 {'Validating' if validate_only else 'Benchmark'}: {framework_name} v{version}"
    )
    print(f"🐳 Image: {image_name}")
    print("=" * 60)

    # Check if the image already exists
    if image_exists(image_name) and not FORCE_REBUILD:
        print(f"✅ Image {image_name} already exists, skipping build...")
        skip_build = True
    else:
        if FORCE_REBUILD:
            print(f"🔨 Forcing rebuild of image {image_name}...")
        else:
            print(f"🔨 Image {image_name} not found, building...")
        prepare_versioned_framework(framework_name, version)
        skip_build = False

    # Validation mode: only tests whether the framework responds
    if validate_only:
        if not skip_build:
            # Build is required first
            try:
                cmd_build = f"docker build -f frameworks/Dockerfile -t {image_name} frameworks/{framework_name}"
                run(cmd_build)
                print(f"✅ Build complete!")
            except subprocess.CalledProcessError as e:
                print(f"❌ Build error for {versioned_name}: {e}")
                return False

        # Validate whether the framework responds
        return validate_framework(framework_name, version)
    else:
        # Full benchmark mode
        try:
            cmd_df = f"./benchmark.sh {framework_name} {version}"
            run(cmd_df)

            # Destination: inside exc_dir (round) or root for single run without flag
            base_dir = exc_dir if exc_dir is not None else ROOT_DIR
            result_dir = base_dir / f"results_{versioned_name}"
            if result_dir.exists():
                shutil.rmtree(result_dir)
            RESULTS_DIR.rename(result_dir)

            print(f"✅ Results saved to: {result_dir}")
            print(f"💾 Image {image_name} available for reuse\n")

            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error running benchmark for {versioned_name}: {e}")
            return False


def list_existing_images(framework_name):
    """Lists all existing images for a given framework"""
    success, output = run_output(
        f"docker images {framework_name}_app --format '{{{{.Tag}}}}'"
    )
    if success and output:
        tags = [tag for tag in output.split("\n") if tag and tag != "<none>"]
        return tags
    return []


def main():
    print("🐳 Docker Image Cache Manager for Benchmarks")
    print(f"🔄 Force rebuild: {'Yes' if FORCE_REBUILD else 'No'}")

    if VALIDATE_ONLY:
        print(f"🧪 Mode: VALIDATION ONLY (build + quick test)")
    elif USE_GOOD_VERSIONS:
        print(f"📋 Mode: Using versions from good_versions.json")
    else:
        print(f"🏃 Mode: Full benchmark")

    if not VALIDATE_ONLY:
        print(f"🔁 Rounds: {ROUNDS}")

    print("=" * 60)

    good_versions = {}
    good_versions_file = ROOT_DIR / "good_versions.json"

    # If --use-good-versions, load from file
    if USE_GOOD_VERSIONS:
        if not good_versions_file.exists():
            print("❌ File good_versions.json not found!")
            print("💡 Run with --validate-only first to generate the file")
            sys.exit(1)

        with open(good_versions_file, "r") as f:
            good_versions = json.load(f)

        print("📦 Versions loaded from good_versions.json:")
        for fw, versions in good_versions.items():
            print(f"  {fw}: {len(versions)} versions")
        print("=" * 60)

        # Use the validated versions
        FRAMEWORKS.update(
            {
                fw: versions.copy()
                for fw, versions in good_versions.items()
                if fw in FRAMEWORKS_NAMES
            }
        )
    else:
        # Collect versions from PyPI
        for framework in FRAMEWORKS_NAMES:
            good_versions[framework] = []
            versions_list = sorted(get_versions(framework), reverse=True)
            pre_release = ("a", "b", "rc", "dev", "post")
            versions_list = [v for v in versions_list if not any(tag in v for tag in pre_release)]

            if versions_list:
                FRAMEWORKS[framework] = versions_list

                # List already existing images
                existing_images = list_existing_images(framework)
                if existing_images and not VALIDATE_ONLY:
                    print(
                        f"📦 Existing images for {framework}: {', '.join(existing_images)}"
                    )
            else:
                print(
                    f"⚠️ Warning: No versions found for framework '{framework}'."
                )

    print("=" * 60)

    ensure_docker_network(NETWORK)

    total_versions = sum(len(versions) for versions in FRAMEWORKS.values())

    # Validation mode: no rounds
    if VALIDATE_ONLY:
        current = 0
        for framework, versions in FRAMEWORKS.items():
            for version in versions:
                current += 1
                print(f"\n📊 Progress: {current}/{total_versions}")
                success = run_benchmark(framework, version, validate_only=True)
                if success and not USE_GOOD_VERSIONS:
                    good_versions[framework].append(version)

        if not USE_GOOD_VERSIONS:
            with open(good_versions_file, "w") as f:
                json.dump(good_versions, f, indent=4)

        print("\n" + "=" * 60)
        print("✅ Validation complete!")
        print(f"📊 Validated versions saved to: {good_versions_file}")
        print("\n💡 To run full benchmarks on validated versions:")
        print("   ./run.py --use-good-versions")
        return

    # Benchmark mode: run N rounds
    next_exc = get_next_execution_number()

    for round_offset in range(ROUNDS):
        exc_number = next_exc + round_offset
        exc_dir = ROOT_DIR / f"results_exc_{exc_number}"
        exc_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n{'#' * 60}")
        print(f"# ROUND {exc_number}  ({round_offset + 1}/{ROUNDS})")
        print(f"# Directory: {exc_dir.name}")
        print(f"{'#' * 60}")

        current = 0
        for framework, versions in FRAMEWORKS.items():
            for version in versions:
                current += 1
                print(f"\n📊 [{exc_dir.name}] Progress: {current}/{total_versions}")
                success = run_benchmark(
                    framework, version, validate_only=False, exc_dir=exc_dir
                )
                if success and not USE_GOOD_VERSIONS:
                    if version not in good_versions.get(framework, []):
                        good_versions.setdefault(framework, []).append(version)

        print(f"\n✅ Round {exc_number} complete → {exc_dir.name}/")

    # Save good_versions only if not already using the file
    if not USE_GOOD_VERSIONS:
        with open(good_versions_file, "w") as f:
            json.dump(good_versions, f, indent=4)

    print("\n" + "=" * 60)
    print(f"✅ All {ROUNDS} round(s) complete!")

    # Show summary of created rounds
    created = sorted(
        [d for d in ROOT_DIR.iterdir() if re.match(r"^results_exc_\d+$", d.name)],
        key=lambda d: int(re.search(r"(\d+)$", d.name).group(1)),
    )
    print(f"\n📁 Available executions ({len(created)} total)")

    print("\n🐳 Cached Docker images:")
    for framework in FRAMEWORKS_NAMES:
        images = list_existing_images(framework)
        if images:
            print(f"  {framework}: {len(images)} versions")


if __name__ == "__main__":
    main()
