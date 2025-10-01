#!/usr/bin/env python3
"""
Script para extrair dados de emissão de carbono de resultados de frameworks.
Processa pastas no formato "results_framework_X_Y_Z" e extrai dados do emissions.csv.
"""

import os
import csv
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import sys
from collections import OrderedDict

# CONFIGURAÇÃO: Frameworks específicos para processar (None = todos)
# Exemplos: ["fastapi"], ["django", "flask"], ["tensorflow", "pytorch"]
#FILTER_FRAMEWORKS = None  # Altere aqui para filtrar frameworks específicos
FILTER_FRAMEWORKS = ["fastapi"]  # Descomente e edite para filtrar


def find_results_folders(base_path: str = ".", filter_frameworks: Optional[List[str]] = None) -> List[Path]:
    """
    Encontra todas as pastas que seguem o padrão results_framework_X_Y_Z
    
    Args:
        base_path: Caminho base para buscar as pastas
        filter_frameworks: Lista de frameworks para filtrar (None = todos)
        
    Returns:
        Lista de caminhos para as pastas encontradas
    """
    base_path = Path(base_path)
    pattern = re.compile(r'^results_([^_]+)_(.+)$')
    
    results_folders = []
    
    for item in base_path.iterdir():
        if item.is_dir():
            match = pattern.match(item.name)
            if match:
                framework_name = match.group(1).lower()  # Converter para minúsculo para comparação
                
                # Se há filtro de frameworks, verificar se este framework está na lista
                if filter_frameworks is not None:
                    # Converter lista de filtros para minúsculo para comparação case-insensitive
                    filter_lower = [fw.lower() for fw in filter_frameworks]
                    if framework_name not in filter_lower:
                        continue  # Pular este framework
                
                results_folders.append(item)
    
    return sorted(results_folders)


def extract_version_from_folder_name(folder_name: str) -> str:
    """
    Extrai a versão do nome da pasta
    
    Args:
        folder_name: Nome da pasta no formato results_framework_X_Y_Z
        
    Returns:
        Versão extraída (X_Y_Z)
    """
    pattern = re.compile(r'^results_([^_]+)_(.+)$')
    match = pattern.match(folder_name)
    
    if match:
        framework_name = match.group(1)
        version = match.group(2)
        return version
    
    return folder_name


def read_emissions_csv(csv_path: Path) -> List[Dict[str, float]]:
    """
    Lê o arquivo emissions.csv e retorna lista com dados de cada linha
    
    Args:
        csv_path: Caminho para o arquivo emissions.csv
        
    Returns:
        Lista de dicionários, um para cada linha do CSV
    """
    if not csv_path.exists():
        print(f"Arquivo não encontrado: {csv_path}")
        return []
    
    emissions_data = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row_num, row in enumerate(reader, 1):
                try:
                    # Converte emissions e emissions_rate para float
                    emissions = float(row.get('emissions', 0))
                    emissions_rate = float(row.get('emissions_rate', 0))
                    
                    emissions_data.append({
                        "emissions": emissions,
                        "emissions_rate": emissions_rate
                    })
                    
                except (ValueError, TypeError) as e:
                    print(f"Erro ao processar linha {row_num}: {e}")
                    continue
        
        return emissions_data
        
    except Exception as e:
        print(f"Erro ao ler arquivo {csv_path}: {e}")
        return []


def process_all_results(base_path: str = ".", filter_frameworks: Optional[List[str]] = None) -> Dict[str, List[Dict[str, float]]]:
    """
    Processa todas as pastas de resultados e extrai dados de emissão
    
    Args:
        base_path: Caminho base onde estão as pastas de resultados
        filter_frameworks: Lista de frameworks para filtrar (None = todos)
        
    Returns:
        Dicionário onde chave é a versão e valor é lista de objetos com emissions e emissions_rate
    """
    results_folders = find_results_folders(base_path, filter_frameworks)
    
    if not results_folders:
        if filter_frameworks:
            print(f"Nenhuma pasta de resultados encontrada para os frameworks: {filter_frameworks}")
        else:
            print("Nenhuma pasta de resultados encontrada!")
        return {}
    
    results_data = {}
    
    for folder in results_folders:
        print(f"Processando pasta: {folder.name}")
        
        # Extrai versão do nome da pasta
        version = extract_version_from_folder_name(folder.name)
        version = version.replace("_", ".")
        
        # Caminho para o arquivo emissions.csv
        emissions_csv_path = folder / "carbon" / "emissions.csv"
        
        # Lê e processa os dados de emissão
        emissions_data = read_emissions_csv(emissions_csv_path)
        
        # Adiciona os dados com a versão como chave
        results_data[version] = emissions_data
        
        print(f"  Versão: {version}")
        print(f"  Número de registros de emissão: {len(emissions_data)}")
        
        if emissions_data:
            # Mostra estatísticas dos dados
            total_emissions = sum(item['emissions'] for item in emissions_data)
            avg_emissions_rate = sum(item['emissions_rate'] for item in emissions_data) / len(emissions_data)
            
            print(f"  Total de emissões: {total_emissions:.2e}")
            print(f"  Taxa média de emissões: {avg_emissions_rate:.2e}")
        print()
    
    return OrderedDict(sorted(results_data.items())) #melhora ordenação mas n resolveu


