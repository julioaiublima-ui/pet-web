from PIL import Image, ImageDraw


ANIMACOES = {
    "idle_normal": {
        "pasta": "idle",
        "frames": ["idle_1", "idle_2", "idle_3", "idle_4"],
    },
    "idle_glasses": {
        "pasta": "idle",
        "frames": ["idle_glasses_1", "idle_glasses_2", "idle_glasses_3"],
    },
    "idle_curious": {
        "pasta": "idle",
        "frames": ["idle_look_left_1", "idle_look_left_2", "idle_look_right_1", "idle_look_right_2"],
    },
    "idle_thinking": {
        "pasta": "idle",
        "frames": ["idle_thinking_1", "idle_thinking_2"],
    },
    "idle_smile": {
        "pasta": "idle",
        "frames": ["idle_smile_1", "idle_smile_2"],
    },
    "walk": {
        "pasta": "walk",
        "frames": ["walk_1", "walk_2"],
    },
    "talking": {
        "pasta": "talking",
        "frames": ["talking_1", "talking_2"],
    },
    "thinking": {
        "pasta": "thinking",
        "frames": ["thinking_1", "thinking_2"],
    },
    "observing": {
        "pasta": "observing",
        "frames": ["observing_1", "observing_2"],
    },
}


def _criar_sprite_placeholder_imagem(estado, tamanho_sprite):
    cores = {
        "idle": (255, 245, 210),
        "walk": (210, 240, 255),
        "talking": (255, 230, 235),
        "thinking": (235, 230, 255),
        "observing": (220, 255, 235),
    }

    imagem = Image.new("RGBA", (tamanho_sprite, tamanho_sprite), (0, 0, 0, 0))
    draw = ImageDraw.Draw(imagem)

    cor_fundo = cores.get(estado, (245, 245, 245))
    draw.rounded_rectangle((2, 2, tamanho_sprite - 3, tamanho_sprite - 3), radius=12, fill=cor_fundo)

    draw.ellipse((tamanho_sprite * 0.18, tamanho_sprite * 0.18, tamanho_sprite * 0.82, tamanho_sprite * 0.72), fill=(255, 255, 255, 240))
    draw.ellipse((tamanho_sprite * 0.32, tamanho_sprite * 0.35, tamanho_sprite * 0.42, tamanho_sprite * 0.45), fill=(30, 30, 30, 240))
    draw.ellipse((tamanho_sprite * 0.58, tamanho_sprite * 0.35, tamanho_sprite * 0.68, tamanho_sprite * 0.45), fill=(30, 30, 30, 240))
    draw.arc((tamanho_sprite * 0.28, tamanho_sprite * 0.47, tamanho_sprite * 0.72, tamanho_sprite * 0.68), start=20, end=160, fill=(255, 160, 180, 255), width=3)

    return imagem


def carregar_imagens(pasta_base, tamanho_sprite):
    imagens = {}

    for animacao in ANIMACOES.values():
        pasta = animacao["pasta"]

        for nome in animacao["frames"]:
            caminho = pasta_base / "sprites" / pasta / f"{nome}.png"

            try:
                if not caminho.exists() or caminho.stat().st_size == 0:
                    raise FileNotFoundError(caminho)

                imagem = Image.open(caminho).convert("RGBA")
                imagem = imagem.resize((tamanho_sprite, tamanho_sprite))
                imagens[nome] = imagem
            except Exception:
                try:
                    imagens[nome] = _criar_sprite_placeholder_imagem(pasta, tamanho_sprite)
                except Exception as erro:
                    print(f"sprite nao encontrado: {caminho} ({erro})")

    return imagens


def proximo_frame(animacao, frame_animacao):
    nomes = ANIMACOES.get(animacao, ANIMACOES["idle_normal"])["frames"]
    return nomes[frame_animacao % len(nomes)]
