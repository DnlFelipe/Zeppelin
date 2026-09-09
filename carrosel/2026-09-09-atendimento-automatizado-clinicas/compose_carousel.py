from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import json
import shutil


ROOT = Path(__file__).resolve().parent
WORKSPACE = Path(r"C:\Users\dnlfl\Devs\Zeppelin")
GEN = Path(r"C:\Users\dnlfl\.codex\generated_images\01a0874c-0e36-7ea2-8bef-9edb30aed12a")
LOGO = WORKSPACE / "logos" / "LogoPNG.png"

W, H = 1080, 1350
NAVY = (8, 34, 61)
GOLD = (185, 146, 90)
WHITE = (245, 244, 242)
MUTED = (219, 222, 224)
GREEN = (88, 150, 112)

FONT_REG = Path(r"C:\Windows\Fonts\arial.ttf")
FONT_BOLD = Path(r"C:\Windows\Fonts\arialbd.ttf")


sources = [
    ("slide-01-base.png", GEN / "call_OwGl3jYuE1SSPE3yVvyIK3cZ.png"),
    ("slide-02-base.png", GEN / "call_B7Ss1iA1pyZPMR1FDeZgOiZy.png"),
    ("slide-03-base.png", GEN / "call_pQ5vkUzrEAXt3Q6r7giMGkdm.png"),
    ("slide-04-base.png", GEN / "call_CouaKrMCgvIDaO7FTxHAduTv.png"),
    ("slide-05-base.png", GEN / "call_BdVGl8RzctXAXCcifJVjwUOO.png"),
    ("slide-06-base.png", GEN / "call_Q4JATljCr15Mr3ByLsx5LsIl.png"),
]


slides = [
    {
        "file": "slide-01.png",
        "base": "slide-01-base.png",
        "title": "Tem paciente esperando no WhatsApp da sua clínica agora?",
        "body": "E talvez ele não espere muito.",
        "title_xy": (82, 92),
        "title_w": 850,
        "title_size": 72,
        "body_xy": (86, 410),
        "body_w": 760,
        "body_size": 34,
        "overlay": "top",
        "logo": False,
        "accent": "WhatsApp",
    },
    {
        "file": "slide-02.png",
        "base": "slide-02-base.png",
        "title": "A maioria das clínicas não perde paciente por falta de interesse.",
        "body": "Perde no intervalo entre a mensagem enviada e a primeira resposta recebida.",
        "title_xy": (82, 98),
        "title_w": 860,
        "title_size": 64,
        "body_xy": (86, 430),
        "body_w": 810,
        "body_size": 34,
        "overlay": "soft",
        "logo": True,
        "accent": "não",
    },
    {
        "file": "slide-03.png",
        "base": "slide-03-base.png",
        "title": "Sua recepção está tentando fazer tudo ao mesmo tempo.",
        "body": "Balcão. WhatsApp. Agenda. Confirmações. Dúvidas. Reorganização de horários.",
        "title_xy": (78, 92),
        "title_w": 690,
        "title_size": 54,
        "body_xy": (82, 365),
        "body_w": 640,
        "body_size": 28,
        "overlay": "left",
        "logo": True,
        "accent": "tudo",
    },
    {
        "file": "slide-04.png",
        "base": "slide-04-base.png",
        "title": "Para o paciente, demora também comunica.",
        "body": "Comunica desorganização, falta de atenção ou simplesmente dá tempo para ele procurar outra clínica.",
        "title_xy": (76, 105),
        "title_w": 650,
        "title_size": 68,
        "body_xy": (80, 400),
        "body_w": 650,
        "body_size": 31,
        "overlay": "left",
        "logo": True,
        "accent": "demora",
    },
    {
        "file": "slide-05.png",
        "base": "slide-05-base.png",
        "title": "Atendimento automatizado não precisa parecer um robô frio.",
        "body": "Com IA bem treinada, sua clínica acolhe, entende a necessidade e inicia o agendamento com agilidade.",
        "title_xy": (74, 82),
        "title_w": 790,
        "title_size": 53,
        "body_xy": (78, 415),
        "body_w": 710,
        "body_size": 29,
        "overlay": "top",
        "logo": True,
        "accent": "não",
        "body_box": True,
    },
    {
        "file": "slide-06.png",
        "base": "slide-06-base.png",
        "title": "O paciente que chama hoje precisa ser atendido hoje.",
        "body": "Demonstração de agendamento clínico no link da bio.",
        "title_xy": (78, 94),
        "title_w": 760,
        "title_size": 68,
        "body_xy": (82, 425),
        "body_w": 650,
        "body_size": 34,
        "overlay": "left",
        "logo": True,
        "accent": "hoje",
        "cta": True,
    },
]


