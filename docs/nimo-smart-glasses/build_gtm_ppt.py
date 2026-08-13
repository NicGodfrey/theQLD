#!/usr/bin/env python3
"""NIMO 台湾上市 GTM — 汇报型手册 PDF（对齐产业全景手册风格）"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import Color, white, black

pdfmetrics.registerFont(TTFont("WQY", "/tmp/wqy-microhei.ttf"))

W, H = A4  # 595.27 x 841.89
MARGIN_L = 16 * mm
MARGIN_R = 16 * mm
MARGIN_T = 14 * mm
MARGIN_B = 14 * mm
CONTENT_W = W - MARGIN_L - MARGIN_R

C_TEXT = Color(11 / 255, 11 / 255, 11 / 255)
C_BODY = Color(82 / 255, 81 / 255, 78 / 255)
C_MUTED = Color(137 / 255, 135 / 255, 129 / 255)
C_BLUE = Color(28 / 255, 92 / 255, 171 / 255)
C_BLUE_LIGHT = Color(232 / 255, 240 / 255, 250 / 255)
C_GREEN_LIGHT = Color(232 / 255, 244 / 255, 236 / 255)
C_GRAY_BG = Color(245 / 255, 245 / 255, 243 / 255)
C_LINE = Color(220 / 255, 220 / 255, 216 / 255)
C_CARD = Color(250 / 255, 250 / 255, 248 / 255)

DOC_TITLE = "NIMO 智能眼镜 · 台湾上市 GTM 汇报"
DOC_VER = "2026.08 · V1.0"


def wrap_text(c, text, font, size, max_w):
    """Simple CJK-aware wrap by measuring stringWidth."""
    lines = []
    for para in text.split("\n"):
        if not para:
            lines.append("")
            continue
        buf = ""
        for ch in para:
            trial = buf + ch
            if c.stringWidth(trial, font, size) <= max_w:
                buf = trial
            else:
                if buf:
                    lines.append(buf)
                buf = ch
        if buf:
            lines.append(buf)
    return lines


class Deck:
    def __init__(self, path):
        self.c = canvas.Canvas(path, pagesize=A4)
        self.page = 0
        self.y = H - MARGIN_T
        self.part = ""
        self.section = ""

    def new_page(self, part="", section=""):
        if self.page:
            self._footer()
            self.c.showPage()
        self.page += 1
        if part:
            self.part = part
        if section:
            self.section = section
        self.y = H - MARGIN_T
        if self.part or self.section:
            label = " / ".join(x for x in [self.part, self.section] if x)
            self.c.setFont("WQY", 8)
            self.c.setFillColor(C_MUTED)
            self.c.drawString(MARGIN_L, self.y, label)
            self.y -= 8 * mm

    def _footer(self):
        self.c.setStrokeColor(C_LINE)
        self.c.setLineWidth(0.4)
        self.c.line(MARGIN_L, MARGIN_B - 2 * mm, W - MARGIN_R, MARGIN_B - 2 * mm)
        self.c.setFont("WQY", 7)
        self.c.setFillColor(C_MUTED)
        self.c.drawString(MARGIN_L, MARGIN_B - 6 * mm, f"{DOC_TITLE} · {DOC_VER}")
        self.c.drawRightString(W - MARGIN_R, MARGIN_B - 6 * mm, f"{self.page:02d}")

    def title(self, text, size=18):
        self.c.setFont("WQY", size)
        self.c.setFillColor(C_TEXT)
        for line in wrap_text(self.c, text, "WQY", size, CONTENT_W):
            self.c.drawString(MARGIN_L, self.y, line)
            self.y -= size * 1.35
        self.y -= 2 * mm

    def lead(self, text):
        self.c.setFont("WQY", 9)
        self.c.setFillColor(C_BODY)
        for line in wrap_text(self.c, text, "WQY", 9, CONTENT_W):
            self.c.drawString(MARGIN_L, self.y, line)
            self.y -= 12
        self.y -= 3 * mm

    def h2(self, text):
        self.y -= 1 * mm
        # blue square
        self.c.setFillColor(C_BLUE)
        self.c.rect(MARGIN_L, self.y - 1.2, 3.2, 3.2, fill=1, stroke=0)
        self.c.setFont("WQY", 10.5)
        self.c.setFillColor(C_TEXT)
        self.c.drawString(MARGIN_L + 6, self.y - 1, text)
        self.y -= 6 * mm

    def body(self, text, width=None, x=None, size=8.5, leading=11.5, color=C_BODY):
        width = width or CONTENT_W
        x = x if x is not None else MARGIN_L
        self.c.setFont("WQY", size)
        self.c.setFillColor(color)
        for line in wrap_text(self.c, text, "WQY", size, width):
            if self.y < MARGIN_B + 12 * mm:
                self.new_page()
            self.c.drawString(x, self.y, line)
            self.y -= leading
        self.y -= 1.5 * mm

    def blue_span_body(self, parts, width=None, size=8.5, leading=11.5):
        """parts: list of (text, is_blue_bold)"""
        width = width or CONTENT_W
        x0 = MARGIN_L
        x = x0
        self.c.setFont("WQY", size)
        for text, is_blue in parts:
            for ch in text:
                if ch == "\n":
                    self.y -= leading
                    x = x0
                    continue
                w = self.c.stringWidth(ch, "WQY", size)
                if x + w > x0 + width:
                    self.y -= leading
                    x = x0
                self.c.setFillColor(C_BLUE if is_blue else C_BODY)
                self.c.setFont("WQY", size)
                self.c.drawString(x, self.y, ch)
                x += w
        self.y -= leading + 1.5 * mm

    def metrics_row(self, items):
        """items: list of (big, sub, note)"""
        n = len(items)
        gap = 3 * mm
        box_w = (CONTENT_W - gap * (n - 1)) / n
        box_h = 22 * mm
        y0 = self.y - box_h
        for i, (big, sub, note) in enumerate(items):
            x = MARGIN_L + i * (box_w + gap)
            self.c.setFillColor(C_GRAY_BG)
            self.c.roundRect(x, y0, box_w, box_h, 3, fill=1, stroke=0)
            self.c.setFont("WQY", 13)
            self.c.setFillColor(C_TEXT)
            self.c.drawString(x + 3 * mm, y0 + box_h - 8 * mm, big)
            self.c.setFont("WQY", 7.5)
            self.c.setFillColor(C_BODY)
            ty = y0 + box_h - 13 * mm
            for line in wrap_text(self.c, sub, "WQY", 7.5, box_w - 6 * mm):
                self.c.drawString(x + 3 * mm, ty, line)
                ty -= 9
            self.c.setFont("WQY", 6.5)
            self.c.setFillColor(C_MUTED)
            for line in wrap_text(self.c, note, "WQY", 6.5, box_w - 6 * mm):
                self.c.drawString(x + 3 * mm, ty, line)
                ty -= 8
        self.y = y0 - 4 * mm

    def callout(self, title, text, kind="blue"):
        bg = C_BLUE_LIGHT if kind == "blue" else C_GREEN_LIGHT
        pad = 3 * mm
        lines = wrap_text(self.c, text, "WQY", 7.8, CONTENT_W - 2 * pad)
        h = 6 * mm + len(lines) * 10.5 + 2 * mm
        if self.y - h < MARGIN_B + 10 * mm:
            self.new_page()
        y0 = self.y - h
        self.c.setFillColor(bg)
        self.c.roundRect(MARGIN_L, y0, CONTENT_W, h, 3, fill=1, stroke=0)
        self.c.setFont("WQY", 8.5)
        self.c.setFillColor(C_BLUE if kind == "blue" else Color(40 / 255, 110 / 255, 70 / 255))
        self.c.drawString(MARGIN_L + pad, self.y - 4.5 * mm, title)
        self.c.setFont("WQY", 7.8)
        self.c.setFillColor(C_BODY)
        ty = self.y - 9 * mm
        for line in lines:
            self.c.drawString(MARGIN_L + pad, ty, line)
            ty -= 10.5
        self.y = y0 - 3 * mm

    def cards_row(self, cards, height=38 * mm):
        """cards: list of (title, body)"""
        n = len(cards)
        gap = 3 * mm
        box_w = (CONTENT_W - gap * (n - 1)) / n
        y0 = self.y - height
        for i, (title, body) in enumerate(cards):
            x = MARGIN_L + i * (box_w + gap)
            self.c.setFillColor(C_CARD)
            self.c.setStrokeColor(C_LINE)
            self.c.setLineWidth(0.6)
            self.c.roundRect(x, y0, box_w, height, 3, fill=1, stroke=1)
            self.c.setFillColor(C_BLUE)
            self.c.rect(x, y0 + height - 1.2, box_w, 1.2, fill=1, stroke=0)
            self.c.setFont("WQY", 8.5)
            self.c.setFillColor(C_TEXT)
            self.c.drawString(x + 2.5 * mm, y0 + height - 6 * mm, title)
            self.c.setFont("WQY", 7.2)
            self.c.setFillColor(C_BODY)
            ty = y0 + height - 11 * mm
            for line in wrap_text(self.c, body, "WQY", 7.2, box_w - 5 * mm):
                self.c.drawString(x + 2.5 * mm, ty, line)
                ty -= 9.5
        self.y = y0 - 4 * mm

    def table(self, headers, rows, col_ws=None):
        n = len(headers)
        col_ws = col_ws or [CONTENT_W / n] * n
        row_h = 6.2 * mm
        # header
        self.c.setFillColor(C_GRAY_BG)
        self.c.rect(MARGIN_L, self.y - row_h, CONTENT_W, row_h, fill=1, stroke=0)
        self.c.setFont("WQY", 7.5)
        self.c.setFillColor(C_TEXT)
        x = MARGIN_L
        for i, h in enumerate(headers):
            self.c.drawString(x + 1.5 * mm, self.y - row_h + 2 * mm, h)
            x += col_ws[i]
        self.y -= row_h
        self.c.setStrokeColor(C_LINE)
        self.c.setLineWidth(0.3)
        for r_i, row in enumerate(rows):
            # estimate height by wrapping first long cols
            max_lines = 1
            wrapped_cols = []
            for i, cell in enumerate(row):
                lines = wrap_text(self.c, str(cell), "WQY", 7.2, col_ws[i] - 3 * mm)
                wrapped_cols.append(lines)
                max_lines = max(max_lines, len(lines))
            h = max(row_h, max_lines * 9 + 3 * mm)
            if self.y - h < MARGIN_B + 10 * mm:
                self.new_page()
            if r_i % 2 == 1:
                self.c.setFillColor(Color(252 / 255, 252 / 255, 250 / 255))
                self.c.rect(MARGIN_L, self.y - h, CONTENT_W, h, fill=1, stroke=0)
            self.c.setStrokeColor(C_LINE)
            self.c.line(MARGIN_L, self.y - h, MARGIN_L + CONTENT_W, self.y - h)
            x = MARGIN_L
            self.c.setFont("WQY", 7.2)
            self.c.setFillColor(C_BODY)
            for i, lines in enumerate(wrapped_cols):
                ty = self.y - 3.5 * mm
                for line in lines:
                    self.c.drawString(x + 1.5 * mm, ty, line)
                    ty -= 9
                x += col_ws[i]
            self.y -= h
        self.y -= 3 * mm

    def two_col(self, left_title, left_text, right_title, right_text):
        gap = 4 * mm
        col_w = (CONTENT_W - gap) / 2
        y_start = self.y
        # left
        self.c.setFillColor(C_BLUE)
        self.c.rect(MARGIN_L, self.y - 1.2, 3.2, 3.2, fill=1, stroke=0)
        self.c.setFont("WQY", 9.5)
        self.c.setFillColor(C_TEXT)
        self.c.drawString(MARGIN_L + 6, self.y - 1, left_title)
        y_l = self.y - 6 * mm
        self.c.setFont("WQY", 7.8)
        self.c.setFillColor(C_BODY)
        for line in wrap_text(self.c, left_text, "WQY", 7.8, col_w):
            self.c.drawString(MARGIN_L, y_l, line)
            y_l -= 10.5
        # right
        x_r = MARGIN_L + col_w + gap
        self.c.setFillColor(C_BLUE)
        self.c.rect(x_r, self.y - 1.2, 3.2, 3.2, fill=1, stroke=0)
        self.c.setFont("WQY", 9.5)
        self.c.setFillColor(C_TEXT)
        self.c.drawString(x_r + 6, self.y - 1, right_title)
        y_r = self.y - 6 * mm
        self.c.setFont("WQY", 7.8)
        self.c.setFillColor(C_BODY)
        for line in wrap_text(self.c, right_text, "WQY", 7.8, col_w):
            self.c.drawString(x_r, y_r, line)
            y_r -= 10.5
        self.y = min(y_l, y_r) - 3 * mm

    def save(self):
        self._footer()
        self.c.save()


def build(path):
    d = Deck(path)

    # ========== P01 封面导读 ==========
    d.new_page()
    d.c.setFont("WQY", 8)
    d.c.setFillColor(C_MUTED)
    d.c.drawString(MARGIN_L, H - MARGIN_T, "战略汇报材料 · 2026 年 8 月版")
    d.y = H - MARGIN_T - 10 * mm
    d.title("NIMO × 台湾市场", 22)
    d.title("上市 GTM 汇报手册", 22)
    d.y -= 1 * mm
    d.lead(
        "从市场分割、消费者顾虑、竞品格局到四套打法——讲清楚用哪条路径冲击台湾，"
        "以及产品、营销、渠道、价格如何配套。读完应能直接进入决策会：主推哪条、放弃哪条、先谈哪个 KA。"
    )
    d.h2("这本汇报讲什么")
    d.body(
        "台湾智能眼镜已不是「教育品类」阶段。HTC Eagle 占繁中日常摄像心智，Rokid×宝岛占视光有屏柜面，"
        "Even×iNNOHOME 占无摄像 Quiet Tech（3C/电信），Meta 有全球审美却无正规通路。"
        "NIMO 与 Even 产品哲学高度同构——若只喊「无摄像头」，上市即变平替。"
    )
    d.body(
        "本材料给出四套可对比 GTM：A 视光主场（主推）、B 双轨协同、C 电信/3C 对撞（慎用）、D 精品慢火（保底）。"
        "每套覆盖产品 / 营销 / 渠道 / 价格，并附 SWOT 与 90 天里程碑。"
    )
    d.h2("怎么读")
    d.body(
        "顺读约 25 分钟。每页页首导语即结论；蓝色「操盘视角」框是判断句，值得停一下。"
        "方案对照见 P07，主案拆解见 P08–P09，执行清单见 P11。"
    )
    d.cards_row(
        [
            (
                "PART I · 洞察",
                "P02–P05\n市场分割、消费者旅程、竞争对照、SWOT。先对齐「战场在哪、对手是谁」。",
            ),
            (
                "PART II · 打法",
                "P06–P09\n四套 GTM 总览与主推方案 A/B 详解。回答「用什么打、怎么定价铺货」。",
            ),
            (
                "PART III · 落地",
                "P10–P12\n产品营销渠道价格组合、宝岛谈判话术、Go/No-Go 与里程碑。",
            ),
        ],
        height=36 * mm,
    )
    d.h2("读完你能")
    d.body(
        "· 用一张竞争地图向管理层解释：为什么不能学 Even 铺全国电子；\n"
        "· 在宝岛谈判桌上讲清「增量品类」而非「再进一个 AI 镜」；\n"
        "· 锁定价格带原则：含镜套餐透明，避开框+片+戒指与水货比价坑；\n"
        "· 带着北星指标开会：配镜完成率 / NPS / 愿天天戴，而不是门市铺货数。"
    )
    d.callout(
        "数据口径与免责",
        "竞品价格、门店数、融资信息来自公开官宣与媒体报道（截至 2026-08），非审计数据。"
        "本材料供内部战略讨论，不构成投资建议。价格区间为策略建议，落地需财务与法规校准。",
        "blue",
    )

    # ========== P02 决策摘要 ==========
    d.new_page("PART I · 洞察", "决策摘要")
    d.title("先看结论：主推视光主场")
    d.lead(
        "台湾柜面已被三家正规玩家切开。NIMO 的可赢空位不是再铺一套 3C，而是把 Quiet Tech 拉回验光台——"
        "更轻、可门店验配、含镜总价更清楚。"
    )
    d.metrics_row(
        [
            ("4 条赛道", "台湾供给已分割", "摄像 / 视光有屏 / Quiet Tech / 巨幕"),
            ("Even 先手", "2026.8 正规登台", "iNNOHOME：3C+电信+精品"),
            ("宝岛窗口", "Rokid 已教育品类", "可谈第二品牌分品类"),
            ("主推 A", "视光主场打法", "3–6 月后可升双轨 B"),
        ]
    )
    d.h2("已被占位 vs 仍可争取")
    d.table(
        ["位置", "占位者", "对 NIMO 含义"],
        [
            ["繁中日常摄像 AI", "HTC VIVE Eagle", "不正面硬刚语音生态"],
            ["视光有屏（有摄像）", "Rokid × 宝岛", "同柜可分流「隐私日常版」"],
            ["无摄像 Quiet Tech（3C/电信）", "Even G2 × iNNOHOME", "口号已被占，必须换武器"],
            ["视光深度无摄像 HUD", "尚空", "主攻空位：验配+重量+含镜价"],
        ],
        [45 * mm, 55 * mm, CONTENT_W - 100 * mm],
    )
    d.h2("四套打法速览")
    d.cards_row(
        [
            ("A 视光主场 ★", "宝岛等 KA\n含镜套餐\n会议隐私内容\n→ 主推"),
            ("B 双轨协同", "A + 精选 3C\n预约电商\n→ 验证后升级"),
            ("C 电信/3C", "学 Eagle/Even\n专案价冲量\n→ 慎用，易平替"),
            ("D 精品慢火", "8–15 精品店\n高体验控货\n→ KA 卡关保底"),
        ],
        height=32 * mm,
    )
    d.callout(
        "操盘视角",
        "默认路径：A 为骨 → 数据健康后升 B；D 作谈判保底；C 最多做局部体验，绝不作品牌定义战役。"
        "北星看配镜完成率与愿天天戴，不看第一个月铺了多少全国电子柜。",
        "blue",
    )

    # ========== P03 市场洞察 ==========
    d.new_page("PART I · 洞察", "市场洞察")
    d.title("市场：分割完毕，后发者要选缝")
    d.lead(
        "全球品类在放量，台湾本地已完成「正规货 + 水货 + 影音 AR」分层。"
        "消费者问的不再是有没有，而是正不正规、配不配度数、敢不敢天天戴。"
    )
    d.metrics_row(
        [
            ("赛道 B", "NIMO 主战场", "轻显示 HUD：字幕/提词/导航"),
            ("~1.6万", "Eagle 心智锚", "正规入门 AI 镜价格带"),
            ("~2.0万", "Rokid / Even", "有显示旗舰带常用成交"),
            ("高度近视", "台湾刚需底色", "验配不是可选项"),
        ]
    )
    d.two_col(
        "三条赛道，勿混战",
        "A 日常摄像 AI：Eagle / Meta 水货——听与拍。\n"
        "B 轻显示 HUD：Rokid / Even /（NIMO）——看得见信息。\n"
        "C 影音巨幕：RayNeo / XREAL / VITURE——追剧掌机，与配镜决策弱相关。\n\n"
        "NIMO 只打 B，且要落在「隐私/静默显示」细分；不进 C，不与 Eagle 拼语音助理。",
        "渠道结构在说什么",
        "视光连锁（宝岛）：处方、信任、复购——Even 尚未深绑。\n"
        "电信（台哥大）：体验密度、绑约降门槛——Eagle/Even 已用。\n"
        "综合 3C（全国电子）：看见与试用——Even 主铺货场。\n"
        "精品（法雅客/诚品）：调性种草。\n"
        "电商（momo）：比价与预约。\n\n"
        "后发最优切口仍是视光深度，不是再铺一套 3C。",
    )
    d.h2("价格带心智（2026）")
    d.table(
        ["价格带（TWD）", "代表", "消费者解读", "NIMO 策略"],
        [
            ["1.5–1.6 万", "Eagle 主销", "正规入门", "含镜套餐可落此带或略上"],
            ["~2.0 万", "Rokid / Even G2", "有显示旗舰", "总拥有成本对照，不裸拼"],
            ["0.9–1.8 万", "Meta/小米水货", "便宜但不保", "打正规+售后，不跟破价"],
            ["0.8–3.5 万", "影音 AR", "另一品类", "不进入横评场"],
        ],
        [32 * mm, 38 * mm, 40 * mm, CONTENT_W - 110 * mm],
    )
    d.callout(
        "市场判断",
        "品类教育已被 Rokid×宝岛与 Eagle 做完；Even 把「无摄像」变成可购买的正规选项。"
        "NIMO 进场买的不是科普预算，而是差异化柜面与验配信任。",
        "green",
    )

    # ========== P04 消费者洞察 ==========
    d.new_page("PART I · 洞察", "消费者洞察")
    d.title("消费者：要的是本命镜，不是又一台 3C")
    d.lead(
        "Jobs-to-be-done：换一副能天天戴的近视镜，让必要信息出现在眼前——"
        "但不要拍别人，也不要看起来像戴了电子设备。"
    )
    d.h2("优先人群")
    d.table(
        ["人群", "动机", "顾虑", "NIMO 钩子"],
        [
            ["办公/会议族 28–45", "提词、过滤通知", "摄像头、漏音", "无摄像+静默 HUD"],
            ["高度近视换镜族", "反正要配新镜", "重、丑、配不准", "29g+验配当本命镜"],
            ["跨境/双语用户", "翻译字幕", "只靠「念出来」", "看得见的翻译"],
            ["反感水货的尝鲜者", "跟全球潮流", "Meta 无保固", "正规通路+本地售后"],
        ],
        [38 * mm, 38 * mm, 35 * mm, CONTENT_W - 111 * mm],
    )
    d.h2("决策旅程与槽点（设计输入）")
    d.body(
        "内容种草（YouTube / Mobile01 / IG）→ 核对恐惧点（隐私？度数？保固？）→ 想试戴 → "
        "关键成交：验光是否专业、能否短期取镜 → 私域复购。\n\n"
        "论坛高频槽点：电信店锁链试戴/尺寸不全；有摄像不敢进会议室；Even 处方实验室交期长；"
        "框+片+戒指总价不透明。每一条都对应 NIMO 可设计的体验优势。"
    )
    d.callout(
        "操盘视角",
        "营销不要教育「什么是 AI 眼镜」（别人已教育完），要回答三句："
        "敢不敢戴进会议室？能不能当每天那副镜？含镜到底多少钱？",
        "blue",
    )
    d.cards_row(
        [
            ("恐惧", "被拍摄\n配不准\n坏了没保"),
            ("欲望", "少掏手机\n翻译提词\n外型正常"),
            ("信任锚", "验光师\n连锁背书\n本地售后"),
            ("成交杠杆", "当场试戴\n含镜套餐\n取镜时效"),
        ],
        height=28 * mm,
    )

    # ========== P05 竞争洞察 ==========
    d.new_page("PART I · 洞察", "竞争洞察")
    d.title("竞争：主敌 Even 与同柜 Rokid")
    d.lead(
        "Eagle 是心智对照组，Meta 是舆论对照组；真正会抢走定位与柜面的，是 Even（同哲学）和 Rokid（同店）。"
    )
    d.table(
        ["对手", "他强在哪", "他弱在哪", "NIMO 怎么打"],
        [
            ["Even G2", "Quiet Tech 心智、已上市、全球高端叙事", "3C 为主、处方中心制、总价易上冲", "视光主场+更轻+含镜套餐"],
            ["Rokid@宝岛", "验配网、字幕场景、宝岛背书", "有摄像、更重、价高", "同店讲隐私日常版，分流"],
            ["HTC Eagle", "繁中、门市密度、本土情感", "无显示屏", "不拼语音，拼看得见"],
            ["Meta 水货", "外型心智", "无保、难验配", "正规化对照"],
        ],
        [28 * mm, 48 * mm, 48 * mm, CONTENT_W - 124 * mm],
    )
    d.h2("Even 登台的渠道含义（必须读懂）")
    d.body(
        "iNNOHOME 独家 + 全国电子 / 法雅客 / 诚品 / momo / 台哥大 = 标准「消费电子代理商打法」："
        "解决看得到、买得到、专案价带回家，并不默认解决验光与处方调校。"
        "全国电子≈综合 3C 前二；法雅客≈百货精品 3C；诚品≈生活风格；momo≈本土电商龙头；台哥大≈绑约降门槛。"
    )
    d.callout(
        "竞争结论",
        "Even 证明无摄像路线可卖且已占 3C/电信；NIMO 若跟着铺全国电子，将在同质货架上打价格。"
        "应把战场挪到宝岛验光台，让对比维度变成重量 / 交期 / 含镜总价 / 门店服务。",
        "green",
    )

    # ========== P06 SWOT ==========
    d.new_page("PART I · 洞察", "SWOT")
    d.title("优劣势：牌够打，但不能靠口号")
    d.lead("优势集中在产品物理与验配基因；劣势是台湾零品牌资产。机会在 Even 未深绑视光；威胁是叙事被收编为平替。")
    d.cards_row(
        [
            (
                "S 优势",
                "无摄像+HUD 与全球空位同向\n约 29g 重量可感知差异\n含配镜价值锚可迁移\n适配眼镜店旅程",
            ),
            (
                "W 劣势",
                "台湾零品牌资产\n繁中 App/售后/认证待补\n无电信级门市密度\n无摄像差异被 Even 稀释",
            ),
            (
                "O 机会",
                "宝岛可谈分品类第二品牌\n隐私与全天戴槽点真实\nEven 未占视光主场\n企业/校园合规场景",
            ),
            (
                "T 威胁",
                "Even 专案价固化心智\n宝岛排他加深\n水货拉低价格预期\n处方良率翻车伤连锁",
            ),
        ],
        height=42 * mm,
    )
    d.h2("由此导出的战略约束")
    d.body(
        "1）对外主信息不能只剩「无摄像头」——必须绑定更轻 / 门店验配 / 含镜透明。\n"
        "2）组织资源向视光 KA 与培训售后倾斜，而不是向 3C 铺货人数倾斜。\n"
        "3）上市前 Go/No-Go：认证、繁中 App、处方 SLA、至少一家 KA MOU，四项缺一不上量。\n"
        "4）公关禁止「吊打 Meta / Even 山寨」；只做结构对照。"
    )
    d.callout(
        "操盘视角",
        "SWOT 不是平衡表，是资源分配指令：每一分营销预算，优先用于验光师内容与门店体验，"
        "而不是用于和 Even 比谁更 Quiet Tech。",
        "blue",
    )

    # ========== P07 四套打法总览 ==========
    d.new_page("PART II · 打法", "GTM 总览")
    d.title("四套打法：选缝，而不是选热闹")
    d.lead("四套方案都能「上市」，但只有 A/B 能定义品牌；C 能起量却易毁掉定位；D 适合卡关时保活。")
    d.table(
        ["维度", "A 视光主场", "B 双轨", "C 电信3C", "D 精品慢火"],
        [
            ["品牌定义", "本命智能近视镜", "同上+破圈", "数码新品", "精品科技镜"],
            ["主竞品", "Even / Rokid", "Even", "Even / Eagle", "Even"],
            ["起量速度", "中", "中快", "快", "慢"],
            ["毛利质量", "高", "中高", "低", "高"],
            ["口碑风险", "中（可控）", "中", "高", "低"],
            ["与宝岛契合", "最强", "强", "弱", "中"],
            ["推荐", "主推", "升级", "慎用", "保底"],
        ],
        [28 * mm, 32 * mm, 28 * mm, 28 * mm, CONTENT_W - 116 * mm],
    )
    d.h2("推荐路径")
    d.body(
        "采用 A 作为上市主案 → 3–6 个月转化与 NPS 达标后启用 B（精选精品 3C + momo 预约）→ "
        "全程保留 D 作为 KA 谈判备胎 → C 仅局部体验/员工购，不扛 KPI。"
    )
    d.cards_row(
        [
            ("定位句", "无摄像头、轻到忘记的智能近视镜。信息只在需要时出现——在眼镜门市完成专业验配。"),
            ("价格原则", "含基础配镜套餐清晰公示；做总拥有成本对照；MAP 纪律；电商预约核销。"),
            ("北星指标", "配镜完成率 · 试戴转化 · NPS · 店均月销与功能片连带 · 非门市铺货数"),
        ],
        height=34 * mm,
    )

    # ========== P08 方案 A ==========
    d.new_page("PART II · 打法", "方案 A")
    d.title("方案 A｜视光主场（主推）")
    d.lead(
        "把 NIMO 做成能在验光台上成交的本命智能近视镜——用宝岛打穿 Even 的 3C 优势，用无摄像打穿 Rokid 的隐私短板。"
    )
    d.h2("产品")
    d.body(
        "主 SKU：标准款含基础单光套餐 + 门店 Demo。增值：防蓝光/变色/偏光。"
        "本地化：繁中 App、通知白名单、会议/捷运/旅行场景预设。"
        "服务包：验配 + 14 天舒适调整 + 硬件保修，序列号绑门店。"
        "首发不做影音巨幕配件，不做复杂企业套装。"
        "话术铁律：不是多买一台 3C，是升级你每天那副眼镜。"
    )
    d.h2("价格")
    d.metrics_row(
        [
            ("1.3–1.6万", "含镜套餐建议带", "低于 Rokid/Even 裸机心智或与 Eagle 同带有屏"),
            ("升级片", "门店加价公示", "功能片利润池留给 KA"),
            ("对照页", "总拥有成本", "NIMO 含镜 vs Even 框+片+R1"),
            ("MAP", "价格纪律", "电商预约核销，不长期破价"),
        ]
    )
    d.h2("渠道节奏")
    d.body(
        "0–3 月：宝岛（优先）或同等连锁 20–40 标杆店，每店认证验光师 ≥2。"
        "3–9 月：加密至 80–120，策略联盟店分级导入。"
        "并行：官网/LINE 预约到店。明确不做主 KPI：电信绑约冲量。"
        "门店旅程 25–35 分钟：问诊隐私场景 → 验光瞳距 → 三场景试戴 → 含镜方案 → 会员建档。"
    )
    d.h2("营销")
    d.body(
        "大创意本地化：「会议室也敢戴的智能近视镜」。"
        "必打三条片：会议无摄像 / 全天无压痕 / 验光师讲为何要验配。"
        "媒体走科技+眼镜产业，避免巨幕横评场；论坛要 Mobile01/ePrice 真实长测；"
        "KOL 偏验光师与职场创作者。与宝岛会员积分、校园/企业巡展联动。"
    )
    d.callout(
        "90 天里程碑",
        "标杆店就绪与认证通过率 ≥90%；试戴→成交与配镜完成率达标；NPS 与重大售后 7 日关闭率达标；"
        "是否进入 KA 下一季主推清单。",
        "green",
    )

    # ========== P09 方案 B/C/D ==========
    d.new_page("PART II · 打法", "方案 B / C / D")
    d.title("其余三套：升级、陷阱与保底")
    d.lead("B 是 A 的放大器；C 是定位陷阱；D 是谈判保底。资源不够时只做 A+D。")
    d.h2("方案 B｜双轨协同")
    d.body(
        "战略：眼镜店负责赚钱与口碑，精选 3C/内容负责让人知道「还有比 Even 更适合配镜的无摄像镜」。"
        "增加 Plano 展示款供精品柜；包装印预约验配码。"
        "价格上 3C 硬件价不得挖空眼镜店含镜套餐。"
        "渠道辅线仅法雅客/诚品级控量体验 + momo 预约页，不对撞全国电子+台哥大全面铺货。"
        "启用条件：A 试点转化健康，且备机池与繁中增长团队到位。"
    )
    d.h2("方案 C｜电信/3C 对撞（不建议主路径）")
    d.body(
        "学 Eagle/Even 用密度与专案价起量：产品偏无度数、价格打到数千、营销偏促销。"
        "风险：丢掉本命近视镜定义，与 Even 同柜同质，毛利与品牌双杀。"
        "结论：可做局部城市曝光或员工购，不能作为品牌定义战役。"
    )
    d.h2("方案 D｜精品慢火")
    d.body(
        "8–15 家精品眼镜店高体验控货；价格可略高于 A；营销走小圈长测。"
        "适用：KA 谈判卡关时的过渡，或 A 之外的高端补充线。"
    )
    d.cards_row(
        [
            ("B 何时上", "A 的配镜完成率与 NPS 达标\n再开精品柜与预约电商"),
            ("C 红线", "不承诺电信主销量\n不用专案价定义品牌"),
            ("D 价值", "保住验配叙事\n并行接触第二连锁"),
        ],
        height=30 * mm,
    )
    d.callout(
        "操盘视角",
        "最常见误判：一上市就「全通路铺开」。在台湾当前格局下，全通路≈把自己扔进 Even 的战场。"
        "先赢验光台，再谈破圈。",
        "blue",
    )

    # ========== P10 组合执行 ==========
    d.new_page("PART III · 落地", "产品·营销·渠道·价格")
    d.title("主推组合：A 为骨，B 为翼")
    d.lead("把四套选择收束成一套可执行的上市组合：定义、价格、渠道、营销、预算同向。")
    d.h2("产品 × 价格")
    d.table(
        ["模块", "动作", "原则"],
        [
            ["主售", "含基础单光套餐的 NIMO 标准款", "货架上先看到「能戴出门的镜」"],
            ["Demo", "每标杆店体验机+场景脚本", "5–8 分钟三场景：导航/提词/翻译"],
            ["增值", "功能片升级包", "利润与专业感留给门店"],
            ["价格锚", "含镜套餐 1.3–1.6 万带（策略区间）", "对照 Even/Rokid 总价，不跟水货"],
            ["纪律", "MAP + 序列号区域", "破价停货"],
        ],
        [28 * mm, 70 * mm, CONTENT_W - 98 * mm],
    )
    d.h2("渠道 × 营销")
    d.two_col(
        "渠道",
        "主：宝岛或同等 KA 标杆店加密。\n"
        "辅（后期）：诚品/法雅客级体验柜、momo 预约验配。\n"
        "禁：以全国电子+电信专案作为品牌主叙事。\n"
        "系统：门店工单、序列号、会员度数档案。",
        "营销",
        "主信息：会议室也敢戴 / 轻到忘记 / 验配完成。\n"
        "预算示意：门店体验培训 30%、内容论坛 25%、KA 联合 25%、公关 10%、售后预备 10%。\n"
        "禁止参数战与竞品羞辱。",
    )
    d.h2("六个月节奏")
    d.table(
        ["月份", "重点"],
        [
            ["M0", "KA 签约、体验桌、媒体闭门、培训认证"],
            ["M1", "会员软开业 → 正式开卖"],
            ["M2–M3", "转化优化、差评闭环、第二批店"],
            ["M4–M5", "开启 B：精选体验柜 + momo 预约"],
            ["M6", "复盘扩岛 / 第二连锁"],
        ],
        [28 * mm, CONTENT_W - 28 * mm],
    )

    # ========== P11 宝岛与话术 ==========
    d.new_page("PART III · 落地", "KA 与话术")
    d.title("宝岛谈判与对外话术弹药")
    d.lead(
        "对宝岛不谈「再进一个 AI 镜」，谈「把 Quiet Tech 从数码柜拉回验光台」的增量品类与客单结构。"
    )
    d.h2("给宝岛的一句话")
    d.callout(
        "谈判句",
        "宝岛用 Rokid 打下「看得见的 AI」；HTC 打下「听得懂繁中」；Even 已在 3C/电信占「无摄像 Quiet Tech」。"
        "NIMO 给的增量是：视光主场上的无摄像日常镜——更轻、可门店验配、含镜更亲民。",
        "blue",
    )
    d.h2("商务框架要点")
    d.body(
        "试点 20–40 店 → 数据说话再加密；争取「无摄像 HUD 日常镜」品类优先而非盲目全品类独家；"
        "寄售或小批量+滚动；阶梯返利绑标杆店；品牌方担硬件保修、门店做初检代送修；"
        "培训认证不合格不下放销售权；月度联合经营会看转化/退货/热销度数。"
    )
    d.h2("30 秒电梯稿与三句区隔")
    d.body(
        "电梯稿：Meta 们在拍你的世界；Even 证明不拍也可以很贵。NIMO 走第三条——"
        "和普通近视镜一样轻，在眼镜店完成验配，信息静默出现在眼前。\n\n"
        "vs Even：同样重视隐私；我们更轻，门市当场验配，总价含镜更清楚。\n"
        "vs Rokid：同样看得见信息；我们去掉摄像头，适合当每天的本命镜。\n"
        "vs Eagle：同样在地服务；我们多一块只给你看的显示，翻译提词不用听着记。"
    )
    d.callout(
        "禁止话术",
        "Even 山寨/抄袭；吊打 Meta；不用验光也能完美。结构对照可以，羞辱战不行。",
        "green",
    )

    # ========== P12 Go/No-Go ==========
    d.new_page("PART III · 落地", "清单与建议")
    d.title("Go / No-Go 与最终建议")
    d.lead("没有清单的上市叫发布会；有清单的上市叫操盘。以下任一红灯，应推迟上量。")
    d.h2("上市前清单")
    d.table(
        ["项", "Go 标准"],
        [
            ["合规", "NCC/BSMI 等必要认证到手"],
            ["软件", "繁中 App 稳定，核心场景可用"],
            ["供应", "处方交期 SLA 书面化，备机池到位"],
            ["渠道", "至少 1 家视光 KA MOU + 首批店清单"],
            ["价格", "含镜套餐与对照页通过财务审核"],
            ["培训", "TOT 完成，神秘客脚本就绪"],
        ],
        [28 * mm, CONTENT_W - 28 * mm],
    )
    d.h2("风险与应对")
    d.table(
        ["风险", "应对"],
        [
            ["被叫 Even 平替", "首月集中打重量实测、验配 Vlog、总价对照"],
            ["宝岛谈不拢", "启动 D + 平行接触第二连锁"],
            ["处方交期爆", "常见度数快配清单；超时补偿"],
            ["3C 窜货破价", "序列号区域锁 + 停货"],
            ["繁中差评", "每周 OTA + 论坛值班"],
        ],
        [40 * mm, CONTENT_W - 40 * mm],
    )
    d.h2("决策会五句话")
    d.body(
        "1. 采用方案 A 作上市主案，资源向视光 KA 倾斜。\n"
        "2. 预留 B 的内容与 Plano SKU，3C 必须控量从属。\n"
        "3. 拒绝以 C 定义品牌；电信最多做体验点。\n"
        "4. 价格打含镜透明套餐，避开 Even 加价结构与水货比价。\n"
        "5. 北星看验配完成与愿意天天戴——不是铺了多少 3C 柜。"
    )
    d.callout(
        "一页纸收束",
        "A 视光主场：宝岛 20–40 店 → 含镜套餐 → 会议隐私内容 → 验配 SOP。"
        "路径：A →（验证后）B；D 保底；C 慎用。"
        "定位：无摄像头、轻到忘记的智能近视镜——在眼镜门市完成专业验配。",
        "blue",
    )

    d.save()
    print("wrote", path)


if __name__ == "__main__":
    out = "/workspace/docs/nimo-smart-glasses/NIMO台湾上市GTM汇报手册.pdf"
    build(out)
