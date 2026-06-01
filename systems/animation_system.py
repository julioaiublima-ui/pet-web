from PIL import Image, ImageTk


SPRITES_POR_ESTADO = {
    "idle": ["idle_1", "idle_2"],
    "walk": ["walk_1", "walk_2"],
    "talking": ["talking_1", "talking_2"],
    "thinking": ["thinking_1", "thinking_2"],
    "observing": ["observing_1", "observing_2"],
}


def carregar_imagens(pasta_base, tamanho_sprite):
    imagens = {}

    for estado, nomes in SPRITES_POR_ESTADO.items():
        for nome in nomes:
            caminho = pasta_base / "sprites" / estado / f"{nome}.png"

            if not caminho.exists():
                continue

            try:
                imagem = Image.open(caminho).resize((tamanho_sprite, tamanho_sprite))
                imagens[nome] = ImageTk.PhotoImage(imagem)
            except Exception:
                print(f"sprite nao encontrado: {caminho}")

    return imagens


def proximo_frame(estado, frame_animacao):
    nomes = SPRITES_POR_ESTADO.get(estado, SPRITES_POR_ESTADO["idle"])
    return nomes[frame_animacao % len(nomes)]
