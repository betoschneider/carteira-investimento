import yfinance as yf
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import dotenv
import os
import time

dotenv.load_dotenv()

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
            
            time.sleep(0.2)
        except Exception as e:
            st.error(f"Erro ao buscar {t}: {e}")
    return data_list

def get_base_data(sheet_id=None):
    """Lê apenas a lista de ações do CSV."""
    if sheet_id is None:
        sheet_id = os.getenv("SHEET_ID")
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    df_base = pd.read_csv(url)
    # Garante que pegamos apenas os tickers únicos ativos
    tickers = (df_base[df_base['status'] == 'Ativo']['acao'] + '.SA').unique().tolist()
    return tickers

# --- Persistência de Ciclo (CSV) ---
CSV_HISTORICO = "historico_ciclo.csv"

def ler_ativos_investidos():
    """Lê o CSV e retorna a lista de ativos que já receberam aporte."""
    if os.path.exists(CSV_HISTORICO):
        try:
            df_hist = pd.read_csv(CSV_HISTORICO)
            if not df_hist.empty and 'Ação' in df_hist.columns:
                return df_hist['Ação'].dropna().tolist()
        except Exception as e:
            st.error(f"Erro ao ler histórico: {e}")
    return []

def salvar_ativo_investido(ativos):
    """Adiciona novos ativos ao arquivo CSV."""
    df_novos = pd.DataFrame({'Ação': ativos, 'Data': datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    if os.path.exists(CSV_HISTORICO):
        df_novos.to_csv(CSV_HISTORICO, mode='a', header=False, index=False)
    else:
        df_novos.to_csv(CSV_HISTORICO, index=False)

def limpar_historico_csv():
    """Remove o arquivo CSV para reiniciar o ciclo."""
    if os.path.exists(CSV_HISTORICO):
        os.remove(CSV_HISTORICO)

# --- LOGICA DE NEGOCIO ---

def main():
    st.set_page_config(
        page_title="Balanceador B3", 
        # layout="wide"
    )
    
    # 1. Busca Dados (Otimizado com Cache)
    sheet_id = os.getenv("SHEET_ID")
    ticker_list = get_base_data(sheet_id=sheet_id)
    
    with st.spinner('Atualizando cotações do Yahoo Finance...'):
        precos_atualizados = fetch_prices(ticker_list)

    df_completo = pd.DataFrame(precos_atualizados, columns=['Ação', 'Preço'])
    data_atualizacao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # Carrega o histórico do CSV e filtra os ativos do ciclo atual
    ativos_ja_investidos = ler_ativos_investidos()

    # df será o dataframe filtrado (apenas os que restam para o ciclo)
    df = df_completo[~df_completo['Ação'].isin(ativos_ja_investidos)].copy()

    # Se todos já foram investidos, avisa o usuário (evita dataframe vazio com erro)
    ciclo_completo_pelo_csv = df.empty and len(df_completo) > 0

    # --- UI ---
    st.title("📈 Carteira de investimento - B3")
    st.write(f"Última consulta à API: {data_atualizacao}")

    # Layout principal: se não há ativos (todos investidos), mostra aviso e preserva tabs
    col1, col2, col3 = st.columns([1, 2, 1])

    if df.empty:
        with col1:
            st.info("Nenhum ativo disponível após filtragem. Verifique a planilha ou reinicie o ciclo.")
        with col2:
            st.metric("Investimento Estimado", "R$ 0,00")
        df_sorted = df.copy()
        soma_total = 0
    else:
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
        st.dataframe(df_sorted, hide_index=True)

    # --- VISUALIZAÇÃO ---
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "TreeMap", "Equilíbrio Real", "Análise de Barras", "Dispersão de Peso", "Simulador de Aporte", "Sorteador de Ciclo"
    ])

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
    with tab5:
        st.subheader("💰 Calcular Lote por Valor de Aporte")
        st.info("Insira quanto deseja investir e o sistema calculará a quantidade de cada ativo para manter a carteira o mais equilibrada possível.")
        
        valor_aporte = st.number_input("Valor total para investir (R$)", min_value=100.0, step=100.0, value=1000.0)
        
        if valor_aporte > 0:
            # Lógica de cálculo: Valor ideal por ativo
            qtd_ativos = len(df)
            valor_alvo_por_ativo = valor_aporte / qtd_ativos
            
            df_simulacao = df[['Ação', 'Preço']].copy()
            
            # Calcula a quantidade inteira que mais se aproxima do valor alvo
            df_simulacao['Sugerido'] = df_simulacao['Preço'].apply(lambda x: round(valor_alvo_por_ativo / x))
            
            # Garante que pelo menos 1 cota seja comprada se o valor for suficiente
            df_simulacao['Sugerido'] = df_simulacao['Sugerido'].apply(lambda x: max(x, 0))
            
            df_simulacao['Subtotal'] = round(df_simulacao['Sugerido'] * df_simulacao['Preço'], 2)
            
            total_simulado = df_simulacao['Subtotal'].sum()
            diferenca = valor_aporte - total_simulado
            
            # Métricas de resumo
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Sugerido", f"R$ {total_simulado:,.2f}")
            c2.metric("Diferença (Sobras)", f"R$ {diferenca:,.2f}")
            c3.metric("Eficiência", f"{(total_simulado/valor_aporte)*100:.1f}%")
            
            # Exibição do Lote Sugerido
            st.table(df_simulacao[df_simulacao['Sugerido'] > 0].sort_values(by='Subtotal', ascending=False), hide_index=True)
    with tab6:
        st.subheader("🎲 Sorteador de Aporte (Ciclo Fechado via CSV)")
        st.info("""
        Esta simulação escolhe até **2 ativos aleatórios** por rodada. Ao confirmar, 
        eles são salvos em arquivo local e removidos de **todo o painel** até que o ciclo termine.
        """)

        lista_total = df_completo['Ação'].tolist()
        restantes_no_ciclo = df['Ação'].tolist()

        # Botão para resetar manualmente a qualquer momento
        if st.button("🔄 Reiniciar Ciclo Completo (Limpar CSV)"):
            limpar_historico_csv()
            st.session_state.ativos_sorteados_rodada = []
            st.toast("Histórico limpo! Reiniciando...", icon="🧹")
            time.sleep(0.5)
            st.rerun()

        # Exibição visual do progresso baseado no que está no CSV
        total_ativos = len(lista_total)
        investidos_qtd = len(ativos_ja_investidos)
        progresso = investidos_qtd / total_ativos if total_ativos > 0 else 0.0
        st.progress(progresso, text=f"Progresso do Ciclo: {investidos_qtd} de {total_ativos} ativos concluídos")

        # Verifica se o ciclo acabou
        if ciclo_completo_pelo_csv or len(restantes_no_ciclo) == 0:
            st.success("🎉 Todos os ativos da carteira receberam aportes! Ciclo finalizado.")
            if st.button("🚀 Iniciar Novo Ciclo"):
                limpar_historico_csv()
                st.session_state.ativos_sorteados_rodada = []
                st.rerun()
        else:
            valor_aporte = st.number_input("Valor total para esta rodada (R$)", min_value=10.0, step=50.0, value=500.0, key="val_tab6")

            # Inicializa a variável de controle de sorteio na sessão se não existir
            if 'ativos_sorteados_rodada' not in st.session_state:
                st.session_state.ativos_sorteados_rodada = []

            if st.button("🎲 Sortear Ativos") or not st.session_state.ativos_sorteados_rodada:
                import random
                qtd_a_sortear = min(2, len(restantes_no_ciclo))
                st.session_state.ativos_sorteados_rodada = random.sample(restantes_no_ciclo, qtd_a_sortear)

            if st.session_state.ativos_sorteados_rodada:
                ativos_validos = [a for a in st.session_state.ativos_sorteados_rodada if a in restantes_no_ciclo]
                
                if not ativos_validos:
                    st.session_state.ativos_sorteados_rodada = []
                    st.rerun()

                st.write(f"**Sugeridos para compra:** {', '.join(ativos_validos)}")
                
                df_rodada = df[df['Ação'].isin(ativos_validos)].copy()
                valor_por_ativo = valor_aporte / len(df_rodada)
                
                df_rodada['Sugerido (Cotas)'] = df_rodada['Preço'].apply(lambda x: int(valor_por_ativo // x))
                df_rodada['Subtotal'] = round(df_rodada['Sugerido (Cotas)'] * df_rodada['Preço'], 2)
                
                total_simulado = df_rodada['Subtotal'].sum()
                sobra = valor_aporte - total_simulado
                
                c1, c2 = st.columns(2)
                c1.metric("Total a Alocar", f"R$ {total_simulado:,.2f}")
                c2.metric("Sobra", f"R$ {sobra:,.2f}")
                
                st.table(df_rodada[['Ação', 'Preço', 'Sugerido (Cotas)', 'Subtotal']])
                
                if st.button("✅ Confirmar Aporte e Avançar"):
                    # 1. Salva no CSV os ativos desta rodada
                    salvar_ativo_investido(ativos_validos)
                    
                    # 2. Limpa o state do sorteio para a próxima rodada
                    st.session_state.ativos_sorteados_rodada = []
                    
                    # 3. Verifica se com estes, fechamos o ciclo para limpar o CSV imediatamente
                    ativos_atualizados_pos_click = ler_ativos_investidos()
                    if len(ativos_atualizados_pos_click) >= len(lista_total):
                        limpar_historico_csv()
                        st.balloons()
                    
                    st.toast("Rodada gravada no CSV com sucesso!", icon="💾")
                    time.sleep(1)
                    st.rerun()
    
    st.markdown("---")
    st.markdown(f"""
        Para editar a carteira, acesse a planilha vinculada abaixo.
        - [Planilha de Controle](https://docs.google.com/spreadsheets/d/{sheet_id}/edit?usp=sharing)
        
        As alterações são refletidas automaticamente aqui, mas podem levar até 1 hora para atualizar devido ao cache implementado para otimizar o desempenho e evitar sobrecarga na API do Yahoo Finance.
        """
    )
    st.markdown("---")
    st.markdown("Desenvolvido por [Beto Schneider](https://betoschneider.com)")

if __name__ == "__main__":
    main()