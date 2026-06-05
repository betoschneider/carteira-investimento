import yfinance as yf
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
import dotenv
import os
import time

dotenv.load_dotenv()

# --- CAMADA DE DADOS ---

@st.cache_data(ttl=3600) # Cache de 1 hora para as cotações
def fetch_prices(ticker_list):
    data_list = []
    for t in ticker_list:
        try:
            ticker_obj = yf.Ticker(t)
            info = ticker_obj.fast_info
            price = round(info['last_price'], 2)
            
            if pd.isna(price) or price <= 0:
                t_base = t.replace("F.SA", ".SA")
                price = round(yf.Ticker(t_base).fast_info['last_price'], 2)
                
            data_list.append([t.replace(".SA", ""), price])
            time.sleep(0.2)
        except Exception as e:
            st.error(f"Erro ao buscar {t}: {e}")
    return data_list

def get_base_data():
    """Lê a lista de ações do CSV."""
    arquivo = 'carteira.csv'
    df_base = pd.read_csv(arquivo)
    tickers = (df_base['Ativo'] + '.SA').unique().tolist()
    return tickers

# --- CALLBACK PARA SALVAR AS EDIÇÕES INSTATANEAMENTE ---
def salvar_edicoes_editor():
    """Captura o que foi alterado na UI e consolida no nosso DataFrame do Session State."""
    key = "meu_data_editor"
    if key in st.session_state and "edited_rows" in st.session_state[key]:
        edited_rows = st.session_state[key]["edited_rows"]
        for idx, updates in edited_rows.items():
            if "Sugerido (Cotas)" in updates:
                st.session_state.df_aporte_atual.iloc[idx, st.session_state.df_aporte_atual.columns.get_loc("Sugerido (Cotas)")] = updates["Sugerido (Cotas)"]

# --- LOGICA DE NEGOCIO ---

