from pathlib import Path

from common import get_base_dir
from preprocessa_relatorio_unico import processa_relatorio_unico
from combina_reordena import main as combina_reordena_main
import configparser


BASE_DIR = get_base_dir()
RAW_DIR = BASE_DIR / "csv_brutos"
PARES_DIR = BASE_DIR / "csv_fora_ordem"
OUT_DIR = BASE_DIR / "csv_tratados"

RAW_DIR.mkdir(exist_ok=True)
PARES_DIR.mkdir(exist_ok=True)
OUT_DIR.mkdir(exist_ok=True)

def get_registros_faltantes() -> dict:
    config = configparser.ConfigParser()
    config_path = BASE_DIR / "config.ini"
    if not config_path.exists():
        return {}
    config.read(config_path, encoding="utf-8")
    registros_faltantes = {}
    if config.has_section("REGISTROS_FALTANTES"):
        for nome, semanas_str in config.items("REGISTROS_FALTANTES"):
            registros_faltantes[nome.lower()] = [
                int(s.strip()) for s in semanas_str.split(",") if s.strip()
            ]
    return registros_faltantes

def processa_arquivo(arquivo: Path, registros_faltantes: dict):  # ← novo parâmetro
    nome_base = arquivo.stem
    saida = OUT_DIR / f"{nome_base}_tratado.csv"

    semanas_sem_registro = registros_faltantes.get(nome_base.lower(), [])  # ← busca no config

    print(f"\n=== {arquivo.name} ===")
    print("Processando relatório único...")
    if semanas_sem_registro:
        print(f"  Semanas sem registro declaradas: {semanas_sem_registro}")
    processa_relatorio_unico(arquivo, saida, semanas_sem_registro=semanas_sem_registro)  # ← passa adiante
    print("OK")

def processa_pares():
    """Processa pares Quiz/Registros fora de ordem."""
    arquivos = sorted(PARES_DIR.glob("*_Quiz.csv"))
    processados = set()
    
    for quiz_file in arquivos:
        base_name = quiz_file.stem.replace('_Quiz', '')
        regs_file = PARES_DIR / f"{base_name}_Registros.csv"
        
        if regs_file.exists() and regs_file not in processados:
            print(f"\n=== Processando par: {base_name} ===")
            print("Combinando e reordenando Quiz + Registros...")
            combina_reordena_main(str(regs_file), str(quiz_file))
            processados.add(regs_file)
            processados.add(quiz_file)
            print("OK")
        else:
            print(f"Aviso: Par incompleto para {base_name} (faltando Registros ou já processado)")

def main():
    registros_faltantes = get_registros_faltantes()
    
    print("Processando arquivos em pares (desordenados)...")
    processa_pares()
    
    print("\nProcessando arquivos únicos...")
    arquivos = sorted(RAW_DIR.glob("*.csv"))
    if not arquivos:
        print("Atenção - Nenhum CSV encontrado em csv_brutos/.")
    else:
        for arq in arquivos:
            processa_arquivo(arq, registros_faltantes)

    print("\n Ok Pipeline concluída.")
    print(f"Arquivos tratados em: {OUT_DIR}")

if __name__ == "__main__":
    main()
