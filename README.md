# 📧 AutoU Email App - Case Prático

## Case Prático AutoU

### Introdução

Antes de mais nada, **parabéns por ter sido seleci## 🌐 Links

- **Aplicação**: https://autou-email-app.onrender.com/
- **Repositório**: https://github.com/HayJM/autou-email-app
- **API**: https://autou-email-app.onrender.com/apidocs/

---

## 📋 Histórico de Versões

### **v2.1** *(Atual)*
- **🆕** Respostas individuais para cada e-mail em arquivos múltiplos
- **🔧** Correção crítica no processamento de múltiplos e-mails
- **🎨** Interface aprimorada com cards e botões de cópia
- **📈** Estatísticas detalhadas de processamento
- **🛠️** Preservação de formatação em arquivos TXT/PDF

### **v2.0**
- **📄** Suporte a múltiplos e-mails em um único arquivo
- **🤖** Classificação automática com sub-intenções
- **📊** Interface com barras de confiança
- **📋** Sistema de cópia de respostas

### **v1.0**
- **📧** Classificação individual de e-mails
- **💬** Sugestões de respostas básicas
- **🌐** Interface web responsiva
- **📄** Suporte a PDF e TXT

---

## 📝 Licença

Este projeto está sob a licença MIT.a) para nosso processo seletivo**. Recebemos centenas de aplicações e apenas pessoas que apresentam uma trajetória de destaque são convidadas para esta etapa! 🚀

Nesta fase, você vivenciará na prática uma **simulação simplificada de um projeto real da AutoU**.

Nosso time é formado por pessoas capazes de **resolver problemas complexos** aplicando tecnologia de maneira simples e eficiente, com **autonomia** e sempre focando em melhorar a vida do usuário. É exatamente essa capacidade que iremos avaliar neste processo seletivo.

No final do dia, **vamos avaliar sua capacidade de resolver o problema** de verdade, bem como a qualidade da solução entregue e a **experiência proporcionada para o usuário final**.

---

## 🎯 Solução Implementada

Aplicação web inteligente para classificação automática de e-mails (únicos ou múltiplos) em **Produtivo** ou **Improdutivo** com geração de respostas sugeridas e análise estatística.

