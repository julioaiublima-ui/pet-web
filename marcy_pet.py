import random
import queue
import threading
import time
import tkinter as tk
import webbrowser
from pathlib import Path

from PIL import ImageTk

import marcy_ai
from systems.animation_system import carregar_imagens, proximo_frame
from systems.app_detection import detectar_app
from systems.mood_system import AutomacoesMarcy


LARGURA_JANELA = 260
ALTURA_JANELA = 170
TAMANHO_SPRITE = 50
INTERVALO_ATUALIZACAO = 300  # Reduzido de 150ms para movimento mais suave
VELOCIDADE_MOVIMENTO = 0.8   # Reduzido de 2 para movimento mais lento
CHANCE_DE_FALA = 0.1
INTERVALO_FALA_ESPONTANEA = 45
ATRASO_PRIMEIRA_FALA = 20
TEXTO_PLACEHOLDER = "fale com a Marcy..."
DURACAO_CAMINHADA = (5, 10)      # Aumentado de (4,8) para caminhar por mais tempo
DURACAO_PARADA = (12, 24)        # Aumentado de (6,14) para descansar mais entre movimentos
INTERVALO_SUB_IDLE = (6, 14)     # Aumentado de (3,8) para menos mudanças de expressão


class MarcyPet:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Marcy")
        self.root.geometry(f"{LARGURA_JANELA}x{ALTURA_JANELA}")
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.attributes("-alpha", 0.9)

        self.canvas = tk.Canvas(
            self.root,
            width=LARGURA_JANELA,
            height=ALTURA_JANELA,
            bg="white",
            highlightthickness=0
        )
        self.canvas.pack()

        self.label = tk.Label(
            self.root,
            text="",
            bg="white",
            fg="black",
            wraplength=LARGURA_JANELA - 8,
            justify="center"
        )
        self.label.place(x=8, y=74, width=LARGURA_JANELA - 16, height=52)

        self.entrada = tk.Entry(self.root, bg="white", fg="gray30", relief="solid", bd=1)
        self.entrada.insert(0, TEXTO_PLACEHOLDER)
        self.entrada.place(x=8, y=136, width=LARGURA_JANELA - 16, height=24)
        self.entrada.bind("<Return>", self.enviar_comando)
        self.entrada.bind("<FocusIn>", self.limpar_placeholder)
        self.entrada.bind("<FocusOut>", self.restaurar_placeholder)

        self.estado = "idle_normal"
        self.x = 100
        self.y = 100
        self.dx = 0
        self.dy = 0
        self.frame_animacao = 0
        self.movendo = False
        self.respondendo = False
        self.fila_respostas = queue.Queue()
        self.app_atual = ""
        self.automacoes = AutomacoesMarcy()
        self.limpar_resposta_id = None
        self.proxima_fala_espontanea = time.monotonic() + ATRASO_PRIMEIRA_FALA
        self.proxima_mudanca_movimento = time.monotonic() + random.uniform(*DURACAO_PARADA)
        self.proxima_sub_idle = time.monotonic() + random.uniform(*INTERVALO_SUB_IDLE)
        self.animacao_bloqueada_ate = 0

        self.imagens = {}
        self.carregar_imagens()

        self.sprite = None
        self.texto_placeholder = None
        self.imagem_atual = self.imagens.get("idle_1")

        if self.imagem_atual:
            self.sprite = self.canvas.create_image(
                LARGURA_JANELA // 2,
                40,
                image=self.imagem_atual
            )
        else:
            self.texto_placeholder = self.canvas.create_text(
                LARGURA_JANELA // 2,
                40,
                text="Marcy",
                fill="black",
                font=("Arial", 14, "bold")
            )

        self.root.after(INTERVALO_ATUALIZACAO, self.atualizar)

    def carregar_imagens(self):
        pasta_base = Path(__file__).resolve().parent
        imagens_pil = carregar_imagens(pasta_base, TAMANHO_SPRITE)
        self.imagens = {
            nome: ImageTk.PhotoImage(imagem)
            for nome, imagem in imagens_pil.items()
        }

    def atualizar(self):
        self.app_atual = detectar_app()
        self.manter_visivel()
        self.mover()
        self.animar()
        self.processar_automacoes()
        self.processar_respostas()
        self.reagir(self.app_atual)
        self.root.after(INTERVALO_ATUALIZACAO, self.atualizar)

    def manter_visivel(self):
        self.root.attributes("-topmost", True)
        self.root.lift()

    def mover(self):
        largura_tela = self.root.winfo_screenwidth()
        altura_tela = self.root.winfo_screenheight()
        agora = time.monotonic()

        if agora >= self.proxima_mudanca_movimento and agora >= self.animacao_bloqueada_ate:
            self.alternar_movimento(agora)

        if not self.movendo:
            return

        self.x += self.dx * VELOCIDADE_MOVIMENTO
        self.y += self.dy * VELOCIDADE_MOVIMENTO

        if self.x <= 0:
            self.x = 0
            self.dx = abs(self.dx)
        elif self.x >= largura_tela - LARGURA_JANELA:
            self.x = largura_tela - LARGURA_JANELA
            self.dx = -self.dx

        if self.y <= 0:
            self.y = 0
            self.dy = abs(self.dy)
        elif self.y >= altura_tela - ALTURA_JANELA:
            self.y = altura_tela - ALTURA_JANELA
            self.dy = -self.dy

        self.root.geometry(f"{LARGURA_JANELA}x{ALTURA_JANELA}+{int(self.x)}+{int(self.y)}")

    def alternar_movimento(self, agora):
        self.movendo = not self.movendo

        if self.movendo:
            self.dx = random.choice([-1, 1])
            self.dy = random.choice([-1, 0, 1])
            self.estado = "walk"
            self.proxima_mudanca_movimento = agora + random.uniform(*DURACAO_CAMINHADA)
        else:
            self.dx = 0
            self.dy = 0
            self.estado = self.escolher_sub_idle()
            self.proxima_mudanca_movimento = agora + random.uniform(*DURACAO_PARADA)

    def animar(self):
        agora = time.monotonic()
        if not self.movendo and agora >= self.proxima_sub_idle and agora >= self.animacao_bloqueada_ate:
            self.estado = self.escolher_sub_idle()
            self.proxima_sub_idle = agora + random.uniform(*INTERVALO_SUB_IDLE)

        nome_frame = proximo_frame(self.estado, self.frame_animacao)
        self.frame_animacao += 1
        self.imagem_atual = self.imagens.get(nome_frame)

        if self.imagem_atual and self.sprite:
            self.canvas.itemconfig(self.sprite, image=self.imagem_atual)
        elif self.texto_placeholder:
            self.canvas.itemconfig(self.texto_placeholder, text="Marcy")

    def escolher_sub_idle(self):
        if self.app_atual == "Code":
            return random.choice(["idle_glasses", "idle_thinking", "idle_curious", "idle_normal"])

        return random.choice(["idle_normal", "idle_curious", "idle_smile", "idle_thinking"])

    def definir_animacao_temporaria(self, estado, duracao):
        self.estado = estado
        self.movendo = False
        self.dx = 0
        self.dy = 0
        self.animacao_bloqueada_ate = time.monotonic() + duracao

    def reagir(self, app):
        if self.respondendo:
            return

        agora = time.monotonic()
        if agora < self.proxima_fala_espontanea:
            return

        self.proxima_fala_espontanea = agora + INTERVALO_FALA_ESPONTANEA

        if random.random() >= CHANCE_DE_FALA:
            return

        self.respondendo = True
        thread = threading.Thread(target=self.buscar_resposta, args=(app,), daemon=True)
        thread.start()

    def buscar_resposta(self, app, texto=""):
        resposta = marcy_ai.responder(texto, app)
        self.fila_respostas.put(resposta)

    def processar_automacoes(self):
        for mensagem in self.automacoes.verificar_eventos(self.app_atual):
            self.fila_respostas.put(mensagem)

    def processar_respostas(self):
        while not self.fila_respostas.empty():
            resposta = self.fila_respostas.get()
            self.mostrar_resposta(resposta)

    def enviar_comando(self, evento=None):
        texto = self.entrada.get().strip()

        if not texto or texto == TEXTO_PLACEHOLDER:
            return

        self.entrada.delete(0, tk.END)
        resultado = self.automacoes.executar_comando(texto, self.app_atual)

        if resultado["entendido"]:
            self.mostrar_resposta(resultado["mensagem"])
            self.executar_acao(resultado.get("acao"))
            return

        self.definir_animacao_temporaria("thinking", 10)
        self.mostrar_resposta("Deixa eu pensar rapidinho...", estado="thinking", duracao=10)
        thread = threading.Thread(
            target=self.buscar_resposta,
            args=(self.app_atual, texto),
            daemon=True
        )
        thread.start()

    def executar_acao(self, acao):
        if not acao:
            return

        if acao.get("tipo") == "abrir_url":
            webbrowser.open(acao.get("url", ""))
            return

        if acao.get("tipo") == "fechar":
            self.root.after(800, self.root.destroy)

    def limpar_placeholder(self, evento=None):
        if self.entrada.get() == TEXTO_PLACEHOLDER:
            self.entrada.delete(0, tk.END)
            self.entrada.config(fg="black")

    def restaurar_placeholder(self, evento=None):
        if self.entrada.get().strip():
            return

        self.entrada.insert(0, TEXTO_PLACEHOLDER)
        self.entrada.config(fg="gray30")

    def mostrar_resposta(self, resposta, estado="talking", duracao=3):
        self.respondendo = True
        self.definir_animacao_temporaria(estado, duracao)
        if self.limpar_resposta_id:
            self.root.after_cancel(self.limpar_resposta_id)

        self.label.config(text=resposta)
        self.limpar_resposta_id = self.root.after(int(duracao * 1000), self.limpar_resposta)

    def limpar_resposta(self):
        self.label.config(text="")
        self.respondendo = False
        self.limpar_resposta_id = None
        self.estado = self.escolher_sub_idle()


if __name__ == "__main__":
    pet = MarcyPet()
    pet.root.mainloop()
