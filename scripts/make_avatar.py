#!/usr/bin/env python3
"""把一张 2x2 表情图（左上平静、右上眨眼、左下干活时的表情、右下开心/说话）
做成：<name>.png（平时静态）、<name>-hover.gif、<name>-busy.gif、<name>-talk.gif、<name>-grok.gif。
用法: python3 make_avatar.py SHEET.png OUT_DIR NAME [--size 320]
"""
import sys, argparse
from pathlib import Path
from PIL import Image, ImageChops

ap = argparse.ArgumentParser()
ap.add_argument("sheet"); ap.add_argument("out"); ap.add_argument("name")
ap.add_argument("--size", type=int, default=320)
a = ap.parse_args()
S = a.size
sheet = Image.open(a.sheet).convert("RGB")
W, H = sheet.size
cells = [sheet.crop((x*W//2, y*H//2, (x+1)*W//2, (y+1)*H//2)) for y in (0, 1) for x in (0, 1)]

# 统一裁切框：四格内容外框的并集，保证四格对齐、人物不跳
bg = Image.new("RGB", cells[0].size, "white")
boxes = [ImageChops.difference(c, bg).convert("L").point(lambda v: 255 if v > 18 else 0).getbbox() for c in cells]
boxes = [b for b in boxes if b]
l = min(b[0] for b in boxes); t = min(b[1] for b in boxes); r = max(b[2] for b in boxes); btm = max(b[3] for b in boxes)
side = max(r - l, btm - t); cx = (l + r) / 2
x0 = int(cx - side / 2); y0 = btm - side  # 底边贴齐（肩膀到画框底）
def norm(c):
    can = Image.new("RGB", (side, side), "white")
    can.paste(c.crop((max(x0, 0), max(y0, 0), min(x0 + side, c.width), min(y0 + side, c.height))),
              (max(-x0, 0), max(-y0, 0)))
    return can.resize((S, S), Image.LANCZOS)
neutral, blink, busy, happy = [norm(c) for c in cells]

def fade(a_, b_, n):  # a->b 过渡帧（不含 a，含 b）
    return [Image.blend(a_, b_, (i + 1) / n) for i in range(n)]

def save(frames, path):  # frames: [(img, ms)]
    pal = frames[0][0].quantize(colors=255, method=Image.MEDIANCUT)
    imgs = [f.quantize(palette=pal, dither=Image.FLOYDSTEINBERG) for f, _ in frames]
    imgs[0].save(path, save_all=True, append_images=imgs[1:], duration=[d for _, d in frames],
                 loop=0, optimize=True, disposal=1)

out = Path(a.out); out.mkdir(parents=True, exist_ok=True); n = a.name
neutral.save(out / f"{n}.png")

# 鼠标移上：眨眼 → 笑开 → 回到平静
hover = [(neutral, 500), (blink, 110), (neutral, 500)] + [(f, 45) for f in fade(neutral, happy, 4)] \
      + [(happy, 1300)] + [(f, 45) for f in fade(happy, neutral, 4)] + [(neutral, 700), (blink, 110)]
save(hover, out / f"{n}-hover.gif")

# 干活中：切到干活表情，偶尔回神眨眼
bz = [(f, 50) for f in fade(neutral, busy, 4)] + [(busy, 2200)] + [(f, 50) for f in fade(busy, neutral, 3)] \
   + [(neutral, 250), (blink, 110), (neutral, 250)]
save(bz, out / f"{n}-busy.gif")

# 回复中：平静/开心交替，像在说话
talk = []
for i in range(6):
    talk += [(neutral, 170), (Image.blend(neutral, happy, .6), 70), (happy, 190), (Image.blend(neutral, happy, .4), 70)]
talk += [(neutral, 300), (blink, 110)]
save(talk, out / f"{n}-talk.gif")

# Grok Bot 只能放一张：一段里轮流演四种表情
grok = [(neutral, 900), (blink, 110), (neutral, 500)] + [(f, 50) for f in fade(neutral, busy, 4)] + [(busy, 1400)] \
     + [(f, 50) for f in fade(busy, happy, 4)] + [(happy, 1400)] + [(f, 50) for f in fade(happy, neutral, 4)]
save(grok, out / f"{n}-grok.gif")
print("ok", out)
