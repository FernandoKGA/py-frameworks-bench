#!/usr/bin/env python3
"""
Sistema de Benchmark para Frameworks Python com Cache Docker

Modos de execução:
  ./run.py                        # Benchmark completo em todas as versões
  ./run.py --validate-only        # Apenas build + validação rápida
  ./run.py --use-good-versions    # Benchmark apenas em versões validadas
  ./run.py --force-rebuild        # Força rebuild mesmo se imagem existe

Flags:
  --validate-only, --build-only   Constrói imagens e valida com teste rápido
  --use-good-versions             Usa versões do good_versions.json
  --force-rebuild                 Reconstrói todas as imagens
  --help, -h                      Mostra esta ajuda

Workflow recomendado:
  1. ./run.py --validate-only          # Valida todas as versões (rápido)
  2. ./run.py --use-good-versions      # Benchmark completo apenas nas validadas
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

# Mostra ajuda se solicitado
if "--help" in sys.argv or "-h" in sys.argv:
    print(__doc__)
    sys.exit(0)
import sys

# Dicionário: framework -> lista de versões desejadas

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

# Opções de execução
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
            print("❌ --rounds requer um número inteiro positivo. Ex: --rounds 5")
            sys.exit(1)
    return 1


ROUNDS = parse_rounds()


def run(cmd, **kwargs):
    print(f"» Rodando: {cmd}")
    subprocess.run(cmd, shell=True, check=True, **kwargs)


def run_output(cmd, **kwargs):
    """Executa comando e retorna o output"""
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
        print(f"Rede Docker '{network_name}' já existe.")
    except subprocess.CalledProcessError:
        print(f"Criando rede Docker '{network_name}'...")
        run(f"docker network create {network_name}")


def image_exists(image_name):
    """Verifica se uma imagem Docker existe localmente"""
    success, _ = run_output(f"docker image inspect {image_name}")
    return success


def get_next_execution_number() -> int:
    """Detecta o número da última execução e retorna o próximo."""
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
    """Valida se o framework funciona com uma requisição rápida"""
    versioned_name = f"{framework_name}_{version.replace('.', '_')}"
    container_name = f"validate_{versioned_name}"

    print(f"  🧪 Validando {framework_name} v{version}...")

    try:
        # Remove container antigo se existir
        run_output(f"docker rm -f {container_name}")

        # Sobe container
        run(
            f"docker run -d -p 8080:8080 --name {container_name} {framework_name}_app:{version}",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Aguarda inicialização
        max_attempts = 10
        for attempt in range(max_attempts):
            time.sleep(1)
            try:
                response = requests.get("http://localhost:8080/html", timeout=2)
                if response.status_code == 200:
                    print(f"  ✅ {framework_name} v{version} validado com sucesso!")
                    run_output(f"docker stop -t 2 {container_name}")
                    run_output(f"docker rm {container_name}")
                    return True
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                continue

        print(f"  ❌ {framework_name} v{version} não respondeu em {max_attempts}s")
        run_output(f"docker stop -t 2 {container_name}")
        run_output(f"docker rm {container_name}")
        return False

    except Exception as e:
        print(f"  ❌ Erro ao validar {framework_name} v{version}: {e}")
        run_output(f"docker stop -t 2 {container_name}")
        run_output(f"docker rm {container_name}")
        return False


def prepare_versioned_framework(base_name, version):
    """Modifica o requirements.txt para usar a versão específica"""
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
        f"🚀 {'Validando' if validate_only else 'Benchmark'}: {framework_name} v{version}"
    )
    print(f"🐳 Imagem: {image_name}")
    print("=" * 60)

    # Verifica se a imagem já existe
    if image_exists(image_name) and not FORCE_REBUILD:
        print(f"✅ Imagem {image_name} já existe, pulando build...")
        skip_build = True
    else:
        if FORCE_REBUILD:
            print(f"🔨 Forçando rebuild da imagem {image_name}...")
        else:
            print(f"🔨 Imagem {image_name} não existe, construindo...")
        prepare_versioned_framework(framework_name, version)
        skip_build = False

    # Modo validação: apenas testa se funciona
    if validate_only:
        if not skip_build:
            # Precisa buildar primeiro
            try:
                cmd_build = f"docker build -f frameworks/Dockerfile -t {image_name} frameworks/{framework_name}"
                run(cmd_build)
                print(f"✅ Build concluído!")
            except subprocess.CalledProcessError as e:
                print(f"❌ Erro no build de {versioned_name}: {e}")
                return False

        # Valida se funciona
        return validate_framework(framework_name, version)
    else:
        # Modo benchmark completo
        try:
            cmd_df = f"./benchmark.sh {framework_name} {version}"
            run(cmd_df)

            # Destino: dentro de exc_dir (rodada) ou raiz se rodada única sem flag
            base_dir = exc_dir if exc_dir is not None else ROOT_DIR
            result_dir = base_dir / f"results_{versioned_name}"
            if result_dir.exists():
                shutil.rmtree(result_dir)
            RESULTS_DIR.rename(result_dir)

            print(f"✅ Resultados salvos em: {result_dir}")
            print(f"💾 Imagem {image_name} disponível para reuso\n")

            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao rodar benchmark para {versioned_name}: {e}")
            return False


def list_existing_images(framework_name):
    """Lista todas as imagens existentes para um framework"""
    success, output = run_output(
        f"docker images {framework_name}_app --format '{{{{.Tag}}}}'"
    )
    if success and output:
        tags = [tag for tag in output.split("\n") if tag and tag != "<none>"]
        return tags
    return []


def main():
    print("🐳 Docker Image Cache Manager for Benchmarks")
    print(f"🔄 Rebuild forçado: {'Sim' if FORCE_REBUILD else 'Não'}")

    if VALIDATE_ONLY:
        print(f"🧪 Modo: VALIDAÇÃO APENAS (build + teste rápido)")
    elif USE_GOOD_VERSIONS:
        print(f"📋 Modo: Usando versões do good_versions.json")
    else:
        print(f"🏃 Modo: Benchmark completo")

    if not VALIDATE_ONLY:
        print(f"🔁 Rodadas: {ROUNDS}")

    print("=" * 60)

    good_versions = {}
    good_versions_file = ROOT_DIR / "good_versions.json"

    # Se --use-good-versions, carrega do arquivo
    if USE_GOOD_VERSIONS:
        if not good_versions_file.exists():
            print("❌ Arquivo good_versions.json não encontrado!")
            print("💡 Execute primeiro com --validate-only para criar o arquivo")
            sys.exit(1)

        with open(good_versions_file, "r") as f:
            good_versions = json.load(f)

        print("📦 Versões carregadas do good_versions.json:")
        for fw, versions in good_versions.items():
            print(f"  {fw}: {len(versions)} versões")
        print("=" * 60)

        # Usa as versões validadas
        FRAMEWORKS.update(
            {
                fw: versions.copy()
                for fw, versions in good_versions.items()
                if fw in FRAMEWORKS_NAMES
            }
        )
    else:
        # Coleta versões do PyPI
        for framework in FRAMEWORKS_NAMES:
            good_versions[framework] = []
            versions_list = sorted(get_versions(framework), reverse=True)
            pre_release = ("a", "b", "rc", "dev", "post")
            versions_list = [v for v in versions_list if not any(tag in v for tag in pre_release)]

            if versions_list:
                FRAMEWORKS[framework] = versions_list

                # Lista imagens já existentes
                existing_images = list_existing_images(framework)
                if existing_images and not VALIDATE_ONLY:
                    print(
                        f"📦 Imagens existentes para {framework}: {', '.join(existing_images)}"
                    )
            else:
                print(
                    f"⚠️ Aviso: Nenhuma versão encontrada para o framework '{framework}'."
                )

    print("=" * 60)

    ensure_docker_network(NETWORK)

    total_versions = sum(len(versions) for versions in FRAMEWORKS.values())

    # Modo validação: sem rodadas
    if VALIDATE_ONLY:
        current = 0
        for framework, versions in FRAMEWORKS.items():
            for version in versions:
                current += 1
                print(f"\n📊 Progresso: {current}/{total_versions}")
                success = run_benchmark(framework, version, validate_only=True)
                if success and not USE_GOOD_VERSIONS:
                    good_versions[framework].append(version)

        if not USE_GOOD_VERSIONS:
            with open(good_versions_file, "w") as f:
                json.dump(good_versions, f, indent=4)

        print("\n" + "=" * 60)
        print("✅ Validação concluída!")
        print(f"📊 Versões validadas salvas em: {good_versions_file}")
        print("\n💡 Para rodar benchmarks completos nas versões validadas:")
        print("   ./run.py --use-good-versions")
        return

    # Modo benchmark: executa N rodadas
    next_exc = get_next_execution_number()

    for round_offset in range(ROUNDS):
        exc_number = next_exc + round_offset
        exc_dir = ROOT_DIR / f"results_exc_{exc_number}"
        exc_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n{'#' * 60}")
        print(f"# RODADA {exc_number}  ({round_offset + 1}/{ROUNDS})")
        print(f"# Diretório: {exc_dir.name}")
        print(f"{'#' * 60}")

        current = 0
        for framework, versions in FRAMEWORKS.items():
            for version in versions:
                current += 1
                print(f"\n📊 [{exc_dir.name}] Progresso: {current}/{total_versions}")
                success = run_benchmark(
                    framework, version, validate_only=False, exc_dir=exc_dir
                )
                if success and not USE_GOOD_VERSIONS:
                    if version not in good_versions.get(framework, []):
                        good_versions.setdefault(framework, []).append(version)

        print(f"\n✅ Rodada {exc_number} concluída → {exc_dir.name}/")

    # Salva good_versions apenas se não estava usando o arquivo
    if not USE_GOOD_VERSIONS:
        with open(good_versions_file, "w") as f:
            json.dump(good_versions, f, indent=4)

    print("\n" + "=" * 60)
    print(f"✅ Todas as {ROUNDS} rodada(s) concluídas!")

    # Mostra resumo das rodadas criadas
    created = sorted(
        [d for d in ROOT_DIR.iterdir() if re.match(r"^results_exc_\d+$", d.name)],
        key=lambda d: int(re.search(r"(\d+)$", d.name).group(1)),
    )
    print(f"\n📁 Execuções disponíveis ({len(created)} total)")

    print("\n🐳 Imagens Docker em cache:")
    for framework in FRAMEWORKS_NAMES:
        images = list_existing_images(framework)
        if images:
            print(f"  {framework}: {len(images)} versões")


if __name__ == "__main__":
    main()
