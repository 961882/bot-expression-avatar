---
name: bot-expression-avatar
description: 给 bot 做会变表情的头像：一张 2×2 表情图切成静态 PNG 和四表情轮播 GIF，用作 Grok Bot 的 bot 头像。用在"给 bot 做头像 / 动态头像 / 表情头像 / 新 bot 要头像"时。
---

# Bot 表情头像（Grok Bot 版）

把一张四格表情图做成会变表情的 bot 头像。完整说明、演示和 OpenMausBot 版见 https://github.com/961882/bot-expression-avatar 。
本文件自带切图脚本（见文末），不需要额外下载。

## 开始前
一次只问用户一件事：给哪个 bot 做、想要什么动物或角色。没说风格就用默认风格。

## 默认风格
3D 皮克斯风、白底、藏青色带领衬衫、金色圆框眼镜、胸前一枚和 bot 职责相关的金色小胸针。每个 bot 一种动物，不要和用户已有的 bot 重复。用户另有要求时以用户为准。

## 第 1 步：出一张 2×2 表情图
用你的生图工具出**一张**图（不要分四次出，四格才能对齐）。提示词模板，只换【】里的内容：

```text
Character expression sheet, a 2x2 grid of four equal square panels on a pure white background with no borders or text. Every panel shows the exact same 3D Pixar-style cartoon 【动物+外貌】 character, head and shoulders, identical size, position, camera angle and lighting in every panel: 【毛色/发型】, round gold wire-rim glasses, navy blue button-up shirt with collar, small gold 【胸针】 pin on the chest. Only the facial expression changes. Top-left: 【平静友好】, eyes open. Top-right: same as top-left but both eyes closed (blink). Bottom-left: 【干活时的表情：thoughtful / skeptical / calculating / surprised】. Bottom-right: 【开心说话：open-mouth smile】.
```

四格含义固定：左上平静、右上眨眼、左下干活、右下开心说话。
出图后检查：四格里人物大小、位置一致，白底。不一致就重出。
没有生图工具时：把提示词发给用户，请他用任意生图工具出图后发回来。

## 第 2 步：切图、做动图
1. 把文末「切图脚本」原样存成 `make_avatar.py`。
2. 装依赖并运行：

```bash
pip install pillow
python3 make_avatar.py <表情图> out <名字> --size 320
```

产出在 `out/` 里：
- `名字-grok.gif`：四种表情轮播，**Grok Bot 头像用这个**
- `名字.png`：静态头像，GIF 用不了时的备选
- `名字-hover.gif`、`名字-busy.gif`、`名字-talk.gif`：给 OpenMausBot 按状态换图用的，Grok Bot 用不到

## 第 3 步：交给用户上传
Grok Bot 的头像只能用户在界面里自己换。把 `名字-grok.gif` 和 `名字.png` 发给用户，附上这几步：
1. 打开 Grok Bot → 点 bot 的名字 → **编辑 Bot 头像** → 选择图片，上传 `名字-grok.gif`（支持 png、jpeg、gif、webp，最大 20 MB）。
2. 会弹出裁剪框，确认即可。
3. 裁完如果头像不动了（GIF 被压成了静态图），改传 `名字.png`。

## 常见问题
- 人物在动图里跳：四格没对齐，重新出图，提示词里强调 `identical size, position, camera angle`。
- GIF 太大：用 `--size 200`。

## 切图脚本（make_avatar.py）

```python
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
```
