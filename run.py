#!/usr/bin/env python3
import subprocess
from pathlib import Path
import shutil
import re
from util.python_lib_info import get_versions
import json

# Dicionário: framework -> lista de versões desejadas

BANNED =["blacksheep", "quart", "sanic", "emmett"]
# FRAMEWORKS_NAMES = ['aiohttp', 'baize', 'muffin', 'starlette', 'django', 'falcon', 'tornado', 'fastapi']
FRAMEWORKS_NAMES = ['fastapi']
FRAMEWORKS = {}

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
    path_dir = BASE_FRAMEWORKS_DIR / base_name
    req_file = path_dir / "requirements.txt"
    lines = req_file.read_text().splitlines()
    base_pattern = re.compile(rf"^\s*{re.escape(base_name)}\s*==")
    new_lines = [line for line in lines if not base_pattern.match(line)]
    new_lines.append(f"{base_name}=={version}")
    req_file.write_text("\n".join(new_lines) + "\n")

def run_benchmark(framework_name, version):
    prepare_versioned_framework(framework_name, version)
    versioned_name = f"{framework_name}_{version.replace('.', '_')}"
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
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao rodar benchmark para {versioned_name}: {e}")
        return False

def main():
    good_versions = {}
    for framework in FRAMEWORKS_NAMES:
        good_versions[framework] = []
        versions_list = sorted(get_versions(framework), reverse=True)
        versions_list = [v for v in versions_list if "b" not in v and "a" not in v]  # Ignora versões beta e alpha
        if versions_list:
            FRAMEWORKS[framework] = versions_list
        else:
            print(f"⚠️ Aviso: Nenhuma versão encontrada para o framework '{framework}'.")
    ensure_docker_network(NETWORK)
    for framework, versions in FRAMEWORKS.items():
        for version in versions:
            if run_benchmark(framework, version):
                good_versions[framework].append(version)
    
    with open("good_versions.json", "w") as f:
        json.dump(good_versions, f, indent=4)

if __name__ == "__main__":
    main()
