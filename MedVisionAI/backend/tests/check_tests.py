"""
Script rápido para validar que os testes estão configurados corretamente.

Execute este arquivo diretamente para verificar a estrutura de testes
sem precisar de todas as dependências instaladas.
"""

import sys
from pathlib import Path

# Cores para output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_status(message, status="info"):
    """Imprime mensagem colorida."""
    colors = {
        "success": GREEN,
        "error": RED,
        "warning": YELLOW,
        "info": BLUE
    }
    color = colors.get(status, RESET)
    symbol = {"success": "✓", "error": "✗", "warning": "⚠", "info": "ℹ"}
    print(f"{color}{symbol.get(status, '•')} {message}{RESET}")


def check_test_files():
    """Verifica que todos os arquivos de teste existem."""
    print("\n" + "="*60)
    print(f"{BLUE}Verificando Arquivos de Teste{RESET}")
    print("="*60 + "\n")
    
    test_files = [
        "conftest.py",
        "test_schemas.py",
        "test_api_video.py",
        "test_api_audio.py",
        "test_api_reports.py",
        "test_storage_service.py",
        "test_report_service.py",
        "test_edge_cases.py",
        "test_video_service.py",
        "test_audio_service.py",
        "test_gemini_service.py",
    ]
    
    tests_dir = Path(__file__).parent
    found = 0
    missing = []
    
    for test_file in test_files:
        file_path = tests_dir / test_file
        if file_path.exists():
            print_status(f"{test_file}", "success")
            found += 1
        else:
            print_status(f"{test_file} - NÃO ENCONTRADO", "error")
            missing.append(test_file)
    
    print(f"\n{GREEN}{found}/{len(test_files)}{RESET} arquivos encontrados")
    
    if missing:
        print_status(f"Faltando: {', '.join(missing)}", "warning")
    
    return len(missing) == 0


def check_config_files():
    """Verifica arquivos de configuração."""
    print("\n" + "="*60)
    print(f"{BLUE}Verificando Configuração{RESET}")
    print("="*60 + "\n")
    
    backend_dir = Path(__file__).parent.parent
    config_files = {
        "pytest.ini": "Configuração do PyTest",
        ".coveragerc": "Configuração de Coverage",
        "requirements.txt": "Dependências Python"
    }
    
    all_found = True
    for file_name, description in config_files.items():
        file_path = backend_dir / file_name
        if file_path.exists():
            print_status(f"{file_name} - {description}", "success")
        else:
            print_status(f"{file_name} - {description} - NÃO ENCONTRADO", "error")
            all_found = False
    
    return all_found


def count_test_cases():
    """Conta número aproximado de casos de teste."""
    print("\n" + "="*60)
    print(f"{BLUE}Contando Casos de Teste{RESET}")
    print("="*60 + "\n")
    
    tests_dir = Path(__file__).parent
    total_tests = 0
    
    test_patterns = ["def test_", "async def test_"]
    
    for test_file in tests_dir.glob("test_*.py"):
        count = 0
        try:
            content = test_file.read_text(encoding='utf-8')
            for pattern in test_patterns:
                count += content.count(pattern)
            
            if count > 0:
                print_status(f"{test_file.name}: ~{count} testes", "info")
                total_tests += count
        except Exception as e:
            print_status(f"Erro ao ler {test_file.name}: {e}", "warning")
    
    print(f"\n{GREEN}Total: ~{total_tests} casos de teste{RESET}")
    return total_tests


def check_markers():
    """Lista markers customizados configurados."""
    print("\n" + "="*60)
    print(f"{BLUE}Markers Customizados{RESET}")
    print("="*60 + "\n")
    
    markers = [
        ("unit", "Testes unitários isolados"),
        ("integration", "Testes de integração"),
        ("api", "Testes de endpoints da API"),
        ("slow", "Testes que demoram >5 segundos"),
        ("requires_model", "Requer modelo YOLO carregado"),
        ("requires_gemini", "Requer API Gemini"),
    ]
    
    for marker, description in markers:
        print_status(f"@pytest.mark.{marker} - {description}", "info")
    
    print(f"\n{GREEN}{len(markers)} markers configurados{RESET}")


def show_usage_examples():
    """Mostra exemplos de uso."""
    print("\n" + "="*60)
    print(f"{BLUE}Exemplos de Uso{RESET}")
    print("="*60 + "\n")
    
    examples = [
        ("pytest", "Executar todos os testes"),
        ("pytest -v", "Modo verboso"),
        ("pytest -m unit", "Apenas testes unitários"),
        ("pytest -m \"not slow\"", "Pular testes lentos"),
        ("pytest tests/test_schemas.py", "Arquivo específico"),
        ("pytest --cov=app", "Com cobertura de código"),
        ("pytest --cov=app --cov-report=html", "Relatório HTML"),
    ]
    
    for command, description in examples:
        print(f"{YELLOW}${RESET} {command}")
        print(f"  {description}\n")


def main():
    """Função principal."""
    print(f"\n{BLUE}{'='*60}")
    print("🧪 Verificação de Testes - MedVision AI")
    print(f"{'='*60}{RESET}\n")
    
    checks = [
        check_config_files(),
        check_test_files(),
    ]
    
    count_test_cases()
    check_markers()
    show_usage_examples()
    
    print("\n" + "="*60)
    if all(checks):
        print(f"{GREEN}✓ Todos os arquivos de teste estão no lugar!{RESET}")
        print(f"{GREEN}✓ Estrutura de testes configurada corretamente!{RESET}")
        print("\n💡 Execute 'pytest' para rodar os testes")
    else:
        print(f"{RED}✗ Alguns arquivos estão faltando{RESET}")
        print(f"{YELLOW}⚠ Verifique os erros acima{RESET}")
    print("="*60 + "\n")
    
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
