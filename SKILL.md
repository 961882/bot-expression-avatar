---
name: bot-expression-avatar
description: 给 bot 做会变表情的头像：平时静止，鼠标移上眨眼微笑，干活时换思考表情，回复时像在说话。支持 OpenMausBot 和 Grok Bot。用在"给 bot 做头像 / 动态头像 / 表情头像 / 新 bot 要头像"时。
aliases: [头像, 动态头像, 表情头像, bot 头像, avatar, expression avatar]
---

# Bot 表情头像

完整说明和案例见 README.md。本文件是给 agent 的执行步骤。脚本在本 skill 的 `scripts/` 下，下文用 `$SKILL` 指本 skill 所在目录。

## 风格
默认：3D 皮克斯风、白底、藏青色带领衬衫、金色圆框眼镜、胸前一枚和 bot 职责相关的金色小胸针。每个 bot 一种动物，不要和已有 bot 重复。用户另有风格要求时以用户为准。

## 第 1 步：出一张 2×2 表情图
用图片生成工具，提示词模板（只换【】）：

> Character expression sheet, a 2x2 grid of four equal square panels on a pure white background with no borders or text. Every panel shows the exact same 3D Pixar-style cartoon 【动物+外貌】 character, head and shoulders, identical size, position, camera angle and lighting in every panel: 【毛色/发型】, round gold wire-rim glasses, navy blue button-up shirt with collar, small gold 【胸针】 pin on the chest. Only the facial expression changes. Top-left: 【平静友好】, eyes open. Top-right: same as top-left but both eyes closed (blink). Bottom-left: 【干活时的表情：思考 / 怀疑 / 算账 / 吃惊】. Bottom-right: 【开心/说话：张嘴笑】.

四格固定含义：左上平静、右上眨眼、左下干活、右下开心说话。检查四格人物位置一致、白底；不一致就重出。

## 第 2 步：切图、做动图
```
python3 $SKILL/scripts/make_avatar.py <表情图> <输出目录> <名字> [--size 320]
```
产出 `名字.png`（静态）、`名字-hover.gif`、`名字-busy.gif`、`名字-talk.gif`、`名字-grok.gif`。需要 Pillow。

## 第 3 步 A：OpenMausBot
用主题实现：头像设静态 PNG，主题 CSS 按状态换 GIF。**每轮最多改 10 项设置**，一个 bot 占 4 项（3 个动图 + 1 个头像），外加 1 次套主题，所以一轮最多做 2 个 bot；超了就请用户再发一句话继续。设置只能在用户本人发消息的那一轮里改。
1. `app_settings add_theme_asset`（id 用要放的主题，如 `background`）加入 hover/busy/talk 三个 GIF，记下返回的 `/api/theme-assets/<id>/…` 地址（文件名会被改，以返回值为准）。
2. `app_settings set bots.picture`，值 `{"botId":"…","path":"…/名字.png"}`。从返回里读出该 bot 的 `/api/attachments/<附件id>.png`，取附件 id 前 8 位。
3. 写 bots.json：`[{botId,png,hover,busy,talk}]`，已有 bot 的条目保留。运行 `python3 $SKILL/scripts/maus_css.py bots.json` 得到 CSS。
4. `app_settings theme` 读回现有主题的 css，**合并**（别丢其他规则），再 `set_theme` 写回并启用。
5. 请用户自己看三种状态：鼠标移上、bot 干活时、bot 回复时。

原理：头像是 `[data-avatar="picture"] img`；侧边栏行 `[data-sidebar-bot-row="<botId>"]` 干活时带 `aria-busy="true"`；正在输出的消息文字带 `data-streaming`；CSS 用 `content: url(gif)` 换图。界面改版后失效，就在 app 前端代码里重新找这几个标记。

## 第 3 步 B：Grok Bot
头像存在云端，一个 bot 只能放一张，不能按状态切换。
1. Grok Bot → 点 bot 名字 → 编辑 Bot 头像 → 上传 `名字-grok.gif`（png/jpeg/gif/webp，≤20 MB）。
2. 裁剪后若不动了，改传 `名字.png`。
3. 这一步要在 Grok Bot 界面里点；agent 没有屏幕操作能力时，把文件给用户让他自己上传。

## 做完
- 记下用过的动物，避免以后重复。
- 把 `名字.png` 和 `名字-hover.gif` 给用户看。
