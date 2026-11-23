import os
import threading
import time
from datetime import date, datetime, timedelta

import requests
import telebot
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
API = "http://127.0.0.1:8000"
LIMITE_ESTOQUE_BAIXO = 30
        
LIMITE_ESTOQUE_BAIXO = 30
NOMES_TIPO = {"entrada": "Entrada", "saida": "Saída"}

bot = telebot.TeleBot(TOKEN)
 
chats_alerta = set()
ja_alertados = set()
INTERVALO = 60  # segundos

#verificar o estoque a cada 60 segundos
def verificar_estoque():
    while True:
        try:
            meds = requests.get(f"{API}/medicamentos/alerta-estoque-baixo").json()
            if chats_alerta:
                novos = [m for m in meds if m["id"] not in ja_alertados]
                if novos:
                    linhas = [f"{m['nome']}: {m['estoque_atual']} un." for m in novos]
                    texto = "⚠️ Alerta de estoque baixo:\n" + "\n".join(linhas)
                    for chat_id in chats_alerta:
                        bot.send_message(chat_id, texto)
                ja_alertados.clear()
                ja_alertados.update(m["id"] for m in meds)
        except Exception as e:
            print("Erro ao verificar estoque:", e)
        time.sleep(INTERVALO)

# Função para extrair mensagem de erro da API
def erro_api(resp):
    try:
        return resp.json().get("detail", "Erro desconhecido")
    except Exception:
        return "Erro desconhecido"

# Função para lidar com o comando /start e /ajuda
@bot.message_handler(commands=["start", "ajuda"])
def ajuda(msg):
    chats_alerta.add(msg.chat.id)
    bot.reply_to(msg, (
        "Comandos disponíveis:\n"
        "/estoque - lista todos os medicamentos\n"
        "/alerta - medicamentos com estoque baixo\n"
        "/entrada <id> <qtd> - registra entrada\n"
        "/entradas - últimas entradas\n"
        "/saida <id> <qtd> - registra saída\n"
        "/saidas - últimas saídas\n"
        "/validade - medicamentos vencidos ou perto de vencer\n"
    ))

# Função para lidar com o comando /estoque
@bot.message_handler(commands=["estoque"])
def estoque(msg):
    resp = requests.get(f"{API}/medicamentos/")
    meds = resp.json()
    if not meds:
        bot.reply_to(msg, "Nenhum medicamento cadastrado.")
        return
    linhas = [f"{m['id']} - {m['nome']}: {m['estoque_atual']} un." for m in meds]
    bot.reply_to(msg, "Estoque atual:\n" + "\n".join(linhas))

# Função para lidar com o comando /alerta
@bot.message_handler(commands=["alerta"])
def alerta(msg):
    resp = requests.get(f"{API}/medicamentos/alerta-estoque-baixo")
    meds = resp.json()
    if not meds:
        bot.reply_to(msg, "Nenhum medicamento com estoque baixo.")
        return
    linhas = [f"⚠️ {m['nome']}: {m['estoque_atual']} un." for m in meds]
    bot.reply_to(msg, "Estoque baixo:\n" + "\n".join(linhas))

# Função para listar movimentações (entradas ou saídas)
def listar_movimentacoes(msg, tipo):
    movs = requests.get(f"{API}/movimentacoes/").json()
    meds = requests.get(f"{API}/medicamentos/").json()
    nomes = {m["id"]: m["nome"] for m in meds}

    filtradas = [m for m in movs if m["tipo"] == tipo][-10:][::-1]
    if not filtradas:
        bot.reply_to(msg, f"Nenhuma {NOMES_TIPO[tipo].lower()} registrada ainda.")
        return

    linhas = []
    for m in filtradas:
        data = datetime.fromisoformat(m["data"]) - timedelta(hours=3)
        nome = nomes.get(m["medicamento_id"], "Medicamento removido")
        linhas.append(f"{data.strftime('%d/%m %H:%M')} - {nome}: {m['quantidade']} un. ({m['responsavel']})")

    titulo = "Últimas entradas" if tipo == "entrada" else "Últimas saídas"
    bot.reply_to(msg, f"{titulo}:\n" + "\n".join(linhas))
    
