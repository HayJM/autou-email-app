#!/bin/bash

# Script de Deploy Automatizado - AutoU Email App
echo "🚀 Iniciando deploy da AutoU Email App..."

# Verificar se Git está inicializado
if [ ! -d ".git" ]; then
    echo "📁 Inicializando repositório Git..."
    git init
    git add .
    git commit -m "Initial commit - AutoU Email App"
fi

echo ""
echo "Escolha a plataforma de deploy:"
echo "1) Render (Recomendado - Gratuito)"
echo "2) Heroku (Clássico)"
echo "3) Docker Local"
echo "4) Railway"
echo ""
read -p "Digite sua opção (1-4): " opcao

case $opcao in
    1)
        echo ""
        echo "📋 DEPLOY NO RENDER:"
        echo "1. Acesse: https://render.com"
        echo "2. Conecte seu GitHub"
        echo "3. Selecione este repositório"
        echo "4. Configure:"
        echo "   - Build Command: pip install -r requirements.txt"
        echo "   - Start Command: gunicorn app:app"
        echo "   - Environment: Python 3"
        echo ""
        echo "✅ Deploy será automático após configuração!"
        ;;
    2)
        echo ""
        echo "🔶 DEPLOY NO HEROKU:"
        if ! command -v heroku &> /dev/null; then
            echo "❌ Heroku CLI não encontrado!"
            echo "Instale: https://devcenter.heroku.com/articles/heroku-cli"
            exit 1
        fi
        
        read -p "Nome do app Heroku: " app_name
        heroku create $app_name
        git push heroku main
        heroku open
        echo "✅ Deploy concluído!"
        ;;
    3)
        echo ""
        echo "🐳 DOCKER LOCAL:"
        docker build -t autou-email-app .
        echo "✅ Build concluído!"
        echo "Execute: docker run -p 5001:5001 autou-email-app"
        ;;
    4)
        echo ""
        echo "🚆 RAILWAY:"
        echo "1. Acesse: https://railway.app"
        echo "2. Conecte GitHub"
        echo "3. Selecione este repositório" 
        echo "4. Deploy automático!"
        ;;
    *)
        echo "❌ Opção inválida!"
        ;;
esac

echo ""
echo "📋 Checklist pós-deploy:"
echo "[ ] Aplicação acessível via URL"
echo "[ ] Upload de arquivos funcionando"
echo "[ ] Classificação de emails operacional"
echo "[ ] Respostas automáticas sendo geradas"
echo ""
echo "🎉 Deploy configurado com sucesso!"