"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()


def pull_prompts_from_langsmith():
    """
    Faz pull do prompt bug_to_user_story_v1 do LangSmith Hub
    e retorna os dados serializados em formato dicionário.

    Returns:
        dict: Dados do prompt em formato YAML-friendly ou None se falhar
    """
    prompt_owner = "leonanluppi"
    prompt_name = "bug_to_user_story_v1"
    full_name = f"{prompt_owner}/{prompt_name}"

    print(f"   Fazendo pull do prompt: {full_name}")

    try:
        prompt = hub.pull(full_name)
        print(f"   ✓ Prompt carregado com sucesso do LangSmith Hub")

        # Extrair mensagens do ChatPromptTemplate
        system_prompt = ""
        user_prompt = ""

        for message in prompt.messages:
            msg_type = type(message).__name__
            # Extrair o conteúdo do template
            if hasattr(message, 'prompt') and hasattr(message.prompt, 'template'):
                content = message.prompt.template
            elif hasattr(message, 'content'):
                content = message.content
            else:
                content = str(message)

            if "System" in msg_type:
                system_prompt = content
            elif "Human" in msg_type:
                user_prompt = content

        # Montar estrutura YAML
        prompt_data = {
            prompt_name: {
                "description": "Prompt para converter relatos de bugs em User Stories",
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "version": "v1",
                "created_at": "2025-01-15",
                "tags": ["bug-analysis", "user-story", "product-management"]
            }
        }

        return prompt_data

    except Exception as e:
        print(f"   ❌ Erro ao fazer pull do prompt: {e}")
        print(f"\n   Verifique:")
        print(f"   - LANGSMITH_API_KEY está configurada no .env")
        print(f"   - O prompt '{full_name}' existe no LangSmith Hub")
        print(f"   - Sua conexão com a internet está funcionando")
        return None


def main():
    """Função principal"""
    print_section_header("PULL DE PROMPTS DO LANGSMITH HUB")

    # Verificar variáveis de ambiente
    required_vars = ["LANGSMITH_API_KEY"]
    if not check_env_vars(required_vars):
        return 1

    # Fazer pull do prompt
    print("Iniciando pull dos prompts...\n")
    prompt_data = pull_prompts_from_langsmith()

    if prompt_data is None:
        print("\n❌ Falha ao fazer pull dos prompts.")
        return 1

    # Salvar localmente
    output_path = "prompts/bug_to_user_story_v1.yml"
    print(f"\n   Salvando prompt em: {output_path}")

    if save_yaml(prompt_data, output_path):
        print(f"   ✓ Prompt salvo com sucesso em {output_path}")
        print(f"\n✅ Pull concluído! Prompt salvo localmente.")
        print(f"\nPróximos passos:")
        print(f"1. Analise o prompt em {output_path}")
        print(f"2. Crie sua versão otimizada em prompts/bug_to_user_story_v2.yml")
        return 0
    else:
        print(f"   ❌ Erro ao salvar prompt em {output_path}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
