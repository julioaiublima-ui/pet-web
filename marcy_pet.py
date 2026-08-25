import random
import os
import queue
import threading
import time
import tkinter as tk
import webbrowser
from pathlib import Path

import pyautogui
from PIL import ImageTk
from systems import ui_automation

import marcy_ai
from systems.animation_system import carregar_imagens, duracao_frame, proximo_frame
from systems.app_detection import detectar_app
from systems.mood_system import AutomacoesMarcy


LARGURA_JANELA = 340
ALTURA_JANELA = 330
TAMANHO_SPRITE = 180
INTERVALO_ATUALIZACAO = 16
VELOCIDADE_MOVIMENTO = 10
CHANCE_DE_FALA = 0.1
INTERVALO_FALA_ESPONTANEA = 45
ATRASO_PRIMEIRA_FALA = 20
TEXTO_PLACEHOLDER = "fale com a Marcy..."
USAR_JANELA_TRANSPARENTE = os.environ.get("MARCY_TRANSPARENTE", "0") == "1"
COR_FUNDO_JANELA = "systemTransparent" if USAR_JANELA_TRANSPARENTE else "#eeeeee"


def direcao_horizontal(delta_x):
    if delta_x > 0:
        return 1
    if delta_x < 0:
        return -1
    return 0


class MarcyPet:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Marcy")
        self.root.geometry(f"{LARGURA_JANELA}x{ALTURA_JANELA}")
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.attributes("-alpha", 1.0)
        self.root.attributes("-transparent", USAR_JANELA_TRANSPARENTE)
        self.root.configure(bg=COR_FUNDO_JANELA)

        self.canvas = tk.Canvas(
            self.root,
            width=LARGURA_JANELA,
            height=ALTURA_JANELA,
            bg=COR_FUNDO_JANELA,
            highlightthickness=0
        )
        self.canvas.pack()

        self.painel_chat = tk.Frame(self.root, bg="#eeeeee", bd=0, highlightthickness=0)
        self.painel_chat.place(x=12, y=214, width=LARGURA_JANELA - 24, height=94)

        self.label = tk.Label(
            self.painel_chat,
            text="",
            bg="#eeeeee",
            fg="black",
            wraplength=LARGURA_JANELA - 8,
            justify="center"
        )
        self.label.place(x=0, y=0, width=LARGURA_JANELA - 24, height=52)

        self.entrada = tk.Entry(self.painel_chat, bg="white", fg="gray30", relief="solid", bd=1)
        self.entrada.insert(0, TEXTO_PLACEHOLDER)
        self.entrada.place(x=0, y=60, width=LARGURA_JANELA - 24, height=26)
        self.entrada.bind("<Return>", self.enviar_comando)
        self.entrada.bind("<FocusIn>", self.limpar_placeholder)
        self.entrada.bind("<FocusOut>", self.restaurar_placeholder)

        self.estado = "idle"
        self.x = 100
        self.y = 100
        self.dx = 0
        self.dy = 0
        self.ultima_direcao_horizontal = 1
        self.frame_animacao = 0
        self.estado_animacao_anterior = "idle"
        self.ultimo_frame_animacao = time.monotonic()
        self.respondendo = False
        self.fila_respostas = queue.Queue()
        self.app_atual = ""
        self.automacoes = AutomacoesMarcy()
        self.limpar_resposta_id = None
        self.proxima_fala_espontanea = time.monotonic() + ATRASO_PRIMEIRA_FALA
        self.mouse_anterior = pyautogui.position()
        self.alvo_x = self.x
        self.alvo_y = self.y

        self.imagens = {}
        self.carregar_imagens()

        self.sprite = None
        self.texto_placeholder = None
        self.imagem_atual = self.imagens.get("idle_1")

        if self.imagem_atual:
            self.sprite = self.canvas.create_image(
                LARGURA_JANELA // 2,
                100,
                image=self.imagem_atual
            )
        else:
            self.texto_placeholder = self.canvas.create_text(
                LARGURA_JANELA // 2,
                100,
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
        conversa_em_foco = self.root.focus_get() == self.entrada

        if conversa_em_foco:
            self.dx = 0
            self.dy = 0
            self.estado = "idle"
            self.animar()
            self.processar_automacoes()
            self.processar_respostas()
            self.reagir(self.app_atual)
            self.root.after(INTERVALO_ATUALIZACAO, self.atualizar)
            return

        mouse_atual = pyautogui.position()
        mouse_mudou = mouse_atual != self.mouse_anterior
        self.mouse_anterior = mouse_atual
        self.definir_alvo_mouse(mouse_atual)

        if mouse_mudou or self.distancia_ate_alvo() > 0:
            self.mover()
        else:
            self.dx = 0
            self.dy = 0
            self.estado = "idle"

        self.animar()
        self.processar_automacoes()
        self.processar_respostas()
        self.reagir(self.app_atual)
        self.root.after(INTERVALO_ATUALIZACAO, self.atualizar)

    def definir_alvo_mouse(self, mouse):
        largura_tela = self.root.winfo_screenwidth()
        altura_tela = self.root.winfo_screenheight()
        self.alvo_x = max(0, min(mouse.x - LARGURA_JANELA // 2, largura_tela - LARGURA_JANELA))
        self.alvo_y = max(0, min(mouse.y - ALTURA_JANELA // 2, altura_tela - ALTURA_JANELA))

    def distancia_ate_alvo(self):
        return max(abs(self.alvo_x - self.x), abs(self.alvo_y - self.y))

    def mover(self):
        largura_tela = self.root.winfo_screenwidth()
        altura_tela = self.root.winfo_screenheight()
        delta_x = self.alvo_x - self.x
        delta_y = self.alvo_y - self.y
        distancia = max(abs(delta_x), abs(delta_y))

        if distancia <= VELOCIDADE_MOVIMENTO:
            self.x = self.alvo_x
            self.y = self.alvo_y
            self.dx = 0
            self.dy = 0
            self.estado = "idle"
        else:
            self.dx = direcao_horizontal(delta_x)
            self.dy = 1 if delta_y > 0 else -1 if delta_y < 0 else 0
            if self.dx:
                self.ultima_direcao_horizontal = self.dx
            escala = VELOCIDADE_MOVIMENTO / distancia
            self.x += delta_x * escala
            self.y += delta_y * escala
            self.estado = "walk_direita" if self.ultima_direcao_horizontal > 0 else "walk_esquerda"

        self.x = max(0, min(self.x, largura_tela - LARGURA_JANELA))
        self.y = max(0, min(self.y, altura_tela - ALTURA_JANELA))

        self.root.geometry(f"{LARGURA_JANELA}x{ALTURA_JANELA}+{int(self.x)}+{int(self.y)}")

    def animar(self):
        agora = time.monotonic()
        if self.estado != self.estado_animacao_anterior:
            self.frame_animacao = 0
            self.estado_animacao_anterior = self.estado
            self.ultimo_frame_animacao = agora
        elif agora - self.ultimo_frame_animacao < duracao_frame(self.estado, self.frame_animacao) / 1000:
            return

        nome_frame = proximo_frame(self.estado, self.frame_animacao)
        self.frame_animacao += 1
        self.ultimo_frame_animacao = agora
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

        # Ações de automação de UI opcionais (clicar, digitar, abrir app)
        ok, mensagem = ui_automation.execute_action(acao)
        if ok:
            # Mostrar feedback breve ao usuário
            self.mostrar_resposta(mensagem)
        else:
            # Se não foi executada por UI automation, mostrar razão
            self.mostrar_resposta(mensagem)

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
