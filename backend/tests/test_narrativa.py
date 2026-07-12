"""Testes da narrativa: prompt com grounding, validação (guardrail) e fallback."""

from __future__ import annotations

from datetime import date

import pytest

from srag_report.application import narrativa as n
from srag_report.domain.errors import ErroGuardrail
from srag_report.domain.models import Metrica, Noticia


def _m(nome: str, valor: float | None) -> Metrica:
    return Metrica(nome=nome, valor=valor, unidade="%", denominador=100)


def test_prompt_faz_grounding_nos_numeros_e_fontes() -> None:
    system, user = n.montar_prompt(
        [_m("Taxa de mortalidade", 5.0)],
        [Noticia(titulo="SRAG sobe", fonte="G1", url="http://x")],
        date(2026, 7, 5),
    )
    assert "somente" in system.lower()  # instrução anti-alucinação (grounding)
    assert "Taxa de mortalidade" in user and "5.0%" in user
    assert "SRAG sobe" in user and "G1" in user


def test_prompt_sem_dados_sinaliza_ausencia() -> None:
    _, user = n.montar_prompt([], [], None)
    assert "(sem métricas)" in user and "(sem notícias)" in user


def test_prompt_metrica_na() -> None:
    _, user = n.montar_prompt([_m("X", None)], [], date(2026, 1, 1))
    assert "N/A" in user


def test_validar_narrativa_strip_e_vazia() -> None:
    assert n.validar_narrativa("  texto  ") == "texto"
    with pytest.raises(ErroGuardrail):
        n.validar_narrativa("   ")


def test_fallback_com_e_sem_metricas() -> None:
    com = n.narrativa_fallback([_m("Taxa de mortalidade", 5.0)], date(2026, 7, 5))
    assert "5.0%" in com and "2026-07-05" in com
    assert "sem métricas" in n.narrativa_fallback([], None)
