"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt (ex: "meu_username/bug_to_user_story_v2")
        prompt_data: Dados do prompt carregados do YAML

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        system_prompt = prompt_data.get("system_prompt", "")
        user_prompt = prompt_data.get("user_prompt", "{bug_report}")

        # Criar ChatPromptTemplate com system + user messages
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_prompt),
        ])

        print(f"   Fazendo push do prompt: {prompt_name}")
        print(f"   → Modo: PÚBLICO")

        # Push para o LangSmith Hub (público)
        url = hub.push(
            prompt_name,
            prompt_template,
            new_repo_is_public=True,
            new_repo_description=prompt_data.get("description", "Prompt otimizado para converter bugs em User Stories"),
            tags=prompt_data.get("tags", []),
        )

        print(f"   ✓ Push realizado com sucesso!")
        print(f"   → URL: {url}")
        return True

    except Exception as e:
        error_msg = str(e)
        # 409 Conflict means prompt already exists and hasn't changed — treat as success
        if "409" in error_msg and "Nothing to commit" in error_msg:
            print(f"   ✓ Prompt já está atualizado no LangSmith Hub (nenhuma mudança detectada)")
            return True

        print(f"   ❌ Erro ao fazer push: {e}")
        print(f"\n   Verifique:")
        print(f"   - LANGSMITH_API_KEY está configurada no .env")
        print(f"   - USERNAME_LANGSMITH_HUB está configurado no .env")
        print(f"   - Sua conexão com a internet está funcionando")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []

    # Campos obrigatórios
    required_fields = ["description", "system_prompt", "version"]
    for field in required_fields:
        if field not in prompt_data:
            errors.append(f"Campo obrigatório faltando: {field}")

    # system_prompt não pode estar vazio
    system_prompt = prompt_data.get("system_prompt", "").strip()
    if not system_prompt:
        errors.append("system_prompt está vazio")

    # Não pode conter TODOs
    if "[TODO]" in system_prompt or "TODO" in system_prompt:
        errors.append("system_prompt ainda contém TODOs")

    # Mínimo de 2 técnicas
    techniques = prompt_data.get("techniques_applied", [])
    if len(techniques) < 2:
        errors.append(f"Mínimo de 2 técnicas requeridas, encontradas: {len(techniques)}")

    return (len(errors) == 0, errors)


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPTS OTIMIZADOS PARA LANGSMITH HUB")

    # Verificar variáveis de ambiente
    required_vars = ["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]
    if not check_env_vars(required_vars):
        return 1

    username = os.getenv("USERNAME_LANGSMITH_HUB")

    # Carregar prompt otimizado
    yaml_path = "prompts/bug_to_user_story_v2.yml"
    print(f"Carregando prompt de: {yaml_path}\n")

    yaml_data = load_yaml(yaml_path)
    if yaml_data is None:
        print(f"\n❌ Erro ao carregar {yaml_path}")
        print(f"   Certifique-se de que o arquivo existe e está no formato correto.")
        return 1

    # Extrair dados do prompt (a chave principal é bug_to_user_story_v2)
    prompt_key = "bug_to_user_story_v2"
    if prompt_key in yaml_data:
        prompt_data = yaml_data[prompt_key]
    else:
        # Tentar usar o YAML como está (pode ter estrutura flat)
        prompt_data = yaml_data

    print(f"   ✓ Prompt carregado: {prompt_data.get('description', 'N/A')}")
    print(f"   ✓ Versão: {prompt_data.get('version', 'N/A')}")
    print(f"   ✓ Técnicas: {prompt_data.get('techniques_applied', [])}\n")

    # Validar prompt
    print("Validando prompt...")
    is_valid, errors = validate_prompt(prompt_data)

    if not is_valid:
        print(f"\n❌ Prompt inválido! Erros encontrados:")
        for error in errors:
            print(f"   - {error}")
        print(f"\nCorreija os erros em {yaml_path} e tente novamente.")
        return 1

    print("   ✓ Prompt válido!\n")

    # Push para o LangSmith Hub
    prompt_name = f"{username}/bug_to_user_story_v2"
    print(f"Fazendo push para: {prompt_name}\n")

    success = push_prompt_to_langsmith(prompt_name, prompt_data)

    if success:
        print(f"\n✅ Push concluído com sucesso!")
        print(f"\nPróximos passos:")
        print(f"1. Verifique no dashboard: https://smith.langchain.com/prompts")
        print(f"2. Execute a avaliação: python src/evaluate.py")
        return 0
    else:
        print(f"\n❌ Falha no push do prompt.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
