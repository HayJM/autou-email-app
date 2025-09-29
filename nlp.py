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


# Zero-shot local com transformers (otimizado para memória baixa)
_CACHE_PIPELINE = None


def _get_zero_shot_pipeline():
    global _CACHE_PIPELINE
    if _CACHE_PIPELINE is not None:
        return _CACHE_PIPELINE
    try:
        from transformers import pipeline
        import torch
        
        # Usar modelo menor e mais eficiente para deploy gratuito
        model = os.getenv('ZSC_MODEL', 'facebook/bart-large-mnli')
        
        # Configurações para otimizar memória
        _CACHE_PIPELINE = pipeline(
            'zero-shot-classification', 
            model=model,
            device=-1,  # Forçar CPU
            torch_dtype=torch.float32,  # Precisão padrão
            model_kwargs={'low_cpu_mem_usage': True}
        )
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

    # Verificar se está em ambiente com pouca memória (Render Free)
    if os.getenv('RENDER') or len(text) > 1000:
        print("Usando classificação heurística (ambiente otimizado)")
        category, conf = heuristic_classifier(pre)
        return {
            'category': category,
            'confidence': conf,
            'method': 'heuristic'
        }

    # Tenta zero-shot com configurações otimizadas
    zsc = _get_zero_shot_pipeline()
    labels = ["technical support", "social conversation"]  # Labels em inglês para BART
    if zsc is not None:
        try:
            # Truncar texto para economizar memória
            text_truncated = raw[:300]
            res = zsc(text_truncated, candidate_labels=labels)
            if isinstance(res, list):
                res = res[0]
            scores = dict(zip(res["labels"], res["scores"]))
            top_label = max(scores, key=scores.get)
            conf = float(scores[top_label])
            # Mapear de volta para os labels originais
            category = "Produtivo" if top_label == "technical support" else "Improdutivo"
        except Exception as e:
            print(f"Fallback para heurística: {e}")
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


def split_emails(text: str) -> List[Dict[str, str]]:
    """
    Detecta e separa múltiplos e-mails em um texto
    """
    emails = []
    
    # Padrões para detectar início de e-mail
    email_patterns = [
        r'EMAIL \d+[\s\-]*(?:PRODUTIVO|IMPRODUTIVO)?',  # EMAIL 1 - PRODUTIVO
        r'De:\s*\w+',  # De: usuario@email.com
        r'From:\s*\w+',  # From: user@email.com
        r'Assunto:|Subject:',  # Assunto: ou Subject:
        r'Para:|To:',  # Para: ou To:
        r'(?:^|\n)\s*(?:Prezados?|Olá|Caro|Dear|Hi)',  # Saudações no início
    ]
    
    # Primeiro, tenta detectar e-mails marcados explicitamente (EMAIL 1, EMAIL 2, etc.)
    explicit_pattern = r'EMAIL\s+(\d+)[\s\-]*([^\n]*?)\n([\s\S]*?)(?=EMAIL\s+\d+|$)'
    explicit_matches = re.finditer(explicit_pattern, text, re.IGNORECASE | re.MULTILINE)
    
    for match in explicit_matches:
        email_num = match.group(1)
        email_header = match.group(2).strip()
        email_content = match.group(3).strip()
        
        # Detectar categoria do cabeçalho
        category_hint = None
        if 'produtivo' in email_header.lower():
            category_hint = 'Produtivo'
        elif 'improdutivo' in email_header.lower():
            category_hint = 'Improdutivo'
            
        emails.append({
            'id': f'Email {email_num}',
            'header': email_header,
            'content': email_content,
            'category_hint': category_hint
        })
    
    # Se não encontrou e-mails explícitos, tenta detectar por padrões de cabeçalho
    if not emails:
        # Divide por linhas que começam com "De:", "From:", etc.
        sections = re.split(r'\n(?=(?:De:|From:|Para:|To:|Assunto:|Subject:))', text)
        
        for i, section in enumerate(sections, 1):
            section = section.strip()
            if len(section) > 20:  # Evita seções muito pequenas
                emails.append({
                    'id': f'Email {i}',
                    'header': '',
                    'content': section,
                    'category_hint': None
                })
    
    # Se ainda não encontrou nada, considera como um único e-mail
    if not emails:
        emails.append({
            'id': 'Email único',
            'header': '',
            'content': text.strip(),
            'category_hint': None
        })
    
    return emails


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


def classify_multiple_emails(text: str) -> List[Dict]:
    """
    Classifica múltiplos e-mails encontrados no texto
    """
    emails = split_emails(text)
    results = []
    
    for email_data in emails:
        content = email_data['content']
        if len(content.strip()) < 10:  # Pula conteúdo muito pequeno
            continue
            
        # Classifica o e-mail individual
        classification = classify_email(content)
        
        # Adiciona informações extras
        result = {
            'id': email_data['id'],
            'header': email_data['header'],
            'content_preview': content[:150] + '...' if len(content) > 150 else content,
            'content_full': content,
            'category': classification['category'],
            'confidence': classification['confidence'],
            'sub_intent': classification.get('sub_intent'),
            'signals': classification.get('signals', []),
            'category_hint': email_data['category_hint']
        }
        
        results.append(result)
    
    return results