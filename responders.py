import os
import datetime as dt
import textwrap


OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')


PT_SIGNATURE = """\
Atenciosamente,\nEquipe de Suporte AutoU"""


TEMPLATES = {
    ('Produtivo', 'status_update'): textwrap.dedent('''\
        Olá {name},
        \nRecebemos sua solicitação de atualização sobre o caso {ticket}. Já estamos verificando e retornaremos um novo status até {eta}.
        \nSe tiver algum detalhe adicional (prints, horário do erro, mensagem exibida), por favor, responda a este e‑mail.
        \n{signature}
    '''),
    ('Produtivo', 'attachment'): textwrap.dedent('''\
        Olá {name},
        \nAgradecemos o envio do(s) arquivo(s). Encaminhamos para análise e retornaremos com os próximos passos até {eta}.
        \nCaso falte algum documento, avisaremos por aqui.
        \n{signature}
    '''),
    ('Produtivo', None): textwrap.dedent('''\
        Olá {name},
        \nObrigado pelo contato. Estamos tratando sua solicitação e retornaremos até {eta}.
        \nSe possível, compartilhe mais contexto (ex.: número do chamado, prints, horário do problema).
        \n{signature}
    '''),
    ('Improdutivo', 'greetings'): textwrap.dedent('''\
        Olá {name},
        \nAgradecemos a mensagem! Desejamos o mesmo a você. Caso precise de suporte, estamos à disposição.
        \n{signature}
    '''),
    ('Improdutivo', None): textwrap.dedent('''\
        Olá {name},
        \nObrigado pela mensagem. Se houver alguma demanda específica, é só nos avisar por aqui.
        \n{signature}
    '''),
}




def _extract_name(text: str) -> str:
    # Heurística simples pelo campo de assinatura comum
    for key in ["att.", "atenciosamente", "obrigado", "obrigada", "grato", "grata"]:
        idx = text.lower().find(key)
        if idx != -1:
            tail = text[idx:].split('\n')
            if len(tail) > 1 and 1 <= len(tail[1].strip()) <= 40:
                return tail[1].strip().split('|')[0]
    return "" # deixa vazio




def _guess_ticket(text: str) -> str:
    # Procura padrões tipo #12345, CHM-123, PROTOCOLO 2024-00123 etc.
    import re
    m = re.search(r'(?:#|chm-|ticket\s*|protocolo\s*)([a-z0-9\-_/]{3,20})', text, flags=re.I)
    if m:
        return m.group(1).upper()
    return "N/A"

def _eta_business_hours(hours=8):
    # estimativa simples de SLA: próximo dia útil às 18h ou +N horas
    now = dt.datetime.now()
    eta = now + dt.timedelta(hours=hours)
    return eta.strftime('%d/%m/%Y %H:%M')

def _render_template(category, sub_intent, name, ticket):
    tpl = TEMPLATES.get((category, sub_intent)) or TEMPLATES.get((category, None))
    return tpl.format(name=name or 'tudo bem', ticket=ticket, eta=_eta_business_hours(), signature=PT_SIGNATURE)

def suggest_reply(text: str, category: str, sub_intent: str | None, backend: str = 'local') -> str:
    name = _extract_name(text)
    ticket = _guess_ticket(text)
    if backend == 'openai' and os.getenv('OPENAI_API_KEY'):
        try:
            from openai import OpenAI
            client = OpenAI()
            system = (
                "Você é um assistente de suporte de banco/fintech. Escreva respostas curtas, claras, em PT-BR, "
                "com tom profissional e empático. Se o e-mail for improdutivo, agradeça e encerre."
            )
            user = (
                f"Categoria: {category}\nSub-intenção: {sub_intent}\nTicket:{ticket}\n"
                f"Nome:{name or 'Cliente'}\n\nE-mail:\n{text[:4000]}"
            )
            msg = client.chat.completions.create(
                model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
                messages=[{"role":"system","content":system},{"role":"user","content":user}],
                temperature=0.2,
                max_tokens=220,
            )
            return msg.choices[0].message.content.strip()
        except Exception:
            pass # cai no template


    # Fallback local (ou backend='local')
    return _render_template(category, sub_intent, name, ticket)