# 🚀 Guia de Produção - LegalLex MVP2

## Como Colocar em Produção no VPS Hostinger com EasyPanel

Este guia irá te ensinar passo-a-passo como fazer o deploy da sua aplicação LegalLex MVP2 em um VPS da Hostinger usando o EasyPanel, de forma simples e segura.

---

## 📋 Pré-requisitos

Antes de começar, você precisa ter:

1. **VPS na Hostinger** (com datacenter no Brasil)
2. **Domínio configurado** (opcional, mas recomendado)
3. **Acesso SSH ao servidor** (usuário root ou sudo)
4. **Código da aplicação** no seu computador local

---

## 🎯 Passo 1: Configuração Inicial do VPS

### 1.1 Conectar ao VPS via SSH

```bash
ssh root@SEU_IP_DO_VPS
```

Substitua `SEU_IP_DO_VPS` pelo IP fornecido pela Hostinger.

### 1.2 Atualizar o Sistema

```bash
# Atualizar pacotes
apt update && apt upgrade -y

# Instalar dependências essenciais
apt install -y curl wget git nano
```

### 1.3 Criar Usuário Não-Root (Recomendado)

```bash
# Criar usuário
adduser legallex

# Adicionar ao grupo sudo
usermod -aG sudo legallex

# Trocar para o novo usuário
su - legallex
```

---

## 🐳 Passo 2: Instalar Docker e Docker Compose

### 2.1 Instalar Docker

```bash
# Baixar e executar script oficial do Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# Reiniciar para aplicar as mudanças
sudo systemctl reboot
```

**Aguarde o servidor reiniciar e conecte novamente via SSH**

### 2.2 Verificar Instalação

```bash
# Testar Docker
docker --version
docker run hello-world

# Testar Docker Compose
docker-compose --version
```

---

## 🎛️ Passo 3: Instalar EasyPanel

### 3.1 Instalação Automática

```bash
# Baixar e instalar EasyPanel
curl -sSL https://get.easypanel.io | sh
```

### 3.2 Configuração Inicial

1. Após a instalação, acesse: `http://SEU_IP_DO_VPS:3000`
2. Crie sua conta de administrador
3. Configure o domínio (se você tiver um)

---

## 📂 Passo 4: Preparar o Código no Servidor

### 4.1 Fazer Upload do Código

**Opção A: Via Git (Recomendado)**
```bash
# No servidor
cd /home/legallex
git clone https://github.com/SEU_USUARIO/legallexmvp2.git
cd legallexmvp2
```

**Opção B: Via SCP (do seu computador local)**
```bash
# Do seu computador
scp -r /caminho/para/legallexmvp2 legallex@SEU_IP_DO_VPS:/home/legallex/
```

### 4.2 Verificar Arquivos

```bash
# Listar arquivos importantes
ls -la
# Deve mostrar: app.py, Dockerfile, docker-compose.yml, requirements.txt, etc.
```

---

## ⚙️ Passo 5: Configurar Aplicação no EasyPanel

### 5.1 Criar Nova Aplicação

1. **Acesse o EasyPanel**: `http://SEU_IP_DO_VPS:3000`
2. **Clique em "New Service"**
3. **Selecione "Source Code"**
4. **Configure:**
   - **Service Name**: `legallex-mvp2`
   - **Source**: Local (aponte para `/home/legallex/legallexmvp2`)
   - **Build Method**: Docker
   - **Port**: `8501`

### 5.2 Configurações de Domínio

1. **Vá para aba "Domains"**
2. **Adicione domínio:**
   - **Domain**: `seudominio.com` ou `SEU_IP_DO_VPS:8501`
   - **Enable HTTPS**: ✅ (se usando domínio)

### 5.3 Variáveis de Ambiente

1. **Vá para aba "Environment"**
2. **Adicione:**
   ```
   TZ=America/Sao_Paulo
   PYTHONUNBUFFERED=1
   ```

### 5.4 Volumes/Persistência

1. **Vá para aba "Mounts"**
2. **Adicione volumes:**
   - `/home/legallex/legallexmvp2/analyses` → `/app/analyses`
   - `/home/legallex/legallexmvp2/daily_results` → `/app/daily_results`
   - `/home/legallex/legallexmvp2/saved_rules.json` → `/app/saved_rules.json`

---

## 🚀 Passo 6: Deploy da Aplicação

### 6.1 Fazer o Deploy

1. **No EasyPanel, clique "Deploy"**
2. **Aguarde o build completar** (pode demorar alguns minutos)
3. **Verifique os logs** na aba "Logs"

### 6.2 Verificar Status

```bash
# No servidor, verificar containers
docker ps

# Ver logs da aplicação
docker logs legallex-mvp2
```

---

## 🌐 Passo 7: Configurar Domínio (Opcional)

