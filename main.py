import yfinance as yf
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

def get_current_prices(ticker_list):
    prices = {}
    acoes = []
    for t in ticker_list:
        ticker_obj = yf.Ticker(t)
        prices[t.replace(".SA", "")] = round(ticker_obj.fast_info['last_price'], 2)
        print(t.replace(".SA", ""), ": ", round(prices[t.replace(".SA", "")], 2))
        acoes.append([t.replace(".SA", ""), round(prices[t.replace(".SA", "")], 2)])
    return acoes

def get_acoes():
    df = pd.read_csv("acoes.csv")
    # filtre o dataframe para pegar apenas as ações ativas
    df = df[df['status'] == 'ativo']
    # para cada acao, adiciona o sufixo '.SA'
    df['acao'] = df['acao'] + '.SA'
    ticker_list = df['acao'].to_list()
    
    acoes = get_current_prices(ticker_list)
    df = pd.DataFrame(acoes, columns=['acao', 'preco'])
    df['status'] = 'ativo'
    df['data'] = pd.to_datetime('now')
    
    df.to_csv("acoes.csv", index=False)
    
    return df

def main():
    df = get_acoes()
    data = df['data'].max().strftime("%d/%m/%Y %H:%M:%S")
    
    qtd_acoes = df['acao'].count()
    valor_total = df['preco'].sum()
    
    st.title("Valor do investimento")
    st.write(f"Última atualização: {data}")
    
    col1, col2 = st.columns(2)
    with col1:
        cotas = st.number_input("Quantidade de cotas", value=1)
        
        p_max = df['preco'].max()
        df['qtd'] = df.apply(lambda x: round(p_max / x['preco']), axis=1)
        df['qtd'] = df['qtd'] * cotas
        df['total'] = df['preco'] * df['qtd']
        df.sort_values(by='total', ascending=False, inplace=True)
        df = df[['acao', 'preco', 'qtd', 'total']]
        df.rename(
            columns={
                'acao': 'Ação',
                'preco': 'Preço',
                'qtd': 'Quantidade',
                'total': 'Total'
            }, inplace=True
        )
        soma_total = df['Total'].sum()
        df['%'] = round(df['Total'] / soma_total * 100, 0)
    with col2:
        st.text_input("Valor total", value=f"R$ {soma_total:.2f}", disabled=True)
        # st.write(f"Valor total: R$ {soma_total:.2f}")
    st.dataframe(df, hide_index=True, height=430)
    
    # visualização em treemap
    fig = px.treemap(
        df, 
        path=['Ação'], 
        values='Total',
        custom_data=['Quantidade', 'Preço'],
        title="Distribuição do Portfólio"
    )
    # Ajustando o que aparece ao passar o mouse (hover) e no texto
    fig.update_traces(
        textinfo="label+percent entry",
        hovertemplate="<b>%{label}</b><br>Qtd: %{customdata[0]}<br>Preço: R$ %{customdata[1]}<br>Total: R$ %{value:.2f}"
    )
    st.plotly_chart(fig, use_container_width=True)

    
    # Visualização em barras
    fig_bar = px.bar(
        df,
        x='Total',
        y='Ação',
        orientation='h',
        title="Valor Total por Ativo e Quantidade",
        text='Quantidade', # Mostra a quantidade escrita na barra
        color='Total',
        color_continuous_scale='Blues'
    )
    fig_bar.update_traces(textposition='outside')
    fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_bar, use_container_width=True)
    
    
    # Visualização em bolhas
    fig = px.scatter(
        df, 
        x='Ação', 
        y='Total', 
        size='Total', 
        color='Ação',
        title="Validação de Equilíbrio (Todas as barras devem ter altura similar)",
        text='Quantidade'
    )
    fig.update_traces(textposition='top center')
    fig.update_layout(yaxis_range=[0, df['Total'].max() * 1.2]) # Para dar respiro no topo
    st.plotly_chart(fig, use_container_width=True)

    
    # Visualização em barras horizontais com linha de equilíbrio
    # Calculando a média que o balanceamento deveria atingir
    valor_medio_alvo = df['Total'].mean()
    fig = go.Figure()
    # Barras com o valor total por ação
    fig.add_trace(go.Bar(
        x=df['Total'],
        y=df['Ação'],
        orientation='h',
        name='Valor Alocado',
        text=df['Quantidade'], # Mostra a Qtd dentro da barra
        textposition='auto',
        marker_color='royalblue'
    ))
    # Linha vertical indicando o equilíbrio perfeito (a média)
    fig.add_shape(
        type="line", line=dict(dash="dash", color="red", width=2),
        x0=valor_medio_alvo, x1=valor_medio_alvo, y0=-0.5, y1=len(df)-0.5
    )
    fig.update_layout(
        title="Equilíbrio Financeiro por Ativo (Alvo: Média)",
        xaxis_title="Total em R$",
        yaxis_title="Ações",
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
