import math
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
ALTURA_JANELA = 210
TAMANHO_SPRITE = 50
INTERVALO_ATUALIZACAO = 150
CHANCE_DE_FALA = 0.1
INTERVALO_FALA_ESPONTANEA = 45
ATRASO_PRIMEIRA_FALA = 20
TEXTO_PLACEHOLDER = "fale com a Marcy..."
VELOCIDADE_MINIMA = 1.0
VELOCIDADE_MAXIMA = 2.5
INTERVALO_CAMINHADA_MIN = 2.0
INTERVALO_CAMINHADA_MAX = 4.0
INTERVALO_DESCANSO_MIN = 3.0
INTERVALO_DESCANSO_MAX = 6.0


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

        self.botao_confirmar = tk.Button(
            self.root,
            text="Confirmar",
            bg="#4EA8DE",
            fg="white",
            bd=0,
            relief="flat",
            activebackground="#3C8EC4",
            activeforeground="white",
            command=lambda: self.confirmar_acao_pendente(True),
        )
        self.botao_cancelar = tk.Button(
            self.root,
            text="Cancelar",
            bg="#F0F0F0",
            fg="#2A2A2A",
            bd=0,
            relief="flat",
            activebackground="#E0E0E0",
            activeforeground="#2A2A2A",
            command=lambda: self.confirmar_acao_pendente(False),
        )
        self.botao_confirmar.place(x=8, y=170, width=118, height=28)
        self.botao_cancelar.place(x=134, y=170, width=118, height=28)
        self.atualizar_botoes_confirmacao()

        self.estado = "idle"
        self.x = 100
        self.y = 100
        self.dx = 0
        self.dy = 0
        self.velocidade = 0
        self.movimento_ativo = False
        self.proximo_tempo_mudanca = time.monotonic() + random.uniform(INTERVALO_DESCANSO_MIN, INTERVALO_DESCANSO_MAX)
        self.frame_animacao = 0
        self.respondendo = False
        self.fila_respostas = queue.Queue()
        self.app_atual = ""
        self.automacoes = AutomacoesMarcy()
        self.limpar_resposta_id = None
        self.proxima_fala_espontanea = time.monotonic() + ATRASO_PRIMEIRA_FALA

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
        self.atualizar_movimento()
        self.animar()
        self.processar_automacoes()
        self.processar_respostas()
        self.atualizar_botoes_confirmacao()
        self.reagir(self.app_atual)
        self.root.after(INTERVALO_ATUALIZACAO, self.atualizar)

    def atualizar_movimento(self):
        agora = time.monotonic()

        if agora >= self.proximo_tempo_mudanca:
            self.movimento_ativo = not self.movimento_ativo
            self.proximo_tempo_mudanca = agora + (
                random.uniform(INTERVALO_CAMINHADA_MIN, INTERVALO_CAMINHADA_MAX)
                if self.movimento_ativo
                else random.uniform(INTERVALO_DESCANSO_MIN, INTERVALO_DESCANSO_MAX)
            )

            if self.movimento_ativo:
                angulo = random.uniform(0, 2 * 3.141592653589793)
                self.dx = math.cos(angulo)
                self.dy = math.sin(angulo)
                self.velocidade = random.uniform(VELOCIDADE_MINIMA, VELOCIDADE_MAXIMA)
            else:
                self.dx = 0
                self.dy = 0
                self.velocidade = 0

        if self.movimento_ativo:
            largura_tela = self.root.winfo_screenwidth()
            altura_tela = self.root.winfo_screenheight()

            self.x += self.dx * self.velocidade
            self.y += self.dy * self.velocidade

            if self.x <= 0 or self.x >= largura_tela - LARGURA_JANELA:
                self.dx = -self.dx
                self.x = max(0, min(self.x, largura_tela - LARGURA_JANELA))

            if self.y <= 0 or self.y >= altura_tela - ALTURA_JANELA:
                self.dy = -self.dy
                self.y = max(0, min(self.y, altura_tela - ALTURA_JANELA))

            self.root.geometry(f"{LARGURA_JANELA}x{ALTURA_JANELA}+{int(self.x)}+{int(self.y)}")

        self.estado = "walk" if self.movimento_ativo else "idle"

    def animar(self):
        nome_frame = proximo_frame(self.estado, self.frame_animacao)
        self.frame_animacao += 1
        self.imagem_atual = self.imagens.get(nome_frame)

        if self.imagem_atual and self.sprite:
            self.canvas.itemconfig(self.sprite, image=self.imagem_atual)
        elif self.texto_placeholder:
            self.canvas.itemconfig(self.texto_placeholder, text="Marcy")

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
        try:
            resposta = marcy_ai.responder(texto, app)
        except Exception:
            resposta = "Tive um probleminha para responder agora. Tente de novo em instantes."
        self.fila_respostas.put(resposta)

    def processar_automacoes(self):
        for mensagem in self.automacoes.verificar_eventos(self.app_atual):
            self.fila_respostas.put(mensagem)

    def processar_respostas(self):
        while not self.fila_respostas.empty():
            resposta = self.fila_respostas.get()
            self.mostrar_resposta(resposta)

    def atualizar_botoes_confirmacao(self):
        pendente = self.automacoes.tem_acao_pendente()
        if pendente:
            self.botao_confirmar.place(x=8, y=170, width=118, height=28)
            self.botao_cancelar.place(x=134, y=170, width=118, height=28)
        else:
            self.botao_confirmar.place_forget()
            self.botao_cancelar.place_forget()

    def confirmar_acao_pendente(self, confirmar):
        if not self.automacoes.tem_acao_pendente():
            self.atualizar_botoes_confirmacao()
            return

        texto = "sim" if confirmar else "nao"
        resultado = self.automacoes.executar_comando(texto, self.app_atual)
        self.mostrar_resposta(resultado["mensagem"])
        self.atualizar_botoes_confirmacao()
        self.entrada.delete(0, tk.END)
        self.entrada.insert(0, TEXTO_PLACEHOLDER)
        self.entrada.config(fg="gray30")
        self.executar_acao(resultado.get("acao"))

    def enviar_comando(self, evento=None):
        texto = self.entrada.get().strip()

        if not texto or texto == TEXTO_PLACEHOLDER:
            return

        self.entrada.delete(0, tk.END)
        resultado = self.automacoes.executar_comando(texto, self.app_atual)

        if resultado["entendido"]:
            self.mostrar_resposta(resultado["mensagem"])

            if self.automacoes.tem_acao_pendente():
                self.entrada.focus_set()
                self.entrada.delete(0, tk.END)
                self.entrada.insert(0, "Responda sim ou não")
                self.entrada.config(fg="gray30")
                self.atualizar_botoes_confirmacao()
                return

            self.executar_acao(resultado.get("acao"))
            return

        self.mostrar_resposta("Deixa eu pensar rapidinho...")
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

    def mostrar_resposta(self, resposta):
        self.respondendo = True
        if self.limpar_resposta_id:
            self.root.after_cancel(self.limpar_resposta_id)

        self.label.config(text=resposta)
        self.limpar_resposta_id = self.root.after(3000, self.limpar_resposta)

    def limpar_resposta(self):
        self.label.config(text="")
        self.respondendo = False
        self.limpar_resposta_id = None


if __name__ == "__main__":
    pet = MarcyPet()
    pet.root.mainloop()