prompts = [
    "Slide 1: smartphone em primeiro plano no balcao de clinica brasileira moderna, notificacoes genericas sem texto legivel, recepcao desfocada, espaco negativo para titulo, paleta Zeppelin.",
    "Slide 2: base grafica editorial azul marinho com linha temporal dourada, bolhas de conversa abstratas sem texto, visual premium e minimalista.",
    "Slide 3: recepcao de clinica moderna em rotina cheia, atendente ao telefone, paciente no balcao, agenda e celular sem texto legivel, tom humano.",
    "Slide 4: paciente olhando celular em casa no fim do dia, expressao de espera contida, area escura para texto, atmosfera editorial.",
    "Slide 5: atendimento assistido por IA sem robo literal, bolhas e fluxos abstratos sobre clinica, sensacao de acolhimento e organizacao.",
    "Slide 6: celular com confirmacoes genericas e calendario clinico, fundo azul premium, espaco para CTA, sem texto legivel na base.",
]


def font(size, bold=False):
    return ImageFont.truetype(str(FONT_BOLD if bold else FONT_REG), size)


def cover_resize(img):
    img = img.convert("RGB")
    scale = max(W / img.width, H / img.height)
    nw, nh = int(img.width * scale), int(img.height * scale)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - W) // 2
    top = (nh - H) // 2
    return img.crop((left, top, left + W, top + H))


def add_gradient(img, mode):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = overlay.load()
    for y in range(H):
        for x in range(W):
            alpha = 0
            if mode == "top":
                alpha = max(0, int(205 * (1 - y / 610)))
            elif mode == "left":
                alpha = max(0, int(225 * (1 - x / 760)))
                alpha = max(alpha, max(0, int(95 * (1 - y / 650))))
            elif mode == "soft":
                alpha = 42
            px[x, y] = (NAVY[0], NAVY[1], NAVY[2], alpha)
    return Image.alpha_composite(img.convert("RGBA"), overlay)


def wrap_text(draw, text, fnt, width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        test = word if not current else current + " " + word
        if draw.textbbox((0, 0), test, font=fnt)[2] <= width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_wrapped(draw, xy, text, fnt, width, fill, spacing=10):
    x, y = xy
    for line in wrap_text(draw, text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        bbox = draw.textbbox((x, y), line, font=fnt)
        y += (bbox[3] - bbox[1]) + spacing
    return y


def draw_accent_bar(draw, x, y, w=92):
    draw.rounded_rectangle((x, y, x + w, y + 8), radius=4, fill=GOLD)


def paste_logo(img):
    if not LOGO.exists():
        return img
    logo = Image.open(LOGO).convert("RGBA")
    logo.thumbnail((116, 54), Image.Resampling.LANCZOS)
    alpha = logo.getchannel("A").point(lambda p: int(p * 0.86))
    logo.putalpha(alpha)
    img.alpha_composite(logo, (W - logo.width - 56, 52))
    return img


def draw_footer(draw, idx):
    draw.text((74, H - 82), f"0{idx}/06", font=font(22, True), fill=(WHITE[0], WHITE[1], WHITE[2], 210))
    draw.rounded_rectangle((160, H - 72, 320, H - 66), radius=3, fill=(WHITE[0], WHITE[1], WHITE[2], 72))
    draw.rounded_rectangle((160, H - 72, 160 + int(160 * idx / 6), H - 66), radius=3, fill=GOLD)


def compose_slide(idx, spec):
    base = Image.open(ROOT / spec["base"])
    img = cover_resize(base)
    img = add_gradient(img, spec["overlay"])
    img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=105, threshold=3))
    draw = ImageDraw.Draw(img)
    draw_accent_bar(draw, spec["title_xy"][0], spec["title_xy"][1] - 28)
    draw_wrapped(
        draw,
        spec["title_xy"],
        spec["title"],
        font(spec["title_size"], True),
        spec["title_w"],
        WHITE,
        spacing=8,
    )
    if spec.get("cta"):
        bx, by = spec["body_xy"][0], spec["body_xy"][1] - 18
        draw.rounded_rectangle((bx - 18, by - 16, bx + 670, by + 106), radius=18, fill=(8, 34, 61, 185), outline=GOLD, width=2)
    if spec.get("body_box"):
        bx, by = spec["body_xy"][0], spec["body_xy"][1] - 18
        draw.rounded_rectangle((bx - 18, by - 16, bx + 740, by + 118), radius=18, fill=(8, 34, 61, 205), outline=(245, 244, 242, 70), width=1)
    draw_wrapped(
        draw,
        spec["body_xy"],
        spec["body"],
        font(spec["body_size"], False),
        spec["body_w"],
        MUTED,
        spacing=7,
    )
    if spec["logo"]:
        img = paste_logo(img)
    draw_footer(ImageDraw.Draw(img), idx)
    img.convert("RGB").save(ROOT / spec["file"], quality=95)