### 7.1 DNS no Domínio

Na configuração DNS do seu domínio, adicione:
```
Tipo: A
Nome: @
Valor: SEU_IP_DO_VPS
TTL: 3600
```

### 7.2 SSL/HTTPS

O EasyPanel configurará automaticamente o SSL via Let's Encrypt se você:
1. Tiver um domínio válido apontando para o servidor
2. Marcar "Enable HTTPS" na configuração do domínio

---

## 🔧 Passo 8: Configurações Finais de Segurança

### 8.1 Firewall Básico

```bash
# Instalar UFW
sudo apt install ufw

# Configurar regras básicas
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Permitir SSH, HTTP, HTTPS e porta da aplicação
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8501
sudo ufw allow 3000

# Ativar firewall
sudo ufw enable
```

### 8.2 Atualizar Senhas

**IMPORTANTE**: Altere as senhas padrão no código:
```bash
# Editar arquivo de autenticação
nano auth.py

# Procurar por senhas padrão e alterá-las:
# - Senha do cliente 'Caper': 'Caper'
# - Senha do admin 'lucasaurich': 'caneta123'
```

---

## 🔍 Passo 9: Testes e Verificações

### 9.1 Testar Aplicação

1. **Acesse**: `http://SEU_DOMINIO` ou `http://SEU_IP_DO_VPS:8501`
2. **Teste login:**
   - **Cliente**: username `Caper`, password `Caper`
   - **Admin**: username `lucasaurich`, password `caneta123`
3. **Teste upload de arquivos** (admin)
4. **Teste visualização de análises** (cliente)

### 9.2 Monitorar Logs

```bash
# Logs em tempo real
docker logs -f legallex-mvp2

# Logs do sistema
journalctl -f -u docker
```

---

## 📊 Passo 10: Monitoramento e Manutenção

### 10.1 Comandos Úteis

```bash
# Parar aplicação
docker-compose down

# Iniciar aplicação
docker-compose up -d

# Rebuild após mudanças
docker-compose up -d --build

# Ver status
docker ps
docker stats

# Backup dos dados
tar -czf backup-$(date +%Y%m%d).tar.gz analyses/ daily_results/ saved_rules.json
```

### 10.2 Atualizações

```bash
# Atualizar código
git pull origin main

# Rebuild e restart
docker-compose up -d --build
```

---

## 🚨 Troubleshooting

### Problemas Comuns

**1. Aplicação não inicia:**
```bash
# Verificar logs
docker logs legallex-mvp2

# Verificar portas
netstat -tlnp | grep 8501
```

**2. Erro de permissão:**
```bash
# Corrigir permissões
sudo chown -R legallex:legallex /home/legallex/legallexmvp2
chmod +x start_production.sh
```

**3. Problemas de SSL:**
```bash
# Verificar certificado
sudo docker exec easypanel certbot certificates
```

**4. Falta de memória:**
```bash
# Verificar uso de recursos
free -h
docker stats
```

---

## 📞 Suporte

### Logs Importantes

- **Aplicação**: `/home/legallex/legallexmvp2/app.log`
- **Cronjob**: `/home/legallex/legallexmvp2/cronjob.log`
- **Docker**: `docker logs legallex-mvp2`
- **Sistema**: `journalctl -u docker`

### Comandos de Diagnóstico

```bash
# Verificar status do sistema
systemctl status docker
systemctl status easypanel

# Verificar conectividade
ping google.com
curl -I http://localhost:8501

# Verificar espaço em disco
df -h
du -sh /home/legallex/legallexmvp2
```

---

## ✅ Checklist Final

Antes de considerar o deploy completo, verifique:

- [ ] VPS atualizado e configurado
- [ ] Docker e Docker Compose funcionando
- [ ] EasyPanel instalado e acessível
- [ ] Código da aplicação no servidor
- [ ] Aplicação buildando sem erros
- [ ] Aplicação acessível via web
- [ ] Login funcionando para ambos os usuários
- [ ] Upload de arquivos funcionando
- [ ] Firewall configurado
- [ ] SSL configurado (se usando domínio)
- [ ] Senhas padrão alteradas
- [ ] Backup dos dados implementado
- [ ] Monitoramento configurado

---

## 🎉 Parabéns!

Sua aplicação LegalLex MVP2 está agora rodando em produção no seu VPS da Hostinger! 

**URLs de acesso:**
- **Aplicação**: `http://seudominio.com` ou `http://SEU_IP_DO_VPS:8501`
- **EasyPanel**: `http://SEU_IP_DO_VPS:3000`

**Credenciais de acesso:**
- **Cliente**: username `Caper`, password `Caper` (alterar!)
- **Admin**: username `lucasaurich`, password `caneta123` (alterar!)

Lembre-se de manter o sistema sempre atualizado e fazer backups regulares dos seus dados!