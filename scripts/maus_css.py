#!/usr/bin/env python3
"""生成 OpenMausBot 主题 CSS：头像平时静止；bot 干活时换 busy；回复输出时换 talk；鼠标移上换 hover。
用法: python3 maus_css.py bots.json > avatar.css
bots.json: [{"botId":"…","png":"<头像 PNG 附件 id 的前 8 位>","hover":"/api/theme-assets/…","busy":"…","talk":"…"}]
（png 从 app_settings get bots.picture 读回：/api/attachments/<id>.png）
"""
import json, sys
bots = json.load(open(sys.argv[1]))
out = ["/* bot-expression-avatar: 自动生成，勿手改 */"]
for b in bots:
    img = f'img[src*="{b["png"]}"]'
    row = f'[data-sidebar-bot-row="{b["botId"]}"]'
    # 1 干活中：这个 bot 在侧边栏标为忙，它在任何地方的头像都换 busy
    out.append(f':where(body:has({row}[aria-busy="true"])) {img} {{ content: url("{b["busy"]}") !important; }}')
    # 2 回复输出中：正在流式输出的那条消息、以及有输出时聊天顶栏
    out.append(f':where([data-look="message-bot"]:has([data-streaming]), [data-look="app"]:has([data-look="bot-text"][data-streaming]) [data-look="chat-header"]) {img} {{ content: url("{b["talk"]}") !important; }}')
    # 3 鼠标移上（优先级最高）
    out.append(f':where({row}:hover, [data-avatar]:hover) {img} {{ content: url("{b["hover"]}") !important; }}')
    out.append(f'{img}:hover {{ content: url("{b["hover"]}") !important; }}')
out.append('@media (prefers-reduced-motion: reduce) { [data-avatar] img { content: normal !important; } }')
print("\n".join(out))
