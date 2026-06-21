"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

# Caminho do prompt otimizado v2
V2_PROMPT_PATH = str(Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml")


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


@pytest.fixture
def prompt_data():
    """Fixture que carrega e retorna os dados do prompt v2."""
    data = load_prompts(V2_PROMPT_PATH)
    # Extrair dados do prompt (a chave principal é bug_to_user_story_v2)
    if "bug_to_user_story_v2" in data:
        return data["bug_to_user_story_v2"]
    return data


class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt_data):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in prompt_data, "Campo 'system_prompt' não encontrado no YAML"
        system_prompt = prompt_data["system_prompt"]
        assert system_prompt is not None, "system_prompt é None"
        assert isinstance(system_prompt, str), "system_prompt deve ser uma string"
        assert len(system_prompt.strip()) > 0, "system_prompt está vazio"

    def test_prompt_has_role_definition(self, prompt_data):
        """Verifica se o prompt define uma persona (ex: 'Você é um Product Manager')."""
        system_prompt = prompt_data.get("system_prompt", "").lower()

        # Verifica se contém palavras-chave de definição de persona/papel
        role_keywords = [
            "você é",
            "voce é",
            "você é um",
            "atue como",
            "seu papel",
            "sua função",
            "product manager",
            "especialista",
            "profissional",
            "senior",
            "sênior",
        ]

        has_role = any(keyword in system_prompt for keyword in role_keywords)
        assert has_role, (
            "O prompt não define uma persona/papel (role). "
            "Adicione uma definição como 'Você é um Senior Product Manager...'"
        )

    def test_prompt_mentions_format(self, prompt_data):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        system_prompt = prompt_data.get("system_prompt", "").lower()

        # Verifica se menciona formato esperado
        format_keywords = [
            "markdown",
            "user story",
            "como um",
            "eu quero",
            "para que",
            "critérios de aceitação",
            "criterios de aceitação",
            "given-when-then",
            "dado que",
            "quando",
            "então",
        ]

        has_format = any(keyword in system_prompt for keyword in format_keywords)
        assert has_format, (
            "O prompt não menciona formato Markdown ou User Story padrão. "
            "Adicione instruções sobre o formato esperado da saída."
        )

    def test_prompt_has_few_shot_examples(self, prompt_data):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        system_prompt = prompt_data.get("system_prompt", "")

        # Verifica se contém padrões de exemplos Few-shot
        example_keywords = [
            "exemplo",
            "Exemplo",
            "EXEMPLO",
            "entrada:",
            "saída:",
            "Entrada:",
            "Saída:",
            "input:",
            "output:",
            "Bug Report:",
            "User Story:",
            "### Exemplo",
            "**Exemplo",
        ]

        has_examples = any(keyword in system_prompt for keyword in example_keywords)

        # Verificação adicional: deve ter pelo menos 2 exemplos distintos
        example_count = sum(1 for keyword in ["Exemplo 1", "Exemplo 2", "EXEMPLO 1", "EXEMPLO 2",
                                                "exemplo 1", "exemplo 2", "### Exemplo"]
                           if keyword in system_prompt)

        assert has_examples, (
            "O prompt não contém exemplos Few-shot (entrada/saída). "
            "Adicione pelo menos 2 exemplos claros de conversão bug → user story."
        )

    def test_prompt_no_todos(self, prompt_data):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        # Verifica todos os campos de texto do prompt
        for key, value in prompt_data.items():
            if isinstance(value, str):
                assert "[TODO]" not in value, (
                    f"Encontrado [TODO] no campo '{key}'. "
                    f"Remova todos os TODOs antes de finalizar."
                )
                assert "TODO:" not in value, (
                    f"Encontrado TODO: no campo '{key}'. "
                    f"Remova todos os TODOs antes de finalizar."
                )

    def test_minimum_techniques(self, prompt_data):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = prompt_data.get("techniques_applied", [])

        assert isinstance(techniques, list), (
            "O campo 'techniques_applied' deve ser uma lista"
        )
        assert len(techniques) >= 2, (
            f"Mínimo de 2 técnicas requeridas, encontradas: {len(techniques)}. "
            f"Adicione pelo menos 2 técnicas em 'techniques_applied'."
        )

        # Verificar que as técnicas não estão vazias
        for i, technique in enumerate(techniques):
            assert isinstance(technique, str) and len(technique.strip()) > 0, (
                f"Técnica {i + 1} está vazia ou não é uma string válida"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])