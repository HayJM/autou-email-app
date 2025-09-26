# Configuração para Render Free - Modelo Leve
import re
import os
from typing import Dict, Tuple

# Palavras-chave para classificação heurística otimizada
PRODUCTIVE_KEYWORDS = [
    'urgente', 'problema', 'erro', 'bug', 'falha', 'não funciona', 'suporte',
    'ajuda', 'dúvida', 'questão', 'technical', 'support', 'issue', 'help',
    'prazo', 'deadline', 'entrega', 'delivery', 'projeto', 'project',
    'reunião', 'meeting', 'apresentação', 'presentation', 'relatório', 'report',
    'solução', 'solution', 'resolução', 'resolution', 'documentação', 'documentation',
    'tarefa', 'task', 'atividade', 'activity', 'trabalho', 'work'
]

SOCIAL_KEYWORDS = [
    'parabéns', 'congratulations', 'feliz', 'happy', 'aniversário', 'birthday',
    'obrigado', 'thanks', 'thank you', 'festa', 'party', 'fim de semana', 'weekend',
    'férias', 'vacation', 'feriado', 'holiday', 'pessoal', 'personal',
    'família', 'family', 'casamento', 'wedding', 'bebê', 'baby',
    'saúde', 'health', 'hospital', 'médico', 'doctor', 'viagem', 'trip'
]

def classify_email_lite(text: str) -> Dict:
    """
    Classificação leve para ambientes com pouca memória (Render Free).
    """
    if not text or not text.strip():
        return {'category': 'Improdutivo', 'confidence': 0.5, 'method': 'heuristic_lite'}
    
    text_lower = text.lower()
    
    # Contar matches de palavras-chave
    productive_score = sum(1 for keyword in PRODUCTIVE_KEYWORDS if keyword in text_lower)
    social_score = sum(1 for keyword in SOCIAL_KEYWORDS if keyword in text_lower)
    
    # Análise de padrões
    has_question = '?' in text
    has_urgent_markers = any(marker in text_lower for marker in ['urgente', 'urgent', '!!!', 'asap'])
    has_greeting_only = len(text.split()) < 10 and any(greet in text_lower for greet in ['oi', 'olá', 'hi', 'hello'])
    
    # Scoring
    score = productive_score - social_score
    
    if has_urgent_markers:
        score += 3
    if has_question and productive_score > 0:
        score += 2
    if has_greeting_only:
        score -= 2
    
    # Decisão final
    if score > 0:
        category = 'Produtivo'
        confidence = min(0.9, 0.6 + (score * 0.1))
    else:
        category = 'Improdutivo'
        confidence = min(0.9, 0.6 + (abs(score) * 0.1))
    
    return {
        'category': category,
        'confidence': confidence,
        'method': 'heuristic_lite',
        'scores': {'productive': productive_score, 'social': social_score}
    }

def normalize_text(text: str) -> str:
    """Normalização básica de texto."""
    if not text:
        return ""
    # Remove quebras de linha excessivas e espaços
    text = re.sub(r'\s+', ' ', text.strip())
    return text

def extract_text_from_file(file_path: str) -> str:
    """
    Extração de texto simplificada para arquivos PDF e TXT.
    """
    try:
        if file_path.lower().endswith('.pdf'):
            # Tentar pdfminer.six primeiro
            try:
                from pdfminer.six import extract_text
                return extract_text(file_path)
            except Exception:
                # Fallback básico - ler como texto
                with open(file_path, 'rb') as f:
                    content = f.read()
                    # Tentar decodificar como texto simples
                    try:
                        return content.decode('utf-8', errors='ignore')
                    except:
                        return content.decode('latin-1', errors='ignore')
        
        elif file_path.lower().endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        else:
            # Tentar ler como texto genérico
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
    
    except Exception as e:
        print(f"Erro ao extrair texto: {e}")
        return ""

# Função principal compatível com a interface existente
def classify_email(text: str) -> Dict:
    """
    Interface principal para classificação de emails.
    Usa versão leve otimizada para Render Free.
    """
    return classify_email_lite(text)