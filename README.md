# 💼 Carteira de Investimento - B3

Uma aplicação web interativa para balanceamento e análise de carteira de investimentos da bolsa brasileira (B3).

## 📋 Descrição

A aplicação "Balanceador B3" permite que você gerencie e visualize sua carteira de investimentos de forma dinâmica. Ela busca cotações em tempo real dos ativos da B3 através da API Yahoo Finance e oferece múltiplas visualizações para análise do seu portfólio.

**Fonte de Dados**: Os dados das ações são carregados automaticamente de uma planilha Google Sheets pública, permitindo atualizações em tempo real sem necessidade de modificar arquivos locais.

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

## � Configuração da Planilha Google Sheets

### 1. Criar Planilha
1. Acesse [Google Sheets](https://sheets.google.com)
2. Crie uma nova planilha em branco

### 2. Estrutura dos Dados
A planilha deve conter pelo menos as seguintes colunas:

| acao | status |
|------|--------|
| PETR4 | Ativo |
| VALE3 | Ativo |
| ITUB4 | Inativo |
| BBDC4 | Ativo |

**Regras importantes:**
- **Coluna `acao`**: Código do ativo sem o sufixo `.SA` (ex: PETR4, VALE3)
- **Coluna `status`**: Deve conter exatamente "Ativo" ou "Inativo" (case-sensitive)
- Apenas ações com status "Ativo" serão consideradas na carteira

### 3. Tornar a Planilha Pública
1. Clique em "Compartilhar" (botão azul no canto superior direito)
2. Em "Configurações de compartilhamento", selecione "Qualquer pessoa com o link pode visualizar"
3. Clique em "Copiar link"

### 4. Obter o ID da Planilha
O ID está na URL da planilha:
```
https://docs.google.com/spreadsheets/d/[SHEET_ID]/edit#gid=0
```

Copie apenas a parte `[SHEET_ID]` (string longa entre `/d/` e `/edit`).

### 5. Configurar Arquivo .env
1. Copie o arquivo `.env.example` para `.env`:
```bash
cp .env.example .env
```

2. Edite o arquivo `.env` e substitua `<YOUR_SHEET_ID>` pelo ID obtido:
```env
SHEET_ID=1ABC...xyz123
```

## �🚀 Como Usar

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

## � Variáveis de Ambiente

A aplicação utiliza variáveis de ambiente para configuração:

- **SHEET_ID**: ID da planilha Google Sheets pública

### Arquivo .env
```env
SHEET_ID=1ABC...xyz123
```

**Nota**: O arquivo `.env` não deve ser versionado no Git. Use o `.env.example` como template.

## �📁 Estrutura do Projeto

```
carteira-investimento/
├── main.py              # Arquivo principal da aplicação Streamlit
├── .env                 # Arquivo com ID da planilha Google (não versionado)
├── .env.example         # Exemplo de configuração do .env
├── pyproject.toml       # Configuração de dependências (uv)
├── uv.lock              # Lock file das dependências (uv)
├── Dockerfile           # Configuração Docker da aplicação
├── docker-compose.yml   # Orquestração Docker
└── README.md            # Este arquivo
```

## 📊 Como Funciona

1. **Carregamento de Dados**: A aplicação lê a planilha Google Sheets configurada no arquivo `.env` e busca os tickers ativos.
2. **Busca de Preços**: Conecta à API Yahoo Finance para obter preços atualizados.
3. **Cálculo de Quantidade**: Com base no número de cotas inseridas, calcula quantas ações de cada ativo devem ser compradas.
4. **Análise de Carteira**: Exibe o total investido em cada ativo e seu percentual na carteira.
5. **Atualização Automática**: As alterações na planilha são refletidas automaticamente (com cache de 1 hora).

### Persistência de Ciclo (novo)

- A aplicação agora mantém um arquivo local chamado `historico_ciclo.csv` que armazena os ativos já recebidos em cada rodada do "Sorteador de Ciclo".
- Ao confirmar uma rodada no `Sorteador de Ciclo` (aba "Sorteador de Ciclo"), os ativos escolhidos são gravados em `historico_ciclo.csv` e serão removidos de todas as visualizações e sorteios subsequentes até o fim do ciclo.
- Quando todos os ativos da carteira tiverem sido marcados no CSV, o sistema limpa automaticamente `historico_ciclo.csv` para reiniciar um novo ciclo.
- Também existe um botão manual "Reiniciar Ciclo Completo (Limpar CSV)" na própria aba, que apaga o CSV e reinicia o ciclo.

### Regras do Sorteador de Ciclo

- O sorteador escolhe até **2 ativos aleatórios** por rodada dentre os ativos que ainda não foram aportados.
- Por segurança, ao gerar a sugestão de compra, o sistema garante que cada ativo sorteado tenha **pelo menos 1 cota sugerida** (mesmo que o valor disponível seja inferior ao preço do ativo), evitando que ativos caros apareçam com 0 cotas.
- O cálculo de cotas sugeridas divide o valor da rodada entre os ativos sorteados; o subtotal e a sobra são exibidos antes da confirmação.
- Ao confirmar, os ativos são adicionados ao `historico_ciclo.csv`, a interface faz `st.rerun()` e os ativos deixam de aparecer nas abas até o próximo ciclo.

### Observações sobre persistência em contêiner/Docker

- Se executar via Docker, certifique-se de montar um volume ou diretório persistente se quiser manter `historico_ciclo.csv` entre reinicializações de container (por padrão o arquivo é criado dentro do diretório da aplicação no container).
- O arquivo `.env` é montado no container via `docker-compose.yml` para que o `SHEET_ID` seja lido corretamente.


## 🛠️ Tecnologias Utilizadas

- **Streamlit**: Framework para criação da interface web
- **Pandas**: Manipulação e análise de dados
- **Plotly**: Visualizações interativas de gráficos
- **yfinance**: Integração com dados de mercado do Yahoo Finance
- **python-dotenv**: Gerenciamento de variáveis de ambiente
- **Google Sheets API**: Acesso direto a planilhas públicas
- **Python**: Linguagem de programação

## 📋 Requisitos

- Python >=3.12
- dotenv >=0.9.9
- numpy >=2.4.4
- pandas >=3.0.2
- plotly >=6.7.0
- streamlit >=1.56.0
- yfinance >=1.3.0

## � Cache de Dados

A aplicação utiliza cache de 1 hora para cotações a fim de:
- Reduzir carga na API do Yahoo Finance
- Melhorar performance da aplicação
- Evitar sobrecarga do ambiente HomeLab

**Nota**: As alterações na planilha Google Sheets podem levar até 1 hora para serem refletidas devido ao cache implementado.

## 📈 Futuras Melhorias

- [ ] Adicionar autenticação para planilhas privadas
- [ ] Suporte a múltiplas planilhas/carteiras
- [ ] Validação automática dos dados da planilha
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
- `.env`: Arquivo de configuração com ID da planilha Google
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
