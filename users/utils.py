import random
import re
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError

COLOR_ORANGE = "#FF5733"
COLOR_GREEN = "#33FF57"
COLOR_BLUE = "#3357FF"
COLOR_PURPLE = "#F333FF"
COLOR_CYAN = "#33FFF5"
COLOR_AMBER = "#FFB533"

AVATAR_BG_COLORS = [
    COLOR_ORANGE,
    COLOR_GREEN,
    COLOR_BLUE,
    COLOR_PURPLE,
    COLOR_CYAN,
    COLOR_AMBER,
]

AVATAR_SIZE = (200, 200)
FONT_SIZE = 100
FONT_NAME = "arial.ttf"
AVATAR_TEXT_COLOR = "white"


def generate_avatar(first_letter):
    bg_color = random.choice(AVATAR_BG_COLORS)

    img = Image.new("RGB", AVATAR_SIZE, color=bg_color)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(FONT_NAME, FONT_SIZE)
    except IOError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), first_letter, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]

    position = ((AVATAR_SIZE[0] - w) / 2, (AVATAR_SIZE[1] - h) / 2 - 10)
    draw.text(position, first_letter, font=font, fill=AVATAR_TEXT_COLOR)

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue(), name=f"avatar_{first_letter}.png")


def validate_phone_number(phone, user_instance=None):
    if not phone:
        return phone

    if not re.match(r"^(8|\+7)\d{10}$", phone):
        raise ValidationError(
            "Номер должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX"
        )

    from .models import User

    queryset = User.objects.filter(phone=phone)
    if user_instance and user_instance.pk:
        queryset = queryset.exclude(pk=user_instance.pk)

    if queryset.exists():
        raise ValidationError("Этот номер телефона уже используется.")

    return phone


def validate_github_url(url):
    if url and not url.startswith("https://github.com/"):
        raise ValidationError("Ссылка должна вести на GitHub (https://github.com/...)")
    return url