def page_main():
    # 1. Busca Dados e Cruzamento
    ticker_list = get_base_data()
    
    with st.spinner('Atualizando cotações do Yahoo Finance...'):
        precos_atualizados = fetch_prices(ticker_list)

    df_precos = pd.DataFrame(precos_atualizados, columns=['Ativo', 'Preço'])
    df_base = pd.read_csv('carteira.csv')
    df_completo = pd.merge(df_base, df_precos, on='Ativo', how='left')
    
    # 2. Cálculos de Desvio da Meta
    df_completo['Total Atual'] = df_completo['Quantidade'] * df_completo['Preço']
    patrimonio_total = df_completo['Total Atual'].sum()
    
    if patrimonio_total > 0:
        df_completo['% Atual'] = (df_completo['Total Atual'] / patrimonio_total) * 100
    else:
        df_completo['% Atual'] = 0.0
        
    df_completo['Desvio'] = df_completo['% Atual'] - df_completo['Meta']
    
    df_completo = df_completo.sort_values(by='Desvio', ascending=True)
    
    data_atualizacao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    st.title("📈 Carteira de investimento - B3")
    st.write(f"Última consulta à API: {data_atualizacao}")

    

    c10, c20 = st.columns(2)
    with c10:
        st.subheader("📋 Situação Atual da Carteira")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Patrimônio Total", f"R$ {patrimonio_total:,.2f}")
        with col2:
            st.metric("Total de Ativos Monitorados", f"{len(df_completo)}")
        
        df_display = df_completo[['Empresa', 'Ativo', 'Quantidade', 'Preço', 'Total Atual', 'Meta', '% Atual', 'Desvio']].copy()
        df_display['Total Atual'] = df_display['Total Atual'].round(2)
        df_display['% Atual'] = df_display['% Atual'].round(1)
        df_display['Desvio'] = df_display['Desvio'].round(1)
        df_display['Meta'] = df_display['Meta'].round(1)
        df_display['Empresa'] = df_display.apply(lambda x: x['Empresa'] + " (" + x['Ativo'] + ")", axis=1)
        df_display = df_display.drop(columns=['Ativo'])
        st.dataframe(df_display, hide_index=True, height=400 + (len(df_completo) * 15))

    # st.markdown("---")
    
    with c20:
        st.subheader("📊 Gráfico de Desvio da Meta Perfeita")
        
        fig_eq = go.Figure()
        fig_eq.add_trace(go.Bar(
            x=df_completo['Desvio'], 
            y=df_completo['Ativo'], 
            orientation='h',
            text=df_completo['Desvio'].round(1).apply(lambda x: f"{x}%"), 
            textposition='auto',
            marker_color='royalblue', 
            name='Desvio Atual'
        ))
        fig_eq.add_vline(x=0, line_dash="dash", line_color="red", annotation_text="Equilíbrio Perfeito (Meta)")
        
        fig_eq.update_layout(
            title="Quão longe o ativo está da Meta Estipulada? (Em % da Carteira)",
            xaxis_title="Desvio ( % Atual - % Meta )",
            yaxis={'categoryorder': 'total descending'},
            height=400 + (len(df_completo) * 20)
        )
        st.plotly_chart(fig_eq, use_container_width=True)

    st.markdown("---")
    
    st.subheader("🎯 Sugestão de Aporte Otimizado")
    st.write("Altere a quantidade de cotas diretamente na tabela. Os valores estão protegidos ao confirmar o aporte.")

    col1_tab, col2_tab = st.columns(2)
    with col1_tab:
        valor_aporte = st.number_input("Valor total disponível para aporte (R$)", min_value=10.0, step=50.0, value=500.0)
    with col2_tab:
        qtd_ativos_sugeridos = st.number_input("Quantas empresas do topo quer comprar?", min_value=1, max_value=len(df_completo), value=3)

    config_id = f"{valor_aporte}_{qtd_ativos_sugeridos}"
    
    if "last_config_id" not in st.session_state or st.session_state.last_config_id != config_id:
        st.session_state.last_config_id = config_id
        
        df_sugeridos = df_completo.head(qtd_ativos_sugeridos).copy()
        valor_por_ativo = valor_aporte / len(df_sugeridos) if qtd_ativos_sugeridos > 0 else 0
        
        df_sugeridos['Sugerido (Cotas)'] = df_sugeridos['Preço'].apply(lambda x: max(1, int(valor_por_ativo // x)))
        st.session_state.df_aporte_atual = df_sugeridos[['Ativo', 'Preço', 'Sugerido (Cotas)']].copy()

    if "df_aporte_atual" in st.session_state and not st.session_state.df_aporte_atual.empty:
        df_renderizar = st.session_state.df_aporte_atual.copy()
        df_renderizar['Subtotal'] = round(df_renderizar['Sugerido (Cotas)'] * df_renderizar['Preço'], 2)
        
        total_simulado = df_renderizar['Subtotal'].sum()
        sobra = valor_aporte - total_simulado
        
        c1, c2 = st.columns(2)
        c1.metric("Total a Alocar", f"R$ {total_simulado:,.2f}")
        c2.metric("Sobra em Caixa", f"R$ {sobra:,.2f}")
        
        st.data_editor(
            df_renderizar[['Ativo', 'Preço', 'Sugerido (Cotas)', 'Subtotal']],
            hide_index=True,
            key="meu_data_editor",
            on_change=salvar_edicoes_editor,
            column_config={
                "Ativo": st.column_config.TextColumn("Ativo", disabled=True),
                "Preço": st.column_config.NumberColumn("Preço (R$)", format="R$ %.2f", disabled=True),
                "Sugerido (Cotas)": st.column_config.NumberColumn("Sugerido (Cotas)", min_value=0, step=1),
                "Subtotal": st.column_config.NumberColumn("Subtotal (R$)", format="R$ %.2f", disabled=True)
            }
        )
        
        aprovado_para_gravar = st.checkbox("Estou ciente e desejo gravar estes valores no CSV (destravar botão)")

        if st.button("✅ Confirmar Aporte e Atualizar CSV", disabled=not aprovado_para_gravar):
            df_base_original = pd.read_csv('carteira.csv')
            
            for _, row in st.session_state.df_aporte_atual.iterrows():
                ativo = row['Ativo']
                cotas_novas = int(row['Sugerido (Cotas)'])
                df_base_original.loc[df_base_original['Ativo'] == ativo, 'Quantidade'] += cotas_novas
            
            colunas_originais = ['Empresa', 'Ativo', 'Quantidade', 'Meta', 'Ramo', 'Grupo']
            df_base_original[colunas_originais].to_csv('carteira.csv', index=False)
            
            del st.session_state.df_aporte_atual
            del st.session_state.last_config_id
            
            st.toast("Aporte integrado com sucesso!", icon="💾")
            time.sleep(1)
            st.rerun()
            
    st.markdown("---")
    st.markdown("Desenvolvido por [Beto Schneider](https://betoschneider.com)")


def main():
    st.set_page_config(
        page_title="Balanceador B3",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    pages = [
        st.Page(page_main, title="Principal", icon="🏠", default=True),
        st.Page("pages/1_Controle.py", title="Controle", icon="⚙️")
    ]

    selected_page = st.navigation(pages, position="sidebar", expanded=True)
    selected_page.run()


if __name__ == "__main__":
    main()
