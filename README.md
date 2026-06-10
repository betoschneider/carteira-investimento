# 💼 Carteira de Investimento - B3

Uma aplicação web com Streamlit para analisar e sugerir aportes em uma carteira de ações da B3.

## 📋 Descrição

O projeto lê uma base local em `carteira.csv`, atualiza preços dos ativos via Yahoo Finance e exibe uma visão financeira atualizada da carteira. Ele também sugere aportes otimizados para os ativos que estão fora da meta definida e permite salvar as quantidades sugeridas diretamente no arquivo local.

## ✨ Funcionalidades atuais

- **Autenticação de acesso**: proteção da interface com diálogo modal e validação via token de acesso configurado no `.env`
- **Leitura local da carteira** a partir de `carteira.csv`
- **Atualização de preços em tempo real** via `yfinance`
- **Cálculo de patrimônio atual** e percentual de cada ativo
- **Cálculo de desvio** entre `% Atual` e `% Meta`
- **Gráfico de desvio** por ativo para visualizar quais estão acima ou abaixo da meta
- **Sugestão de aporte otimizado** para os ativos com maior necessidade de compra
- **Edição interativa das cotas sugeridas** diretamente na tabela com `st.data_editor`
- **Confirmação de aporte** que atualiza `carteira.csv` com as novas quantidades
- **Persistência local** do estoque de ativos via atualização do CSV
- **Proteção contra gravação acidental**: checkbox de confirmação para destravar o botão de confirmação antes de sobrescrever `carteira.csv`
- **Página de Controle (Governança)**: nova página `pages/1_Controle.py` com editor completo do CSV, validação da soma de `Meta` e botão para salvar alterações manualmente

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

1. Clone o repositório e navegue até a pasta do projeto:
   ```bash
   git clone <repositório>
   cd carteira-investimento
   ```

2. Crie e configure o arquivo `.env` a partir do modelo `.env.example`:
   ```bash
   cp .env.example .env
   ```
   Abra o arquivo `.env` e defina um valor para o token de acesso:
   ```env
   ACCESS_TOKEN=seu_token_secreto_aqui
   ```

3. Instale as dependências e execute a aplicação Streamlit:
   ```bash
   uv sync
   uv run streamlit run main.py
   ```

A aplicação abrirá em seu navegador no endereço `http://localhost:8501`.

### Com Docker

1. Crie o arquivo `.env` conforme instruído no passo anterior.
2. Inicie o container utilizando o Docker Compose:
   ```bash
   docker-compose up --build
   ```

A aplicação ficará disponível em `http://localhost:8501`.

> **Nota**: Ao rodar com Docker, o arquivo `.env` será carregado automaticamente e o arquivo `carteira.csv` é montado como volume para manter a persistência dos dados entre as execuções do container.

## 🧭 Nova Página de Governança (Controle)

Foi adicionada uma nova página para gerenciamento e auditoria dos dados em `pages/1_Controle.py`.

- **Acessar**: a página aparece no menu lateral do Streamlit como "1_Controle".
- **Funcionalidades**:
	- Carrega o `carteira.csv` e exibe um `st.data_editor` para edição direta.
	- Ordena por `Quantidade` desc por padrão.
	- Exibe a soma da coluna `Meta` como métrica; se a soma não for 100%, aparece um aviso para revisão.
	- Botão `💾 Salvar Alterações na Carteira` regrava o arquivo `carteira.csv` com as alterações feitas.

Use esta página para correções manuais, validações e auditoria antes de aplicar aportes via a página principal.

## 🔐 Autenticação

A aplicação conta com uma rotina de proteção de acesso baseada em token de segurança:

- **Funcionamento**: Caso o usuário ainda não esteja autenticado, um diálogo modal do Streamlit (`st.dialog`) será exibido por cima da aplicação, bloqueando a interação com a página principal e ocultando o menu lateral.
- **Validação com Timing Attack Mitigation**: O token inserido pelo usuário é comparado com o `ACCESS_TOKEN` configurado nas variáveis de ambiente utilizando a função `hmac.compare_digest`. Isso impede que ataques de tempo (*timing attacks*) possam ser usados para inferir o token.
- **Estado de Sessão**: Após uma validação bem-sucedida, o estado da sessão (`st.session_state.autenticado = True`) é gravado e a visualização do painel principal e do painel de controle é liberada.

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