def write_docs():
    brief = """# Briefing consolidado

Marca/projeto: Zeppelin
Canal de referencia: @zeppelin.ia
Nicho: agencia de marketing, automacoes e criacao de software sob demanda
Publico-alvo: donos e gestores de clinicas
Objetivo: fazer donos de clinicas perceberem que o gargalo pode estar no atendimento, especialmente no WhatsApp.
Tema: atendimento automatizado para clinicas
Formato: feed 4:5
Identidade: azul #08223D, dourado #B9925A, branco #F5F4F2. Sem logo na capa; logo sutil nos demais slides.

Tese: sua clinica pode estar perdendo pacientes antes da primeira resposta.
"""

    package = """# Pacote do carrossel

## Estrategia

O problema nao e falta de paciente. E paciente interessado esperando tempo demais para ser acolhido.

## Copy

1. Tem paciente esperando no WhatsApp da sua clinica agora?
   E talvez ele nao espere muito.

2. A maioria das clinicas nao perde paciente por falta de interesse.
   Perde no intervalo entre a mensagem enviada e a primeira resposta recebida.

3. Sua recepcao esta tentando fazer tudo ao mesmo tempo.
   Balcao. WhatsApp. Agenda. Confirmacoes. Duvidas. Reorganizacao de horarios.

4. Para o paciente, demora tambem comunica.
   Comunica desorganizacao, falta de atencao ou simplesmente da tempo para ele procurar outra clinica.

5. Atendimento automatizado nao precisa parecer um robo frio.
   Com IA bem treinada, sua clinica acolhe, entende a necessidade e inicia o agendamento com agilidade.

6. O paciente que chama hoje precisa ser atendido hoje.
   Demonstracao de agendamento clinico no link da bio.

## Legenda

Seu WhatsApp pode estar cheio de pacientes interessados que ainda nao foram atendidos.

E cada minuto de espera comunica alguma coisa: organizacao, atencao, cuidado ou ausencia deles.

Atendimento automatizado com IA nao precisa ser frio. Quando bem treinado, ele acolhe, entende a necessidade do paciente e ajuda sua clinica a iniciar o agendamento com mais agilidade.

Veja a demonstracao de agendamento clinico da Zeppelin no link da bio.

## CTA

Demonstracao de agendamento clinico no link da bio.

## Prompts de imagem

""" + "\n".join(f"{i + 1}. {p}" for i, p in enumerate(prompts)) + """

## Checklist de qualidade

- Tese clara.
- Hook direto para dono de clinica.
- Seis slides com funcoes distintas.
- Visual sem HTML.
- Imagens geradas por IA e copy aplicada como raster.
- Identidade Zeppelin consistente.
- Logo fora da capa e sutil nos demais slides.
- CTA leve.
"""

    metadata = {
        "brand": "Zeppelin",
        "handle": "@zeppelin.ia",
        "format": "4:5",
        "theme": "atendimento automatizado para clinicas",
        "slides": [s["file"] for s in slides],
        "base_images": [s[0] for s in sources],
        "logo": str(LOGO),
        "prompts": prompts,
    }

    (ROOT / "brief.md").write_text(brief, encoding="utf-8")
    (ROOT / "carousel-package.md").write_text(package, encoding="utf-8")
    (ROOT / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    for target, source in sources:
        shutil.copy2(source, ROOT / target)
    for idx, spec in enumerate(slides, start=1):
        compose_slide(idx, spec)
    write_docs()


if __name__ == "__main__":
    main()
