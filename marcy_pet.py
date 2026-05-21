import random
import queue
import threading
import tkinter as tk
from pathlib import Path

import pygetwindow as gw
from PIL import Image, ImageTk

import marcy_ai


LARGURA_JANELA = 120
ALTURA_JANELA = 110
TAMANHO_SPRITE = 50
INTERVALO_ATUALIZACAO = 150
CHANCE_DE_FALA = 0.1


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
        self.label.place(x=4, y=72, width=LARGURA_JANELA - 8, height=34)

        self.estado = "idle"
        self.x = 100
        self.y = 100
        self.dx = 1
        self.dy = 1
        self.frame_animacao = 0
        self.respondendo = False
        self.fila_respostas = queue.Queue()

        self.imagens = {}
        self.carregar_imagens()

        self.sprite = None
        self.texto_placeholder = None
        self.imagem_atual = self.imagens.get("idle_1")

        if self.imagem_atual:
            self.sprite = self.canvas.create_image(
                LARGURA_JANELA // 2,
                36,
                image=self.imagem_atual
            )
        else:
            self.texto_placeholder = self.canvas.create_text(
                LARGURA_JANELA // 2,
                36,
                text="Marcy",
                fill="black",
                font=("Arial", 14, "bold")
            )

        self.root.after(INTERVALO_ATUALIZACAO, self.atualizar)

    def carregar_imagens(self):
        pasta_base = Path(__file__).resolve().parent
        sprites = {
            "idle_1": pasta_base / "sprites" / "idle" / "idle_1.png",
            "idle_2": pasta_base / "sprites" / "idle" / "idle_2.png",
            "walk_1": pasta_base / "sprites" / "walk" / "walk_1.png",
            "walk_2": pasta_base / "sprites" / "walk" / "walk_2.png",
        }

        for nome, caminho in sprites.items():
            try:
                imagem = Image.open(caminho).resize((TAMANHO_SPRITE, TAMANHO_SPRITE))
                self.imagens[nome] = ImageTk.PhotoImage(imagem)
            except Exception:
                print(f"sprite nao encontrado: {caminho}")

    def atualizar(self):
        self.mover()
        self.animar()
        self.processar_respostas()
        self.reagir()
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
        frames = {
            "idle": ["idle_1", "idle_2"],
            "walk": ["walk_1", "walk_2"],
        }

        nomes_frames = frames.get(self.estado, frames["idle"])
        nome_frame = nomes_frames[self.frame_animacao % len(nomes_frames)]
        self.frame_animacao += 1
        self.imagem_atual = self.imagens.get(nome_frame)

        if self.imagem_atual and self.sprite:
            self.canvas.itemconfig(self.sprite, image=self.imagem_atual)
        elif self.texto_placeholder:
            self.canvas.itemconfig(self.texto_placeholder, text="Marcy")

    def reagir(self):
        if self.respondendo or random.random() >= CHANCE_DE_FALA:
            return

        app = self.detectar_app()
        self.respondendo = True
        thread = threading.Thread(target=self.buscar_resposta, args=(app,), daemon=True)
        thread.start()

    def buscar_resposta(self, app):
        resposta = marcy_ai.responder("", app)
        self.fila_respostas.put(resposta)

    def processar_respostas(self):
        while not self.fila_respostas.empty():
            resposta = self.fila_respostas.get()
            self.mostrar_resposta(resposta)

    def mostrar_resposta(self, resposta):
        self.label.config(text=resposta)
        self.root.after(3000, self.limpar_resposta)

    def limpar_resposta(self):
        self.label.config(text="")
        self.respondendo = False

    def detectar_app(self):
        try:
            janela = gw.getActiveWindow()
        except Exception:
            return ""

        if not janela or not janela.title:
            return ""

        titulo = janela.title.lower()

        if "code" in titulo:
            return "Code"
        if "chrome" in titulo:
            return "Chrome"
        if "spotify" in titulo:
            return "Spotify"
        if "discord" in titulo:
            return "Discord"
        if "steam" in titulo:
            return "Steam"
        if "youtube" in titulo:
            return "YouTube"
        if "github" in titulo:
            return "GitHub"

        return ""


if __name__ == "__main__":
    pet = MarcyPet()
    pet.root.mainloop()