![Flask](https://img.shields.io/badge/Flask-3.0.3-blue)
![Python](https://img.shields.io/badge/Python-3.12-green)
![AI](https://img.shields.io/badge/AI-Heuristic-orange)
![Status](https://img.shields.io/badge/Status-Online-brightgreen)

### **🌐 Demo Online**
**🚀 Aplicação**: https://autou-email-app.onrender.com/  
**📚 API Docs**: https://autou-email-app.onrender.com/apidocs/

---

## 🚀 Como Usar

### **Online (Recomendado)**
1. Acesse: https://autou-email-app.onrender.com/
2. Cole o texto do e-mail ou faça upload de arquivo
3. Clique em "Processar" 
4. Visualize a classificação e resposta sugerida

### **📄 Testando com Múltiplos E-mails**
A aplicação detecta automaticamente arquivos com vários e-mails:
- Formato suportado: `EMAIL 1 - PRODUTIVO`, `EMAIL 2 - IMPRODUTIVO`, etc.
- Também detecta e-mails separados por cabeçalhos `De:`, `From:`, `Assunto:`
- Cada e-mail recebe classificação e resposta sugerida individual
- Interface com cards expansíveis e botões de cópia para cada resposta
- Crie um arquivo .txt com múltiplos e-mails para testar a funcionalidade

### **🔌 API REST**
```bash
# E-mail único
curl -X POST -H "Content-Type: application/json" \
  -d '{"text":"Preciso do status do chamado #123"}' \
  https://autou-email-app.onrender.com/api/classify

# Múltiplos e-mails via arquivo
curl -X POST -F "file=@seus_emails.txt" \
  https://autou-email-app.onrender.com/api/classify
```

### **Local**
```bash
# Clone e execute
git clone https://github.com/HayJM/autou-email-app.git
cd autou-email-app
pip install -r requirements.txt
python app.py
```
Acesse: http://localhost:5000

---

## ⚡ Funcionalidades

- ✅ **Classificação IA**: Produtivo vs Improdutivo
- ✅ **Múltiplos e-mails**: Detecta e classifica vários e-mails em um arquivo
- ✅ **Respostas individuais**: Cada e-mail recebe sua própria sugestão de resposta
- ✅ **Upload de arquivos**: PDF e TXT suportados
- ✅ **API REST**: Endpoint `/api/classify` com Swagger
- ✅ **Interface moderna**: Dark mode, drag-drop, responsive
- ✅ **Respostas automáticas**: Sugestões contextuais personalizadas
- ✅ **Análise em lote**: Resumo estatístico para múltiplos e-mails
- ✅ **Cópia rápida**: Botões para copiar cada resposta individual

---

## 🏆 Critérios Atendidos

### ✅ **Funcionalidade**
- Classificação precisa de e-mails (únicos e múltiplos) ✓
- Geração de respostas adequadas para cada caso ✓
- Interface web funcional com recursos avançados ✓
- Detecção automática e separação de múltiplos e-mails ✓

### ✅ **Qualidade Técnica** 
- Código Python organizado ✓
- Uso de bibliotecas de IA ✓
- Arquitetura modular ✓

### ✅ **Deploy na Nuvem**
- Aplicação online no Render ✓
- Configuração para produção ✓
- Acesso público funcionando ✓

---

## � Funcionalidades Recentes

### **📧 Respostas Individuais para Múltiplos E-mails**
- Cada e-mail em arquivos com múltiplos casos agora recebe sua própria resposta sugerida
- Interface aprimorada com cards visuais para cada e-mail
- Botões de cópia individual para facilitar o uso das respostas
- Preservação de quebras de linha para melhor detecção de múltiplos e-mails

### **🎨 Interface Melhorada**
- Cards expansíveis para visualizar conteúdo completo
- Indicadores visuais de categoria (Produtivo/Improdutivo)
- Barras de confiança dinâmicas
- Seção de estatísticas com resumo geral

### **🔧 Correções Técnicas**
- Correção no processamento de arquivos TXT/PDF para múltiplos e-mails
- Otimização do regex de separação de e-mails
- Melhoria na função `extract_text_from_file` para preservar formatação

---

## �🌐 Links

- **Aplicação**: https://autou-email-app.onrender.com/
- **Repositório**: https://github.com/HayJM/autou-email-app
- **API**: https://autou-email-app.onrender.com/apidocs/

---

## 📁 Estrutura do Projeto

```
autou-email-app/
├── app.py                 # Aplicação Flask principal
├── nlp.py                 # Processamento de linguagem natural
├── responders.py          # Geração de respostas
├── requirements.txt       # Dependências Python
├── templates/
│   └── index.html        # Interface web moderna
├── static/
│   └── styles.css        # Estilos CSS customizados
├── Dockerfile            # Container Docker
├── Procfile              # Deploy Heroku/Render
└── README.md             # Este arquivo
```

## 🧪 Como Testar Múltiplos E-mails

Para testar a funcionalidade de múltiplos e-mails, crie um arquivo de texto com o formato:

```
EMAIL 1 - PRODUTIVO
De: cliente@empresa.com
Assunto: Problema urgente no sistema

Prezados, estamos com problema crítico no sistema...

EMAIL 2 - IMPRODUTIVO  
De: marketing@loja.com
Assunto: Promoção especial 50% OFF

Não perca nossa mega promoção...
```

### Recursos para Múltiplos E-mails:
✅ **Detecção automática**: Identifica padrões `EMAIL X` ou cabeçalhos `De:`  
✅ **Classificação individual**: Cada e-mail é analisado separadamente  
✅ **Respostas personalizadas**: Sugestão única para cada caso  
✅ **Interface intuitiva**: Cards expansíveis com botões de ação  
✅ **Estatísticas**: Resumo geral com percentuais  

### Tipos detectados automaticamente:
✅ **Produtivos**: Problemas técnicos, reuniões importantes, bugs críticos  
❌ **Improdutivos**: Spam, newsletters, felicitações

---

**Case Prático desenvolvido para o processo seletivo AutoU**  
**Demonstrando resolução de problemas com autonomia e foco no usuário** ✨