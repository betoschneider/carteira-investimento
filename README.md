# 💼 Carteira de Investimento - B3

Uma aplicação web interativa para balanceamento e análise de carteira de investimentos da bolsa brasileira (B3).

## 📋 Descrição

A aplicação "Balanceador B3" permite que você gerencie e visualize sua carteira de investimentos de forma dinâmica. Ela busca cotações em tempo real dos ativos da B3 através da API Yahoo Finance e oferece múltiplas visualizações para análise do seu portfólio.

## ✨ Recursos

- **Atualização de Cotações em Tempo Real**: Integração com Yahoo Finance para buscar preços atualizados
- **Sistema de Cotas**: Calcule a quantidade de ações a comprar com base em um valor de investimento
- **Balanceamento Automático**: Distribuição proporcional de investimentos baseada no preço máximo
- **Múltiplas Visualizações**:
  - **TreeMap**: Ocupação de patrimônio por ativo
  - **Equilíbrio Real**: Gráfico de barras com linha de equilíbrio
  - **Análise de Barras**: Visualização em barras verticais
  - **Dispersão de Peso**: Análise de distribuição de pesos (em desenvolvimento)
- **Cache de Dados**: Reduz requisições à API com cache de 1 hora
- **Cálculo de Alocação**: Percentual de cada ativo na carteira

## 🚀 Como Usar

### Com Docker (Recomendado)

1. Certifique-se de ter Docker e Docker Compose instalados
2. Clone o repositório e navegue até a pasta:
```bash
git clone <repositório>
cd carteira-investimento
```

3. Execute com Docker Compose:
```bash
docker-compose up --build
```

A aplicação estará disponível em `http://localhost:8501`

### Instalação Local

1. Clone o repositório:
```bash
git clone <repositório>
cd carteira-investimento
```

2. Instale as dependências:
```bash
uv sync
```

### Executando a Aplicação

```bash
uv run streamlit run main.py
```

A aplicação abrirá em seu navegador no endereço `http://localhost:8501`

## 📁 Estrutura do Projeto

```
carteira-investimento/
├── main.py              # Arquivo principal da aplicação Streamlit
├── acoes.csv            # Base de dados com lista de ações
├── pyproject.toml       # Configuração de dependências (Poetry/uv)
├── uv.lock              # Lock file das dependências (uv)
├── Dockerfile           # Configuração Docker da aplicação
├── docker-compose.yml   # Orquestração Docker
└── README.md            # Este arquivo
```

## 📊 Como Funciona

1. **Carregamento de Dados**: A aplicação lê o arquivo `acoes.csv` e busca os tickers ativos
2. **Busca de Preços**: Conecta à API Yahoo Finance para obter preços atualizados
3. **Cálculo de Quantidade**: Com base no número de cotas inseridas, calcula quantas ações de cada ativo devem ser compradas
4. **Análise de Carteira**: Exibe o total investido em cada ativo e seu percentual na carteira

## 🛠️ Tecnologias Utilizadas

- **Streamlit**: Framework para criação da interface web
- **Pandas**: Manipulação e análise de dados
- **Plotly**: Visualizações interativas de gráficos
- **yfinance**: Integração com dados de mercado do Yahoo Finance
- **Python**: Linguagem de programação

## 📋 Requisitos

- Python >=3.12
- numpy >=2.4.4
- pandas >=3.0.2
- plotly >=6.7.0
- streamlit >=1.56.0
- yfinance >=1.3.0

## 📝 Arquivo acoes.csv

O arquivo `acoes.csv` deve conter as seguintes colunas:
- `acao`: Código do ativo (sem o sufixo .SA)
- `status`: Status do ativo (ativo/inativo)

Exemplo:
```
acao,status
PETR4,ativo
VALE3,ativo
ITUB4,ativo
```

## 🔄 Cache de Dados

A aplicação utiliza cache de 1 hora para cotações a fim de:
- Reduzir carga na API do Yahoo Finance
- Melhorar performance da aplicação
- Evitar sobrecarga do ambiente HomeLab

## 📈 Futuras Melhorias

- [ ] Completar a aba "Dispersão de Peso"
- [ ] Adicionar gráficos de histórico
- [ ] Persistência de dados em banco de dados
- [ ] Relatórios exportáveis
- [ ] Análise de performance histórica

## 👤 Autor

Desenvolvido por Beto Schneider

## � Docker

O projeto inclui configuração Docker completa para facilitar o deployment:

### Arquivos Docker
- **Dockerfile**: Imagem baseada em Python 3.12 com uv para gerenciamento de dependências
- **docker-compose.yml**: Orquestração com persistência de dados

### Volumes
- `acoes.csv`: Arquivo de dados das ações é persistido no host
- `~/.streamlit`: Cache do Streamlit para melhor performance

### Comandos Úteis
```bash
# Construir e executar
docker-compose up --build

# Executar em background
docker-compose up -d

# Parar containers
docker-compose down

# Ver logs
docker-compose logs -f
```
