from base64 import b64encode
from functools import lru_cache
from io import BytesIO
from math import cos, pi, sin

from PIL import Image, ImageDraw, ImageFont

from capture_rules import DIFFICULTIES, TARGETS

WIDTH, HEIGHT = 680, 380
CENTER = (298, 186)
RADII = [80, 141]
ORBIT_COLORS = ["#65f0dc", "#b4a2ff"]
GOLD = "#ffd16c"


@lru_cache(maxsize=None)
def font(size):
    return ImageFont.load_default(size=size)


def circle(draw, xy, radius, **style):
    x, y = xy
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), **style)


def orbit_point(radius, angle):
    x, y = CENTER
    return x + radius * cos(angle), y + radius * sin(angle)


@lru_cache(maxsize=1)
def background():
    board = Image.new("RGB", (WIDTH, HEIGHT), "#101a31")
    draw = ImageDraw.Draw(board)
    draw.rectangle((0, 0, WIDTH - 1, HEIGHT - 1), outline="#30415a", width=2)
    for x in range(20, WIDTH, 20):
        for y in range(20, HEIGHT, 20):
            draw.point((x, y), fill="#455874")
    return board


def draw_board(game, now):
    board = background().copy()
    draw = ImageDraw.Draw(board)
    active = game.target if game else 0
    for index, radius in enumerate(RADII):
        color = ORBIT_COLORS[index]
        circle(draw, CENTER, radius + 4, outline="#263854")
        circle(draw, CENTER, radius, outline=color if active == index else "#64748d", width=2)
        label = "K" if index == 0 else "L"
        tag = orbit_point(radius, -2.3)
        circle(draw, tag, 14, fill="#182842", outline=color, width=2)
        draw.text(tag, label, fill=color, font=font(17), anchor="mm")

    circle(draw, CENTER, 43, fill="#203f5d", outline="#4f8ba5", width=2)
    draw.text((CENTER[0], CENTER[1] - 5), "Li", fill="#eefbff", font=font(39), anchor="mm")
    draw.text((CENTER[0], CENTER[1] + 23), "03", fill="#a4c7e2", font=font(13), anchor="mm")

    if game:
        for index, captured_at in enumerate(game.captured):
            shell = TARGETS[index]
            elapsed = (now - captured_at) / 1000
            speed = 1.35 if shell == 0 else -0.8
            angle = speed * elapsed + (index * pi if index else 0)
            xy = orbit_point(RADII[shell], angle)
            circle(draw, xy, 11, fill="#283c60")
            circle(draw, xy, 7, fill=ORBIT_COLORS[shell])

    if active is not None:
        draw_approach(draw, active, game, now)

    buffer = BytesIO()
    board.save(buffer, format="PNG", compress_level=1)
    return "data:image/png;base64," + b64encode(buffer.getvalue()).decode("ascii")


def draw_approach(draw, active, game, now):
    radius = RADII[active]
    y = CENTER[1]
    hit_x = CENTER[0] + radius
    origin = WIDTH + 10
    difficulty = game.difficulty if game else DIFFICULTIES["연습"]
    speed = (origin - hit_x) / difficulty.travel_ms
    tolerance = round(difficulty.capture_window_ms * speed)
    error = now - game.hit_at if game else 0
    in_window = game is not None and game.in_capture_window(now)

    target_color = GOLD if in_window else "#c79b57"
    draw.rectangle((hit_x - tolerance, y - 19, hit_x + tolerance, y + 19),
                   fill="#745122" if in_window else "#332f33",
                   outline=target_color)
    draw.line((hit_x + tolerance, y, WIDTH - 2, y), fill="#687b98", width=2)
    draw.line((hit_x, y - 26, hit_x, y + 26), fill=target_color, width=3)
    if game is not None and now >= game.spawn_at:
        x = max(CENTER[0], hit_x - speed * error)
        draw.line((x, y, min(x + 28, WIDTH), y), fill="#a57945", width=3)
        circle(draw, (x, y), 12, fill="#805634")
        circle(draw, (x, y), 8, fill=GOLD)
        circle(draw, (x, y), 3, fill="#fff1c7")
    draw.text((hit_x, y + 42), "HIT", fill=GOLD, font=font(19), anchor="mm")
