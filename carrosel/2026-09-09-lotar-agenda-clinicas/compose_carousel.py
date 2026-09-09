from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter


ROOT = Path(__file__).resolve().parent
BASE_DIR = ROOT / "base-images"
OUT_DIR = ROOT / "final-slides"
LOGO_PATH = Path(r"C:\Users\dnlfl\Devs\Zeppelin\logos\LogoPNG.png")

W, H = 1080, 1350
NAVY = (8, 34, 61)
NAVY_DARK = (3, 17, 31)
GOLD = (185, 146, 90)
OFF_WHITE = (245, 244, 242)

FONT_REGULAR = r"C:\Windows\Fonts\segoeui.ttf"
FONT_BOLD = r"C:\Windows\Fonts\segoeuib.ttf"


SLIDES = [
    {
        "n": 1,
        "title": "Sua agenda\nvive cheia,",
        "accent": "mas o particular\nnão aparece?",
        "body": "Existe uma diferença entre ter movimento e ter previsibilidade.",
        "layout": "left",
        "overlay": 150,
        "logo": False,
    },
    {
        "n": 2,
        "title": "Plano de saúde\najuda a encher\na agenda.",
        "body": "Ele coloca pacientes na rotina da clínica sem exigir tanto esforço comercial.",
        "layout": "left",
        "overlay": 120,
        "logo": True,
    },
    {
        "n": 3,
        "title": "Mas depender\nsó disso trava\no crescimento.",
        "body": "A clínica trabalha muito, a equipe se ocupa, mas a margem continua limitada.",
        "layout": "left",
        "overlay": 135,
        "logo": True,
    },
    {
        "n": 4,
        "title": "Paciente particular\nnão aparece\npor acaso.",
        "body": "Ele precisa encontrar sua clínica, entender o valor do atendimento e chegar com intenção de marcar.",
        "layout": "right",
        "overlay": 110,
        "logo": True,
    },
    {
        "n": 5,
        "title": "A agenda particular\nprecisa de\n3 camadas.",
        "body": "Demanda. Filtro. Agendamento.",
        "layout": "left",
        "overlay": 95,
        "logo": True,
    },
    {
        "n": 6,
        "title": "Primeiro,\nvocê gera\ndemanda.",
        "body": "Anúncios e ações de marketing levam potenciais pacientes para o WhatsApp da clínica.",
        "layout": "left",
        "overlay": 125,
        "logo": True,
    },
    {
        "n": 7,
        "title": "Depois,\nvocê filtra\nos curiosos.",
        "body": "Triagem e qualificação separam quem só está perguntando de quem realmente tem intenção de marcar.",
        "layout": "left",
        "overlay": 115,
        "logo": True,
    },
    {
        "n": 8,
        "title": "A secretária\nnão recebe\nsó mensagens.",
        "body": "Ela recebe contatos mais prontos para virar consulta.",
        "layout": "left",
        "overlay": 115,
        "logo": True,
    },
    {
        "n": 9,
        "title": "Quer aplicar\nessa estrutura\nna sua clínica?",
        "body": "Comente LOTAR AGENDA que a Zeppelin te mostra o caminho.",
        "layout": "left",
        "overlay": 50,
        "logo": True,
    },
]


def font(size, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REGULAR, size)


def fit_text(draw, text, font_obj, max_width):
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        line = ""
        for word in words:
            test = word if not line else f"{line} {word}"
            if draw.textbbox((0, 0), test, font=font_obj)[2] <= max_width:
                line = test
            else:
                if line:
                    lines.append(line)
                line = word
        if line:
            lines.append(line)
    return lines


def draw_text(draw, xy, text, font_obj, fill):
    x, y = xy
    shadow = (0, 0, 0, 150)
    draw.text((x + 2, y + 3), text, font=font_obj, fill=shadow)
    draw.text((x, y), text, font=font_obj, fill=fill)


def draw_multiline(draw, xy, lines, font_obj, fill, leading):
    x, y = xy
    for line in lines:
        draw_text(draw, (x, y), line, font_obj, fill)
        y += leading
    return y