def save_to_json(data: Dict[str, List[Dict[str, float]]], output_file: str = "carbon_emissions_data.json"):
    """
    Salva os dados processados em um arquivo JSON
    
    Args:
        data: Dados processados (versão -> lista de emissões)
        output_file: Nome do arquivo de saída
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
        
        print(f"Dados salvos em: {output_file}")
        
    except Exception as e:
        print(f"Erro ao salvar arquivo JSON: {e}")


def parse_frameworks_from_args(args: List[str]) -> Optional[List[str]]:
    """
    Extrai lista de frameworks dos argumentos da linha de comando
    
    Args:
        args: Lista de argumentos (sys.argv)
        
    Returns:
        Lista de frameworks ou None se não especificado
    """
    frameworks = []
    
    # Procura por argumentos que começam com --frameworks
    i = 0
    while i < len(args):
        arg = args[i]
        
        if arg == "--frameworks" and i + 1 < len(args):
            # Próximo argumento deve ser a lista de frameworks separados por vírgula
            frameworks_str = args[i + 1]
            frameworks = [fw.strip() for fw in frameworks_str.split(',')]
            break
        elif arg.startswith("--frameworks="):
            # Formato --frameworks=fastapi,django
            frameworks_str = arg.split('=', 1)[1]
            frameworks = [fw.strip() for fw in frameworks_str.split(',')]
            break
            
        i += 1
    
    return frameworks if frameworks else None


def print_usage():
    """
    Imprime informações de uso do script
    """
    print("Uso:")
    print("  python carbon_emissions_extractor.py [pasta_base] [--frameworks framework1,framework2,...]")
    print()
    print("Exemplos:")
    print("  python carbon_emissions_extractor.py")
    print("  python carbon_emissions_extractor.py /caminho/para/resultados")
    print("  python carbon_emissions_extractor.py --frameworks fastapi,django")
    print("  python carbon_emissions_extractor.py /caminho --frameworks tensorflow,pytorch")
    print()


def main():
    """
    Função principal do script
    """
    print("=== Extrator de Dados de Emissão de Carbono ===\n")
    
    # Verifica se foi pedido help
    if "--help" in sys.argv or "-h" in sys.argv:
        print_usage()
        return
    
    # Define o caminho base
    base_path = "."
    for arg in sys.argv[1:]:
        if not arg.startswith("--") and os.path.exists(arg):
            base_path = arg
            break
    
    # Determina frameworks para filtrar (prioridade: linha de comando > configuração hardcoded)
    frameworks_from_args = parse_frameworks_from_args(sys.argv)
    filter_frameworks = frameworks_from_args if frameworks_from_args else FILTER_FRAMEWORKS
    
    print(f"Buscando pastas de resultados em: {os.path.abspath(base_path)}")
    
    if filter_frameworks:
        print(f"Filtrando pelos frameworks: {filter_frameworks}")
    else:
        print("Processando todos os frameworks encontrados")
    
    print()
    
    # Processa todos os resultados
    results = process_all_results(base_path, filter_frameworks)
    
    if not results:
        print("Nenhum dado foi extraído!")
        return
    
    # Salva os resultados em JSON
    save_to_json(results)
    
    # Estatísticas finais
    total_versions = len(results)
    total_records = sum(len(emissions_list) for emissions_list in results.values())
    
    print(f"Processamento concluído!")
    print(f"Versões processadas: {total_versions}")
    print(f"Total de registros de emissão: {total_records}")

if __name__ == "__main__":
    main()
