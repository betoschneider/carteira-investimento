import yfinance as yf
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- CAMADA DE DADOS ---

@st.cache_data(ttl=3600) # Cache de 1 hora para não sobrecarregar a API e o HomeLab
def fetch_prices(ticker_list):
    # fast_info é mais leve e evita erros relacionados a dividendos, mas pode falhar com tickers fracionários
    data_list = []
    for t in ticker_list:
        try:
            # Substitua o ticker fracionário pelo cheio se der erro
            ticker_obj = yf.Ticker(t)
            
            # O fast_info evita baixar o histórico e evita o erro de '_dividends'
            info = ticker_obj.fast_info
            price = round(info['last_price'], 2)
            
            if pd.isna(price) or price <= 0:
                # Fallback se o fracionário falhar: tenta o ticker sem o 'F'
                t_base = t.replace("F.SA", ".SA")
                price = round(yf.Ticker(t_base).fast_info['last_price'], 2)
                
            data_list.append([t.replace(".SA", ""), price])
        except Exception as e:
            st.error(f"Erro ao buscar {t}: {e}")
    return data_list

def get_base_data():
    """Lê apenas a lista de ações do CSV."""
    df_base = pd.read_csv("acoes.csv")
    # Garante que pegamos apenas os tickers únicos ativos
    tickers = (df_base[df_base['status'] == 'ativo']['acao'] + '.SA').unique().tolist()
    return tickers

# --- LOGICA DE NEGOCIO ---

def main():
    st.set_page_config(
        page_title="Balanceador B3", 
        # layout="wide"
    )
    
    # 1. Busca Dados (Otimizado com Cache)
    ticker_list = get_base_data()
    
    with st.spinner('Atualizando cotações do Yahoo Finance...'):
        precos_atualizados = fetch_prices(ticker_list)
    
    df = pd.DataFrame(precos_atualizados, columns=['Ação', 'Preço'])
    data_atualizacao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # --- UI ---
    st.title("⚖️ Carteira de investimento - B3")
    st.write(f"Última consulta à API: {data_atualizacao}")

    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        cotas = st.number_input("Quantidade de cotas", min_value=1, value=1)
        
        # Lógica da Âncora pelo Preço Máximo
        p_max = df['Preço'].max()
        df['Quantidade'] = df['Preço'].apply(lambda x: round(p_max / x))
        df['Quantidade'] = df['Quantidade'] * cotas
        df['Total'] = round(df['Preço'] * df['Quantidade'], 2)
        
        soma_total = df['Total'].sum()
        df['%'] = round((df['Total'] / soma_total) * 100, 1)
        
    with col2:
        st.metric("Investimento Estimado", f"R$ {soma_total:,.2f}")
    
    # Tabela principal
    df_sorted = df.sort_values(by='Total', ascending=False)
    st.dataframe(df_sorted, hide_index=True, width='stretch', height=430)

    # --- VISUALIZAÇÃO ---
    
    tab1, tab2, tab3, tab4 = st.tabs(["TreeMap", "Equilíbrio Real", "Análise de Barras", "Dispersão de Peso"])

    with tab1:
        fig_tree = px.treemap(
            df, path=['Ação'], values='Total',
            custom_data=['Quantidade', 'Preço'],
            title="Ocupação de Patrimônio por Ativo"
        )
        fig_tree.update_traces(textinfo="label+percent entry")
        st.plotly_chart(fig_tree, use_container_width=True)

    with tab2:
        # Gráfico de Barras Horizontais com Linha de Equilíbrio
        avg_val = df['Total'].mean()
        fig_eq = go.Figure()
        fig_eq.add_trace(go.Bar(
            x=df['Total'], y=df['Ação'], orientation='h',
            text=df['Quantidade'], textposition='auto',
            marker_color='royalblue', name='Total Alocado'
        ))
        fig_eq.add_vline(x=avg_val, line_dash="dash", line_color="red", 
                         annotation_text=f"Média: R${avg_val:.2f}")
        fig_eq.update_layout(title="Desvio do Equilíbrio Perfeito", yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_eq, use_container_width=True)

    with tab3:
        fig_bar = px.bar(df_sorted, x='Ação', y='Total', color='Total', text='Quantidade')
        st.plotly_chart(fig_bar, use_container_width=True)
    with tab4:
        avg_total = df['Total'].mean()
        fig = px.scatter(
            df, 
            x='Ação', 
            y='Total', 
            size='Total', 
            color='Ação',
            title="Validação de Equilíbrio (Simetria)",
            text='Quantidade'
        )
        # Adiciona a linha de referência média para ver quem está acima/abaixo
        fig.add_hline(y=avg_total, line_dash="dot", 
                    annotation_text="Média Alvo", 
                    line_color="grey")
        fig.update_traces(textposition='top center')
        fig.update_layout(yaxis_range=[0, df['Total'].max() * 1.4]) 
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()