def add_gradient(img, alpha):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pixels = overlay.load()
    for y in range(H):
        for x in range(W):
            left_bias = int(alpha * max(0, 1 - x / W) * 0.78)
            top_bias = int(alpha * max(0, 1 - y / H) * 0.22)
            bottom_bias = int(70 * max(0, (y - H * 0.66) / (H * 0.34)))
            pixels[x, y] = (*NAVY_DARK, min(210, left_bias + top_bias + bottom_bias))
    return Image.alpha_composite(img.convert("RGBA"), overlay)


def add_logo(img):
    if not LOGO_PATH.exists():
        return img
    logo = Image.open(LOGO_PATH).convert("RGBA")
    target_w = 88
    ratio = target_w / logo.width
    logo = logo.resize((target_w, int(logo.height * ratio)), Image.LANCZOS)
    alpha = logo.getchannel("A").point(lambda p: int(p * 0.72))
    logo.putalpha(alpha)
    img.alpha_composite(logo, (W - target_w - 58, 54))
    return img


def add_text_wash(img, box):
    wash = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(wash)
    draw.rounded_rectangle(box, radius=16, fill=(*NAVY_DARK, 78))
    wash = wash.filter(ImageFilter.GaussianBlur(18))
    return Image.alpha_composite(img, wash)


def compose_slide(slide):
    src = BASE_DIR / f"slide-{slide['n']:02d}-base.png"
    img = Image.open(src).convert("RGB")
    img = ImageOps.fit(img, (W, H), method=Image.LANCZOS, centering=(0.5, 0.5)).convert("RGBA")
    img = add_gradient(img, slide["overlay"])
    draw = ImageDraw.Draw(img)

    margin = 74
    max_width = 760 if slide["layout"] == "left" else 640
    x = margin if slide["layout"] == "left" else W - margin - max_width
    y = 188 if slide["n"] != 9 else 230
    if slide["n"] in {6, 7, 8}:
        img = add_text_wash(img, (x - 32, y - 34, x + max_width + 32, y + 650))
        draw = ImageDraw.Draw(img)

    draw.rounded_rectangle((margin, 56, margin + 58, 64), radius=4, fill=GOLD)
    draw_text(draw, (margin, 78), f"{slide['n']:02d}/09", font(28, True), GOLD)

    title_font = font(74 if slide["n"] != 9 else 72, True)
    title_lines = fit_text(draw, slide["title"], title_font, max_width)
    y = draw_multiline(draw, (x, y), title_lines, title_font, OFF_WHITE, 88)

    if slide.get("accent"):
        y += 12
        accent_font = font(74, True)
        accent_lines = fit_text(draw, slide["accent"], accent_font, max_width)
        y = draw_multiline(draw, (x, y), accent_lines, accent_font, GOLD, 88)

    y += 42
    draw.rounded_rectangle((x, y, x + 86, y + 7), radius=4, fill=GOLD)
    y += 34

    body_font = font(42, False)
    body_lines = fit_text(draw, slide["body"], body_font, max_width)
    draw_multiline(draw, (x, y), body_lines, body_font, OFF_WHITE, 55)

    if slide["logo"]:
        img = add_logo(img)

    img.save(OUT_DIR / f"slide-{slide['n']:02d}.png")


def make_preview():
    thumbs = []
    for n in range(1, 10):
        img = Image.open(OUT_DIR / f"slide-{n:02d}.png").convert("RGB")
        img.thumbnail((270, 338), Image.LANCZOS)
        thumbs.append(img)
    preview = Image.new("RGB", (270 * 3, 338 * 3), OFF_WHITE)
    for idx, thumb in enumerate(thumbs):
        x = (idx % 3) * 270
        y = (idx // 3) * 338
        preview.paste(thumb, (x, y))
    preview.save(ROOT / "preview-grid.jpg", quality=92)


if __name__ == "__main__":
    from PIL import ImageOps

    OUT_DIR.mkdir(exist_ok=True)
    for item in SLIDES:
        compose_slide(item)
    make_preview()
