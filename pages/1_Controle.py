import streamlit as st
import pandas as pd
from pathlib import Path

def page_controle():
    STORAGE_FILE = Path("carteira.csv")

    st.title("🔧 Painel de Controle — Carteira")

    if not STORAGE_FILE.exists():
        st.error("O arquivo 'carteira.csv' não foi encontrado no diretório da aplicação.")
    else:
        df = pd.read_csv(STORAGE_FILE)
        # Ordena por quantidade desc como solicitado
        if 'Quantidade' in df.columns:
            df = df.sort_values(by='Quantidade', ascending=False).reset_index(drop=True)

        st.subheader("📋 Auditoria e Edição Rápida")
        st.write("Edite os campos diretamente e salve as alterações para atualizar a carteira principal.")

        # Mostrar métrica de soma de Meta e validar 100%
        soma_meta = 0
        if 'Meta' in df.columns:
            try:
                soma_meta = df['Meta'].astype(float).sum()
            except Exception:
                soma_meta = None

        if soma_meta is None:
            st.warning("Não foi possível somar a coluna 'Meta' — verifique o formato dos valores.")
        else:
            st.metric("Soma das Metas (%)", f"{soma_meta:.1f}%")
            if f"{soma_meta:.1f}" != "100.0":
                st.warning("A soma das metas não é 100%. Revise a distribuição de metas antes de salvar.")

        edited = st.data_editor(
            df,
            key="controle_editor",
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            height=400 + (len(df) * 18)
        )

        # Counter para forçar recriação do checkbox após salvar
        if "checkbox_reset_counter" not in st.session_state:
            st.session_state.checkbox_reset_counter = 0

        confirm_save = st.checkbox(
            "Estou ciente e quero salvar as alterações no CSV",
            key=f"confirm_save_{st.session_state.checkbox_reset_counter}"
        )

        if st.button("💾 Salvar Alterações na Carteira", disabled=not confirm_save):
            try:
                edited[df.columns].to_csv(STORAGE_FILE, index=False)
                st.success("Arquivo 'carteira.csv' atualizado com sucesso.")
                st.session_state.checkbox_reset_counter += 1
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar o arquivo: {e}")
if __name__ == "__main__":
    page_controle()
