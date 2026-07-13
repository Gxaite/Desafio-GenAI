"""Testes do agendador de coleta de notícias (loop asyncio em background).

Sem pytest-asyncio: cada teste dirige o loop com asyncio.run(). montar_dependencias e
atualizar_historico são substituídos por fakes — nada de I/O real (rede/banco).
"""

from __future__ import annotations

import asyncio

import pytest

import srag_report.api.agendador as agendador


class _DepsFake:
    fonte = "FONTE"
    noticias = "REPO"


def test_ciclo_coleta_e_registra(monkeypatch: pytest.MonkeyPatch) -> None:
    """Caminho feliz: monta deps, chama atualizar_historico com fonte+repo."""
    chamada: dict[str, object] = {}
    monkeypatch.setattr(agendador, "montar_dependencias", lambda: _DepsFake())

    def fake_atualizar(fonte: object, repo: object) -> int:
        chamada["args"] = (fonte, repo)
        return 7

    monkeypatch.setattr(agendador, "atualizar_historico", fake_atualizar)

    asyncio.run(agendador._ciclo())

    assert chamada["args"] == ("FONTE", "REPO")


def test_ciclo_engole_erro_e_nao_propaga(monkeypatch: pytest.MonkeyPatch) -> None:
    """Job de background: qualquer erro é registrado, nunca sobe (não derruba o loop)."""
    monkeypatch.setattr(agendador, "montar_dependencias", lambda: _DepsFake())

    def boom(fonte: object, repo: object) -> int:
        raise RuntimeError("falha simulada")

    monkeypatch.setattr(agendador, "atualizar_historico", boom)

    asyncio.run(agendador._ciclo())  # não deve levantar


def test_loop_coleta_roda_ciclo_e_agenda(monkeypatch: pytest.MonkeyPatch) -> None:
    """O loop dispara um ciclo ao subir e agenda o próximo (cancelado antes de dormir 6h)."""
    ciclos = {"n": 0}

    async def fake_ciclo() -> None:
        ciclos["n"] += 1

    monkeypatch.setattr(agendador, "_ciclo", fake_ciclo)

    async def run() -> None:
        tarefa = asyncio.create_task(agendador.loop_coleta(6))
        await asyncio.sleep(0.05)  # deixa o primeiro ciclo rodar
        tarefa.cancel()
        try:
            await tarefa
        except asyncio.CancelledError:
            pass

    asyncio.run(run())

    assert ciclos["n"] >= 1
