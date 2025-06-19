#!/usr/bin/env python3
import subprocess
from pathlib import Path
import shutil
import re

# Dicionário: framework -> lista de versões desejadas
FRAMEWORKS = {
    "aiohttp": ["3.8.1"],
    "blacksheep": ["1.2.6"],
    "baize": ["0.15.0"],
    "muffin": ["0.86.4"],
    "quart": ["0.18.3"],
    "sanic": ["22.9.0"],
    "starlette": ["0.27.0"],
    "django": ["4.2.0"],
    "falcon": ["3.1.1"],
    "fastapi": ["0.110.0", "0.111.0"],
    "emmett": ["2.5.0"],
    "tornado": ["6.3.3"],
}

FRAMEWORKS = {
    "fastapi": ["0.110.0", "0.111.0"],
}

FRAMEWORKS = {
    "fastapi": ["0.110.0"],
}

NETWORK = "data"
ROOT_DIR = Path(__file__).parent.resolve()
BASE_FRAMEWORKS_DIR = ROOT_DIR / "frameworks"
RESULTS_DIR = ROOT_DIR / "results"

def run(cmd, **kwargs):
    print(f"💻 Rodando: {cmd}")
    subprocess.run(cmd, shell=True, check=True, **kwargs)

def ensure_docker_network(network_name):
    try:
        subprocess.run(
            ["docker", "network", "inspect", network_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        print(f"🔌 Rede Docker '{network_name}' já existe.")
    except subprocess.CalledProcessError:
        print(f"🔧 Criando rede Docker '{network_name}'...")
        run(f"docker network create {network_name}")

def prepare_versioned_framework(base_name, version):
    version_tag = version.replace(".", "_")
    new_name = f"{base_name}-{version_tag}"
    src_dir = BASE_FRAMEWORKS_DIR / base_name
    dst_dir = BASE_FRAMEWORKS_DIR / new_name
    print(f"📁 Criando cópia: {src_dir} → {dst_dir}")
    shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)

    # Atualizar requirements.txt
    req_file = dst_dir / "requirements.txt"
    if req_file.exists():
        lines = req_file.read_text().splitlines()
        base_pattern = re.compile(rf"^\s*{re.escape(base_name)}\s*==")
        new_lines = [line for line in lines if not base_pattern.match(line)]
        new_lines.append(f"{base_name}=={version}")
        req_file.write_text("\n".join(new_lines) + "\n")
    else:
        req_file.write_text(f"{base_name}=={version}\n")

    return new_name

def run_benchmark(framework_name, version):
    versioned_name = prepare_versioned_framework(framework_name, version)
    print("=" * 60)
    print(f"🚀 Benchmark: {framework_name} v{version}")
    print("=" * 60)
    try:
        cmd_df = f"./benchmark.sh {framework_name} {version}"
        run(cmd_df)
        result_dir = ROOT_DIR / f"results_{versioned_name}"
        if result_dir.exists():
            shutil.rmtree(result_dir)
        RESULTS_DIR.rename(result_dir)
        print(f"✅ Resultados salvos em: {result_dir}\n")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao rodar benchmark para {versioned_name}: {e}")
    finally:
        shutil.rmtree(BASE_FRAMEWORKS_DIR / versioned_name, ignore_errors=True)

def main():
    ensure_docker_network(NETWORK)
    for framework, versions in FRAMEWORKS.items():
        for version in versions:
            run_benchmark(framework, version)

if __name__ == "__main__":
    main()
