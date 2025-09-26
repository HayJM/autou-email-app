import os
import io
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from responders import suggest_reply

# Usar versão leve em produção (Render/Heroku)
if os.getenv('RENDER') or os.getenv('DYNO'):
    print("🚀 Modo produção detectado - usando NLP otimizado")
    from nlp_lite import extract_text_from_file, classify_email
else:
    print("🔬 Modo desenvolvimento - usando NLP completo")
    try:
        from nlp import extract_text_from_file, classify_email
    except ImportError:
        print("⚠️  Fallback para NLP lite")
        from nlp_lite import extract_text_from_file, classify_email


ALLOWED_EXTENSIONS = {"txt", "pdf"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024 # 10 MB


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process():
    raw_text = request.form.get('email_text', '').strip()
    uploaded_text = ''

    if 'file' in request.files:
        file = request.files['file']
        if file and file.filename:
            if not allowed_file(file.filename):
                return render_template('index.html', error=f"Formato não suportado: {file.filename}")
            
            filename = secure_filename(file.filename)
            file_bytes = file.read()
            uploaded_text = extract_text_from_file(filename, io.BytesIO(file_bytes))


    content = raw_text or uploaded_text
    if not content:
        return render_template('index.html', error='Insira o texto do e-mail ou faça upload de um arquivo .txt/.pdf')


    # Classificação
    clf_result = classify_email(content)
    category = clf_result['category'] # "Produtivo" ou "Improdutivo"
    confidence = clf_result['confidence'] # 0..1
    sub_intent = clf_result.get('sub_intent') # p.ex. "status_update", "attachment", "greetings"
    signals = clf_result.get('signals', [])


    # Geração de resposta
    reply = suggest_reply(content, category, sub_intent, backend=os.getenv('MODEL_BACKEND', 'local'))


    return render_template('index.html',
                            input_text=content,
                            category=category,
                            confidence=f"{confidence:.2%}",
                            sub_intent=sub_intent,
                            signals=signals,
                            reply=reply)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))