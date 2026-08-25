from PIL import Image, ImageDraw


SPRITES_POR_ESTADO = {
    "idle": ["idle_1", "idle_2"],
    "walk": ["walk_1", "walk_2"],
    "talking": ["talking_1", "talking_2"],
    "thinking": ["thinking_1", "thinking_2"],
    "observing": ["observing_1", "observing_2"],
    "walk_direita": [],
    "walk_esquerda": [],
}

_FRAMES_ATUAIS = {estado: list(nomes) for estado, nomes in SPRITES_POR_ESTADO.items()}
_DURACOES_ATUAIS = {}


def _recortar_frame_duplicado(frame):
    # Os GIFs atuais já contêm uma personagem inteira por frame.
    return frame


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
    global _FRAMES_ATUAIS
    global _DURACOES_ATUAIS

    imagens = {}
    _FRAMES_ATUAIS = {}
    _DURACOES_ATUAIS = {}

    for estado, nomes in SPRITES_POR_ESTADO.items():
        if estado == "walk":
            continue

        frames_estado = []
        duracoes_estado = []
        estado_arquivo = estado
        if estado in ("walk_direita", "walk_esquerda"):
            estado_arquivo = "walk"

        caminhos_gif = [pasta_base / "sprites" / estado_arquivo / f"{estado_arquivo}.gif"]
        if estado == "walk_direita":
            caminhos_gif = [
                pasta_base / "sprites" / estado_arquivo / "walk-direita.gif",
                *caminhos_gif,
            ]
        elif estado == "walk_esquerda":
            caminhos_gif = [
                pasta_base / "sprites" / estado_arquivo / "walk-esquerda.gif",
                *caminhos_gif,
            ]

        caminho_gif = next(
            (caminho for caminho in caminhos_gif if caminho.exists() and caminho.stat().st_size > 0),
            caminhos_gif[0],
        )

        if caminho_gif.exists() and caminho_gif.stat().st_size > 0:
            try:
                with Image.open(caminho_gif) as gif:
                    indice = 0
                    while True:
                        frame = _recortar_frame_duplicado(gif.convert("RGBA"))
                        frame.thumbnail((tamanho_sprite, tamanho_sprite), Image.Resampling.LANCZOS)
                        nome = f"{estado}_{indice + 1}"
                        imagens[nome] = frame.copy()
                        frames_estado.append(nome)
                        duracoes_estado.append(max(40, gif.info.get("duration") or 100))
                        indice += 1
                        try:
                            gif.seek(indice)
                        except EOFError:
                            break
            except Exception as erro:
                print(f"gif nao encontrado: {caminho_gif} ({erro})")

        if not frames_estado:
            for nome in nomes:
                nome_com_hifen = nome.replace("_", "-")
                caminhos = [
                    pasta_base / "sprites" / estado / f"{nome_com_hifen}.gif",
                    pasta_base / "sprites" / estado / f"{nome}.gif",
                ]

                try:
                    caminho = next(
                        caminho
                        for caminho in caminhos
                        if caminho.exists() and caminho.stat().st_size > 0
                    )

                    imagem = _recortar_frame_duplicado(Image.open(caminho).convert("RGBA"))
                    imagem.thumbnail((tamanho_sprite, tamanho_sprite), Image.Resampling.LANCZOS)
                    imagens[nome] = imagem
                    duracoes_estado.append(100)
                except Exception:
                    try:
                        imagens[nome] = _criar_sprite_placeholder_imagem(estado, tamanho_sprite)
                    except Exception as erro:
                        print(f"sprite nao encontrado: {caminho} ({erro})")

                frames_estado.append(nome)

        _FRAMES_ATUAIS[estado] = frames_estado
        _DURACOES_ATUAIS[estado] = duracoes_estado

    _FRAMES_ATUAIS["walk"] = _FRAMES_ATUAIS.get("walk_direita", [])
    _DURACOES_ATUAIS["walk"] = _DURACOES_ATUAIS.get("walk_direita", [])

    return imagens


def proximo_frame(estado, frame_animacao):
    nomes = _FRAMES_ATUAIS.get(estado) or _FRAMES_ATUAIS.get("idle") or SPRITES_POR_ESTADO["idle"]
    return nomes[frame_animacao % len(nomes)]


def duracao_frame(estado, frame_animacao):
    duracoes = _DURACOES_ATUAIS.get(estado) or _DURACOES_ATUAIS.get("idle") or [100]
    return duracoes[frame_animacao % len(duracoes)]
