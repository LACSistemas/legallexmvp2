# LegalLex MVP2 - Automação Jurídica

Sistema automatizado para busca e análise de publicações do Diário de Justiça Eletrônico (DJE) com funcionalidades de upload de análises inteligentes.

## 🆕 Últimas Atualizações

### Versão Atual - Melhorias de Interface e Funcionalidades
- **🎯 Logo Centralizado**: Logos agora aparecem centralizados na página de login e sidebar
- **⚡ Sistema de Busca Otimizado**: Migração para o método de busca otimizado (`djesearchapp.py`)
- **🗑️ Gerenciamento de Arquivos**: Admins podem visualizar e deletar análises enviadas
- **📝 Sistema de Logs Robusto**: Logging completo em `app.log` para debugging e monitoramento
- **🛡️ Tratamento de Erros Aprimorado**: Melhor feedback e recovery em caso de erros
- **🔧 Correções de Bugs**: Resolvido problema de compatibilidade entre módulos de busca

## 🚀 Funcionalidades

### Para Usuário Cliente (Caper)
- **⚙️ Configurar Regras**: Configure regras de busca automática
- **📋 Resultados Diários**: Visualize resultados das buscas automáticas (6:00 AM diário)
- **🔍 Análises Inteligentes**: Acesse análises jurídicas especializadas

### Para Usuário Admin (lucasaurich)
- **📤 Upload Análises**: Envie múltiplos arquivos HTML com análises jurídicas
- **🗑️ Gerenciar Análises**: Visualize e delete arquivos de análises enviados

## 🔐 Credenciais de Acesso

- **Cliente**: usuário `Caper`, senha `Caper`
- **Admin**: usuário `lucasaurich`, senha `caneta123`

## 📦 Instalação e Execução

### Método 1: Execução Direta

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
./start_production.sh
```

### Método 2: Docker (Recomendado)

```bash
# Construir e executar com Docker Compose
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar aplicação
docker-compose down
```

## ⏰ Sistema de Cronjobs

- **Execução Automática**: Todos os dias às 6:00 AM (horário de Brasília)
- **Configuração**: As regras são salvas automaticamente e executadas pelo sistema
- **Resultados**: Armazenados em `daily_results/` com data e timestamp

### Testando o Cronjob Manualmente

```bash
python cronjob_scheduler.py test
```

## 📁 Estrutura de Arquivos

```
legallexmvp2/
├── app.py                 # Aplicação principal Streamlit
├── auth.py               # Sistema de autenticação
├── djesearchapp.py       # Módulo otimizado de busca DJE
├── publiregras.py        # Módulo original de busca DJE (legado)
├── cronjob_scheduler.py  # Agendador de tarefas automáticas
├── analyses/             # Diretório para análises HTML
├── daily_results/        # Resultados das buscas automáticas
├── saved_rules.json      # Regras salvas pelos usuários
├── app.log              # Log da aplicação principal
├── cronjob.log          # Log do sistema de cronjobs
├── legallexmvplogo.png  # Logo da aplicação
├── start_production.sh   # Script de inicialização
├── Dockerfile           # Configuração Docker
├── docker-compose.yml   # Orquestração Docker
├── testme.md            # Guia completo de testes
└── requirements.txt     # Dependências Python
```

## 🌐 Acesso à Aplicação

Após executar, a aplicação estará disponível em:
- **URL**: http://localhost:8501
- **Porta**: 8501

## 📊 Funcionalidades Detalhadas

### Configuração de Regras Automáticas
- Adicione múltiplas regras de inclusão e exclusão
- Configure parâmetros como OAB, nomes de partes, tribunais, etc.
- Visualize quando será a próxima execução automática

### Upload de Análises Inteligentes
- Upload múltiplo de arquivos HTML
- **Gerenciamento de arquivos**: Visualização e exclusão de análises enviadas
- Análises ficam disponíveis instantaneamente para clientes
- Paginação automática (10 análises por página)

### Visualização de Resultados
- Resultados organizados por data
- Paginação de resultados de busca
- Filtros por tribunal, tipo de comunicação, etc.

## 🔧 Configurações de Produção

### Variáveis de Ambiente
- `TZ=America/Sao_Paulo` - Fuso horário de Brasília

### Portas
- `8501` - Aplicação Streamlit

### Volumes Persistentes
- `./analyses` - Análises HTML enviadas
- `./daily_results` - Resultados das buscas automáticas
- `./saved_rules.json` - Configurações das regras
- `./app.log` - Logs da aplicação principal
- `./cronjob.log` - Logs do sistema de cronjobs

## 🔍 Monitoramento

### Logs do Sistema
```bash
# Ver logs da aplicação principal
tail -f app.log

# Ver logs do cronjob
tail -f cronjob.log

# Ver logs do Docker
docker-compose logs -f
```

### Verificar Status
- **Cronjob**: Verifica arquivo `cronjob.log` para últimas execuções
- **Aplicação**: Acesse http://localhost:8501 para verificar se está respondendo
- **Dados**: Verifique diretórios `analyses/` e `daily_results/` para arquivos

## 🚨 Solução de Problemas

### Aplicação não inicia
1. Verifique se a porta 8501 está livre
2. Confirme que todas as dependências estão instaladas
3. Verifique logs de erro no terminal

### Cronjob não executa
1. Verifique o arquivo `cronjob.log`
2. Confirme que existem regras salvas em `saved_rules.json`
3. Teste manualmente: `python cronjob_scheduler.py test`

### Upload de análises falha
1. Verifique permissões do diretório `analyses/`
2. Confirme que os arquivos são .html válidos
3. Verifique espaço em disco disponível
4. Consulte `app.log` para detalhes do erro

### Problemas com delete de análises
1. Verifique permissões do diretório `analyses/`
2. Confirme que o usuário tem permissão de escrita
3. Consulte `app.log` para erros específicos

### Logs não aparecem
1. Verifique se o arquivo `app.log` foi criado
2. Confirme permissões de escrita no diretório
3. Reinicie a aplicação se necessário

## 📝 Notas de Desenvolvimento

- **Framework**: Streamlit para interface web
- **Agendamento**: Biblioteca `schedule` para cronjobs
- **Fuso Horário**: `pytz` para horário de Brasília
- **API DJE**: Integração com API do CNJ para buscas
- **Logging**: Sistema robusto com `logging` do Python
- **Busca Otimizada**: Sistema de exclusões e filtros pós-busca

## 🔒 Segurança

- Autenticação hardcoded conforme especificação
- Isolamento de funcionalidades por perfil de usuário
- **Logs abrangentes**: Monitoramento completo de ações e erros
- Validação de uploads (apenas arquivos .html)
- **Controle de acesso**: Apenas admins podem deletar análises
- **Tratamento seguro de erros**: Informações técnicas apenas nos logs

## 🧪 Testes

Para um guia completo de testes do sistema, consulte:
- **[testme.md](testme.md)** - Guia detalhado com todos os cenários de teste

### Testes Principais
- ✅ Autenticação e navegação
- ✅ Upload e gerenciamento de análises
- ✅ Configuração e execução de regras
- ✅ Sistema de logs e tratamento de erros
- ✅ Funcionalidades de busca otimizada