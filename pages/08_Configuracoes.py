import shutil
from datetime import datetime
import streamlit as st
from auth import alterar_senha, exigir_login
from config import APP_NAME, APP_VERSION, AUTHOR
from components.theme import aplicar_tema
from database.db import DB_FILE, listar_despesas, listar_receitas

aplicar_tema(); exigir_login()
st.title("⚙️ Configurações e segurança")
a,b,c=st.columns(3); a.metric("Aplicação",APP_NAME); b.metric("Versão",APP_VERSION); c.metric("Dados", "Locais")

with st.expander("🔐 Alterar senha"):
    with st.form("alterar_senha"):
        atual=st.text_input("Senha atual",type="password"); nova=st.text_input("Nova senha",type="password"); confirmar=st.text_input("Confirmar nova senha",type="password"); salvar=st.form_submit_button("Atualizar senha")
    if salvar:
        if nova != confirmar: st.error("As senhas não coincidem.")
        else:
            ok,msg=alterar_senha(st.session_state["usuario"],atual,nova); (st.success if ok else st.error)(msg)

st.subheader("Backup e exportação")
col1,col2=st.columns(2)
with col1:
    if st.button("Criar backup do banco",use_container_width=True):
        destino=DB_FILE.parent.parent / "backups" / f"finance_{datetime.now():%Y%m%d_%H%M%S}.db"; destino.parent.mkdir(exist_ok=True); shutil.copy2(DB_FILE,destino); st.success(f"Backup criado em: {destino}")
with col2:
    st.download_button("Baixar banco de dados",data=DB_FILE.read_bytes(),file_name="financeos_backup.db",mime="application/octet-stream",use_container_width=True)

linhas=["tipo,data,categoria,descricao,valor"]
for r in listar_receitas(): linhas.append(f"receita,{r['data']},{r['categoria']},{r['descricao'] or ''},{r['valor']}")
for d in listar_despesas(): linhas.append(f"despesa,{d['data']},{d['categoria']},{d['descricao'] or ''},{d['valor']}")
st.download_button("Exportar receitas e despesas (CSV)",data="\n".join(linhas).encode("utf-8-sig"),file_name="financeos_lancamentos.csv",mime="text/csv")
st.caption(f"Desenvolvido por {AUTHOR}. Faça backup antes de atualizações importantes.")