# Função para registrar entrada ou saída
def registrar(msg, tipo):
    partes = msg.text.split()

    if len(partes) != 3 or not partes[1].isdigit() or not partes[2].isdigit():
        bot.reply_to(msg, f"Uso correto: /{tipo} <id> <quantidade>")
        return

    med_id = int(partes[1])
    quantidade = int(partes[2])

    dados = {
        "medicamento_id": med_id,
        "quantidade": quantidade,
        "tipo": tipo,
        "origem": f"Bot Telegram ({msg.from_user.first_name})",
    }
    resp = requests.post(f"{API}/movimentacoes/", json=dados)

    if resp.status_code != 200:
        bot.reply_to(msg, f"❌ {erro_api(resp)}")
        return

    med = requests.get(f"{API}/medicamentos/{med_id}").json()

    texto = (
        f"✅ {NOMES_TIPO[tipo]} registrada com sucesso.\n"
        f"Medicamento: {med['nome']}\n"
        f"Quantidade: {quantidade} un.\n"
        f"Estoque atual: {med['estoque_atual']} un."
    )
    if med["estoque_atual"] < LIMITE_ESTOQUE_BAIXO:
        texto += "\n⚠️ Atenção: estoque baixo!"

    bot.reply_to(msg, texto)

# Funções para lidar com os comandos de entrada e saída
@bot.message_handler(commands=["entrada"])
def entrada(msg):
    registrar(msg, "entrada")

# Funções para listar entradas e saídas
@bot.message_handler(commands=["saida"])
def saida(msg):
    registrar(msg, "saida")

#  Funções para listar entradas e saídas
@bot.message_handler(commands=["entradas"])
def entradas(msg):
    listar_movimentacoes(msg, "entrada")

# Funções para listar entradas e saídas
@bot.message_handler(commands=["saidas"])
def saidas(msg):
    listar_movimentacoes(msg, "saida")

# Função para lidar com o comando /validade
ja_alertados_val = set()

# Função para gerar texto de validade
def texto_validade(m):
    v = date.fromisoformat(m["validade"])
    dias = (v - date.today()).days
    if dias < 0:
        return f"{m['nome']}: VENCIDO há {-dias} dia(s)"
    if dias == 0:
        return f"{m['nome']}: vence HOJE"
    return f"{m['nome']}: vence em {dias} dia(s) ({v.strftime('%d/%m/%Y')})"

# Função para lidar com o comando /validade
@bot.message_handler(commands=["validade"])
def validade(msg):
    meds = requests.get(f"{API}/medicamentos/alerta-validade").json()
    if not meds:
        bot.reply_to(msg, "Nenhum medicamento vencido ou perto de vencer.")
        return
    bot.reply_to(msg, "⏰ Validade:\n" + "\n".join(texto_validade(m) for m in meds))

# Função para verificar validade periodicamente
def verificar_validade():
    while True:
        try:
            meds = requests.get(f"{API}/medicamentos/alerta-validade").json()
            if chats_alerta:
                novos = [m for m in meds if m["id"] not in ja_alertados_val]
                if novos:
                    texto = "⏰ Alerta de validade:\n" + "\n".join(texto_validade(m) for m in novos)
                    for chat_id in chats_alerta:
                        bot.send_message(chat_id, texto)
                ja_alertados_val.clear()
                ja_alertados_val.update(m["id"] for m in meds)
        except Exception as e:
            print("Erro ao verificar validade:", e)
        time.sleep(INTERVALO)

# Inicia as threads de verificação de estoque e validade
threading.Thread(target=verificar_estoque, daemon=True).start()
threading.Thread(target=verificar_validade, daemon=True).start()
bot.infinity_polling()