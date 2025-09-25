import re
import os
import io
from typing import Dict, List


# Stopwords básicas PT/EN (reduzidas para evitar downloads em produção)
STOPWORDS = set('''
a o os as um uma umas uns de do da das dos e é em no na nas nos para por com sem sobre entre até como que se seua seu sua suas seus eu você vocês nós eles elas de ao à às aos ou mas porém então também mais menos muito pouco tal tais foi foram ser estar estarão estará estão está estava estavam havia have has had the is are to for of in on at from with without about into over under and or not be been being this that these those a an it its it's i you we they he she them him her my your our their me us we'''.split())


# Heurística simples de sub-intenções
SUB_INTENT_PATTERNS = {
'status_update': [r'\bandamento\b', r'\batualiza', r'\bstatus\b', r'\bprogresso\b', r'\bprevis(ão|ao)\b', r'\bcaso\b'],
'attachment': [r'\banexo\b', r'\barquivo\b', r'\bdocumento\b', r'\banexei\b', r'\bsegue?\b'],
'greetings': [r'\bparabéns\b', r'\bfeliz\b', r'\bobrigad', r'\bagradec', r'\bboas festas\b', r'\bcongrat', r'\bthanks?\b'],
}


# Zero-shot local com transformers (multilíngue)
_CACHE_PIPELINE = None


def _get_zero_shot_pipeline():
    global _CACHE_PIPELINE
    if _CACHE_PIPELINE is not None:
        return _CACHE_PIPELINE
    try:
        from transformers import pipeline
        model = os.getenv('ZSC_MODEL', 'joeddav/xlm-roberta-large-xnli')
        _CACHE_PIPELINE = pipeline('zero-shot-classification', model=model)
        return _CACHE_PIPELINE
    except Exception:
        return None




def normalize_text(text: str) -> str:
    text = text.replace('\r', ' ').replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()




def preprocess(text: str) -> str:
    text = text.lower()
    # Remove caracteres especiais, mantém letras, números, espaços, @, . e -
    text = re.sub(r'[^\w\s@\.-]', ' ', text)
    # Remoção simples de stopwords
    tokens = [t for t in text.split() if t not in STOPWORDS]
    return ' '.join(tokens)




def detect_sub_intent(text: str) -> tuple[str, List[str]]:
    hits = []
    chosen = None
    for intent, patterns in SUB_INTENT_PATTERNS.items():
        for p in patterns:
            if re.search(p, text, flags=re.IGNORECASE):
                hits.append((intent, p))
    
    if hits:
        # prioriza intents por ordem definida
        order = ['status_update', 'attachment', 'greetings']
        for o in order:
            if any(h[0] == o for h in hits):
                chosen = o
                break
    
    return chosen, [f"{i}:{p}" for i,p in hits]




def classify_email(text: str) -> Dict:
    raw = normalize_text(text)
    pre = preprocess(raw)


# Tenta zero-shot
    zsc = _get_zero_shot_pipeline()
    labels = ["suporte técnico", "conversa social"]  # Labels mais específicos
    if zsc is not None:
        try:
            res = zsc(raw, candidate_labels=labels)  # Usar texto original, não preprocessado
            if isinstance(res, list):
                res = res[0]
            scores = dict(zip(res["labels"], res["scores"]))
            top_label = max(scores, key=scores.get)
            conf = float(scores[top_label])
            # Mapear de volta para os labels originais
            category = "Produtivo" if top_label == "suporte técnico" else "Improdutivo"
        except Exception:
            category, conf = heuristic_classifier(pre)
    else:
        category, conf = heuristic_classifier(pre)


    sub_intent, signals = detect_sub_intent(raw)
    # Ajuste: saudações fortes → improdutivo, a menos que haja pedido junto
    if sub_intent == 'greetings' and category == 'Produtivo' and conf < 0.8:
        category = 'Improdutivo'
        conf = min(conf, 0.65)
    return {
        'category': category,
        'confidence': conf,
        'sub_intent': sub_intent,
        'signals': signals,
    }

def heuristic_classifier(pre: str):
# Palavras indicativas
    prod = [
        'andamento','atualiza','status','prazo','previs', 'erro','bug','falha','problema',
        'suporte','duvida','acesso','liberacao','conta','fatura','boleto','chamado','protocolo', 'anexo','segue'
    ]
    impr = ['parabens','feliz','boas','agradec','obrigad','bom dia','boa tarde','boa noite','saudacoes']


    score = 0
    for p in prod:
        if p in pre:
            score += 1
    for q in impr:
        if q in pre:
            score -= 1


    if score >= 1:
        return 'Produtivo', 0.75
    elif score <= -1:
        return 'Improdutivo', 0.75
    else:
        # neutro → considerar improdutivo conservador
        return 'Improdutivo', 0.55


def extract_text_from_file(filename: str, file_stream: io.BytesIO) -> str:
    """
    Extrai texto de arquivos .txt ou .pdf
    """
    try:
        file_stream.seek(0)  # Reset stream position
        
        if filename.lower().endswith('.txt'):
            # Para arquivos .txt, tenta diferentes encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            for encoding in encodings:
                try:
                    file_stream.seek(0)
                    content = file_stream.read().decode(encoding)
                    return normalize_text(content)
                except UnicodeDecodeError:
                    continue
            # Se nenhum encoding funcionou, usa errors='ignore'
            file_stream.seek(0)
            content = file_stream.read().decode('utf-8', errors='ignore')
            return normalize_text(content)
            
        elif filename.lower().endswith('.pdf'):
            # Para arquivos .pdf, usa pdfminer
            try:
                from pdfminer.high_level import extract_text
                file_stream.seek(0)
                text = extract_text(file_stream)
                return normalize_text(text)
            except ImportError:
                # Fallback para PyPDF2 se pdfminer não estiver disponível
                try:
                    import PyPDF2
                    file_stream.seek(0)
                    pdf_reader = PyPDF2.PdfReader(file_stream)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text()
                    return normalize_text(text)
                except ImportError:
                    return "Erro: Biblioteca para leitura de PDF não encontrada"
            except Exception as e:
                return f"Erro ao processar PDF: {str(e)}"
        else:
            return "Formato de arquivo não suportado"
            
    except Exception as e:
        return f"Erro ao extrair texto: {str(e)}"