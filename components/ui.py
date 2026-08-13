"""Pequenos componentes visuais reutilizáveis do FinanceOS."""

from html import escape

import streamlit as st


def estado_vazio(titulo, descricao, icone="✨"):
    """Exibe um estado vazio consistente sem interromper o fluxo da página."""
    st.markdown(
        f"""
        <section class="fos-empty" role="status" aria-label="{escape(titulo)}">
          <span class="fos-empty__icon" aria-hidden="true">{escape(icone)}</span>
          <div>
            <strong>{escape(titulo)}</strong>
            <p>{escape(descricao)}</p>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def cabecalho_secao(titulo, descricao=None, icone="◆"):
    """Cria cabeçalhos de seção compactos e semanticamente previsíveis."""
    complemento = f"<p>{escape(descricao)}</p>" if descricao else ""
    st.markdown(
        f"""
        <header class="fos-section-heading">
          <span aria-hidden="true">{escape(icone)}</span>
          <div><h2>{escape(titulo)}</h2>{complemento}</div>
        </header>
        """,
        unsafe_allow_html=True,
    )
