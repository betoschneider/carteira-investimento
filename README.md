# 💼 Carteira de Investimento - B3

Uma aplicação web com Streamlit para analisar e sugerir aportes em uma carteira de ações da B3.

## 📋 Descrição

O projeto lê uma base local em `carteira.csv`, atualiza preços dos ativos via Yahoo Finance e exibe uma visão financeira atualizada da carteira. Ele também sugere aportes otimizados para os ativos que estão fora da meta definida e permite salvar as quantidades sugeridas diretamente no arquivo local.

## ✨ Funcionalidades atuais

- **Leitura local da carteira** a partir de `carteira.csv`
- **Atualização de preços em tempo real** via `yfinance`
- **Cálculo de patrimônio atual** e percentual de cada ativo
- **Cálculo de desvio** entre `% Atual` e `% Meta`
- **Gráfico de desvio** por ativo para visualizar quais estão acima ou abaixo da meta
- **Sugestão de aporte otimizado** para os ativos com maior necessidade de compra
- **Edição interativa das cotas sugeridas** diretamente na tabela com `st.data_editor`
- **Confirmação de aporte** que atualiza `carteira.csv` com as novas quantidades
- **Persistência local** do estoque de ativos via atualização do CSV

## 📄 Estrutura de dados esperada

O arquivo `carteira.csv` deve conter pelo menos as colunas:

- `Empresa`
- `Ativo`
- `Quantidade`
- `Meta`
- `Ramo`
- `Grupo`

Exemplo de cabeçalho:

```csv
Empresa,Ativo,Quantidade,Meta,Ramo,Grupo
Petrobras,PETR4,100,10,Óleo e Gás,Setor 1
Vale,VALE3,50,12,Mineração,Setor 2
```

## 🚀 Como usar

### Instalação local

```bash
git clone <repositório>
cd carteira-investimento
uv sync
uv run streamlit run main.py
```

A aplicação abrirá em seu navegador em `http://localhost:8501`.

### Com Docker

```bash
docker-compose up --build
```

A aplicação ficará disponível em `http://localhost:8501`.

> Se usar Docker, é recomendável montar `carteira.csv` como volume para manter os dados entre reinicializações do container.

## 📊 Como funciona

1. O app lê `carteira.csv` e monta a base inicial de ativos.
2. Busca preços de cada ticker na B3 usando `yfinance`.
3. Calcula o valor atual de cada ativo e o total da carteira.
4. Calcula a porcentagem atual de cada ativo e o desvio em relação à meta definida.
5. Exibe tabela e gráfico de desvio para auxiliar a decisão de aporte.
6. Permite inserir um valor disponível para aporte e escolher quantos ativos do topo deseja comprar.
7. Gera sugestões de cotas para os ativos selecionados e mostra subtotal e sobra.
8. Permite editar as cotas sugeridas e, ao confirmar, atualiza `carteira.csv`.

## 🧠 Detalhes do aporte otimizado

- O aporte é distribuído entre os ativos com maior desvio negativo em relação à meta.
- O usuário escolhe quantos ativos do topo serão considerados na sugestão.
- As cotas sugeridas são calculadas com base no preço atual e no valor disponível.
- O usuário pode ajustar manualmente as cotas no editor antes de confirmar.
- O botão `Confirmar Aporte e Atualizar CSV` grava as quantidades diretamente em `carteira.csv`.

## 🛠️ Tecnologias utilizadas

- Streamlit
- Pandas
- Plotly
- yfinance
- python-dotenv
- Python 3.12+

## 📋 Requisitos

- Python >= 3.12
- uv
- pandas
- plotly
- streamlit
- yfinance
- python-dotenv

## 📁 Estrutura do projeto

```
carteira-investimento/
├── main.py              # Aplicação Streamlit principal
├── carteira.csv         # Dados da carteira local
├── pyproject.toml       # Configuração de dependências
├── uv.lock              # Lock file das dependências uv
├── Dockerfile           # Imagem Docker do app
├── docker-compose.yml   # Orquestração Docker
└── README.md            # Documentação do projeto
```

## 💡 Observações

- A aplicação depende de `carteira.csv` local. Se o arquivo não existir ou estiver fora de formato, o app não funcionará.
- O botão de confirmação atualiza as quantidades no CSV local, fornecendo persistência entre execuções.
- O código usa `st.data_editor` para permitir ajustes finos antes de gravar o aporte.

## 👤 Autor

Desenvolvido por Beto Schneider
