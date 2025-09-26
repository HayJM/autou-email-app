import os
import io
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

from nlp import extract_text_from_file, classify_email
from responders import suggest_reply

# Swagger + CORS
from flasgger import Swagger
from flask_cors import CORS

ALLOWED_EXTENSIONS = {"txt", "pdf"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB

# CORS e Swagger
CORS(app)
swagger = Swagger(
    app,
    template={
        "swagger": "2.0",
        "info": {
            "title": "AutoU — Classificador de E-mails",
            "description": "API para classificar e sugerir respostas (Produtivo/Improdutivo).",
            "version": "1.0.0",
        },
        "basePath": "/",
    },
)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/process", methods=["POST"])
def process():
    raw_text = (request.form.get("email_text") or "").strip()
    uploaded_text = ""

    if "file" in request.files:
        file = request.files["file"]
        if file and file.filename:
            if not allowed_file(file.filename):
                return render_template("index.html", error=f"Formato não suportado: {file.filename}")
            filename = secure_filename(file.filename)
            file_bytes = file.read()
            uploaded_text = extract_text_from_file(filename, io.BytesIO(file_bytes))

    content = raw_text or uploaded_text
    if not content:
        return render_template(
            "index.html",
            error="Insira o texto do e-mail ou faça upload de um arquivo .txt/.pdf",
        )

    # Classificação
    clf_result = classify_email(content)
    category = clf_result["category"]              # "Produtivo" ou "Improdutivo"
    confidence = clf_result["confidence"]          # float 0..1
    sub_intent = clf_result.get("sub_intent")      # p.ex. "status_update", "attachment", "greetings"
    signals = clf_result.get("signals", [])

    # Geração de resposta
    reply = suggest_reply(content, category, sub_intent, backend=os.getenv("MODEL_BACKEND", "local"))

    return render_template(
        "index.html",
        input_text=content,
        category=category,
        confidence=f"{confidence:.2%}",
        sub_intent=sub_intent,
        signals=signals,
        reply=reply,
    )


@app.route("/api/classify", methods=["POST"])
def api_classify():
    """
    Classifica o e-mail e sugere resposta.
    ---
    consumes:
      - application/json
      - multipart/form-data
    parameters:
      - in: body
        name: payload
        required: false
        schema:
          type: object
          properties:
            text:
              type: string
              example: "Bom dia! Poderiam informar o andamento do chamado #12345? Preciso da previsão."
      - in: formData
        name: text
        type: string
        required: false
        description: Texto do e-mail (alternativa ao JSON)
      - in: formData
        name: file
        type: file
        required: false
        description: Arquivo .txt ou .pdf
    responses:
      200:
        description: Resultado da classificação
        schema:
          type: object
          properties:
            category:
              type: string
              enum: ["Produtivo", "Improdutivo"]
            confidence:
              type: number
              format: float
            sub_intent:
              type: string
              nullable: true
            signals:
              type: array
              items:
                type: string
            reply:
              type: string
      400:
        description: Requisição inválida
    """
    text = ""

    # JSON
    if request.is_json:
        payload = request.get_json(silent=True) or {}
        text = (payload.get("text") or "").strip()

    # form-data "text"
    if not text:
        text = (request.form.get("text") or "").strip()

    # form-data "file"
    if not text and "file" in request.files:
        file = request.files["file"]
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            text = extract_text_from_file(filename, io.BytesIO(file.read()))

    if not text:
        return jsonify({"error": "Forneça 'text' no JSON ou um arquivo .txt/.pdf"}), 400

    # Classificar
    clf_result = classify_email(text)
    category = clf_result["category"]
    confidence = float(clf_result["confidence"])
    sub_intent = clf_result.get("sub_intent")
    signals = clf_result.get("signals", [])

    # Resposta sugerida
    reply = suggest_reply(text, category, sub_intent, backend=os.getenv("MODEL_BACKEND", "local"))

    return jsonify(
        {
            "category": category,
            "confidence": confidence,
            "sub_intent": sub_intent,
            "signals": signals,
            "reply": reply,
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
