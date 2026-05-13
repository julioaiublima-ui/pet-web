import tkinter as tk
from PIL import Image, ImageTk
import random
import time
import threading
import pygetwindow as gw
import marcy_ai

class MarcyPet:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Marcy")
        self.root.geometry("100x100")
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.attributes("-alpha", 0.8)  # Transparente

        self.canvas = tk.Canvas(self.root, width=100, height=100, bg='white', highlightthickness=0)
        self.canvas.pack()

        self.label = tk.Label(self.root, text="", bg='white', fg='black')
        self.label.place(x=0, y=80)

        self.state = "idle"
        self.x = 100
        self.y = 100
        self.dx = 1
        self.dy = 1

        self.images = {}
        self.load_images()

        self.current_image = self.images.get("idle_1", None)
        if self.current_image:
            self.canvas.create_image(50, 50, image=self.current_image)

        self.root.after(1000, self.update)

    def load_images(self):
        # Placeholder: assumir imagens existem, senão usar texto
        try:
            self.images["idle_1"] = ImageTk.PhotoImage(Image.open("sprites/idle/idle_1.png").resize((50, 50)))
            self.images["idle_2"] = ImageTk.PhotoImage(Image.open("sprites/idle/idle_2.png").resize((50, 50)))
            self.images["walk_1"] = ImageTk.PhotoImage(Image.open("sprites/walk/walk_1.png").resize((50, 50)))
            self.images["walk_2"] = ImageTk.PhotoImage(Image.open("sprites/walk/walk_2.png").resize((50, 50)))
        except:
            pass  # Sem imagens, usar texto

    def update(self):
        self.move()
        self.animate()
        self.react()
        self.root.after(1000, self.update)

    def move(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        self.x += self.dx * 10
        self.y += self.dy * 10

        if self.x <= 0 or self.x >= screen_width - 100:
            self.dx = -self.dx
        if self.y <= 0 or self.y >= screen_height - 100:
            self.dy = -self.dy

        self.root.geometry(f"100x100+{int(self.x)}+{int(self.y)}")

    def animate(self):
        if self.state == "idle":
            self.current_image = self.images.get("idle_1", None)
        elif self.state == "walk":
            self.current_image = self.images.get("walk_1", None)
        # Adicionar mais estados

        if self.current_image:
            self.canvas.delete("all")
            self.canvas.create_image(50, 50, image=self.current_image)

    def react(self):
        app = self.detect_app()
        if random.random() < 0.1:  # 10% chance de falar
            texto = marcy_ai.responder("", app)
            self.label.config(text=texto)
            self.root.after(3000, lambda: self.label.config(text=""))

    def detect_app(self):
        janela = gw.getActiveWindow()
        if janela:
            title = janela.title.lower()
            if "code" in title:
                return "Code"
            elif "chrome" in title:
                return "Chrome"
        return ""

if __name__ == "__main__":
    pet = MarcyPet()
    pet.root.mainloop()