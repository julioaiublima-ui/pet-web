import random
import queue
import threading
import tkinter as tk
import webbrowser
from pathlib import Path

import marcy_ai
from systems.animation_system import carregar_imagens, proximo_frame
from systems.app_detection import detectar_app
from systems.mood_system import AutomacoesMarcy


LARGURA_JANELA = 260
ALTURA_JANELA = 170
TAMANHO_SPRITE = 50
INTERVALO_ATUALIZACAO = 150
CHANCE_DE_FALA = 0.1
TEXTO_PLACEHOLDER = "fale com a Marcy..."


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

        self.estado = "idle"
        self.x = 100
        self.y = 100
        self.dx = 1
        self.dy = 1
        self.frame_animacao = 0
        self.respondendo = False
        self.fila_respostas = queue.Queue()
        self.app_atual = ""
        self.automacoes = AutomacoesMarcy()
        self.limpar_resposta_id = None

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
        self.imagens = carregar_imagens(pasta_base, TAMANHO_SPRITE)

    def atualizar(self):
        self.app_atual = detectar_app()
        self.mover()
        self.animar()
        self.processar_automacoes()
        self.processar_respostas()
        self.reagir(self.app_atual)
        self.root.after(INTERVALO_ATUALIZACAO, self.atualizar)

    def mover(self):
        largura_tela = self.root.winfo_screenwidth()
        altura_tela = self.root.winfo_screenheight()

        self.x += self.dx * 10
        self.y += self.dy * 10

        if self.x <= 0 or self.x >= largura_tela - LARGURA_JANELA:
            self.dx = -self.dx

        if self.y <= 0 or self.y >= altura_tela - ALTURA_JANELA:
            self.dy = -self.dy

        self.root.geometry(f"{LARGURA_JANELA}x{ALTURA_JANELA}+{int(self.x)}+{int(self.y)}")
        self.estado = "walk" if self.dx != 0 or self.dy != 0 else "idle"

    def animar(self):
        nome_frame = proximo_frame(self.estado, self.frame_animacao)
        self.frame_animacao += 1
        self.imagem_atual = self.imagens.get(nome_frame)

        if self.imagem_atual and self.sprite:
            self.canvas.itemconfig(self.sprite, image=self.imagem_atual)
        elif self.texto_placeholder:
            self.canvas.itemconfig(self.texto_placeholder, text="Marcy")

    def reagir(self, app):
        if self.respondendo or random.random() >= CHANCE_DE_FALA:
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
