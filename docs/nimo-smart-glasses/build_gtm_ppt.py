#!/usr/bin/env python3
"""NIMO 台湾上市 GTM — 横版密排汇报 PDF（少留白）"""

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import Color

pdfmetrics.registerFont(TTFont("WQY", "/tmp/wqy-microhei.ttf"))

W, H = landscape(A4)  # 841.89 x 595.28
MARGIN_L = 8 * mm
MARGIN_R = 8 * mm
MARGIN_T = 7 * mm
MARGIN_B = 7 * mm
CONTENT_W = W - MARGIN_L - MARGIN_R
CONTENT_H = H - MARGIN_T - MARGIN_B

C_TEXT = Color(11 / 255, 11 / 255, 11 / 255)
C_BODY = Color(70 / 255, 70 / 255, 68 / 255)
C_MUTED = Color(120 / 255, 118 / 255, 112 / 255)
C_BLUE = Color(28 / 255, 92 / 255, 171 / 255)
C_BLUE_LIGHT = Color(228 / 255, 238 / 255, 249 / 255)
C_GREEN_LIGHT = Color(228 / 255, 242 / 255, 232 / 255)
C_GRAY_BG = Color(242 / 255, 242 / 255, 240 / 255)
C_LINE = Color(210 / 255, 210 / 255, 206 / 255)
C_CARD = Color(248 / 255, 248 / 255, 246 / 255)
C_ORANGE_BG = Color(255 / 255, 244 / 255, 230 / 255)

DOC_TITLE = "NIMO 智能眼镜 · 台湾上市 GTM 汇报"
DOC_VER = "2026.08 · V1.0 · 横版"


def wrap_text(c, text, font, size, max_w):
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
        self.c = canvas.Canvas(path, pagesize=landscape(A4))
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
        # top bar
        self.c.setFillColor(C_GRAY_BG)
        self.c.rect(0, H - 6.2 * mm, W, 6.2 * mm, fill=1, stroke=0)
        self.c.setFont("WQY", 7)
        self.c.setFillColor(C_MUTED)
        label = " / ".join(x for x in [self.part, self.section] if x) or "NIMO × 台湾 GTM"
        self.c.drawString(MARGIN_L, H - 4.2 * mm, label)
        self.c.drawRightString(W - MARGIN_R, H - 4.2 * mm, f"{DOC_VER}")
        self.y = H - MARGIN_T - 1.5 * mm

    def _footer(self):
        self.c.setFillColor(C_GRAY_BG)
        self.c.rect(0, 0, W, 5.5 * mm, fill=1, stroke=0)
        self.c.setFont("WQY", 6.5)
        self.c.setFillColor(C_MUTED)
        self.c.drawString(MARGIN_L, 1.8 * mm, DOC_TITLE)
        self.c.drawRightString(W - MARGIN_R, 1.8 * mm, f"{self.page:02d}")

    def title(self, text, size=14):
        self.c.setFont("WQY", size)
        self.c.setFillColor(C_TEXT)
        self.c.drawString(MARGIN_L, self.y, text)
        self.y -= size * 1.15 + 1.2 * mm

    def lead(self, text, size=8):
        self.c.setFont("WQY", size)
        self.c.setFillColor(C_BODY)
        for line in wrap_text(self.c, text, "WQY", size, CONTENT_W):
            self.c.drawString(MARGIN_L, self.y, line)
            self.y -= size + 2.2
        self.y -= 1.2 * mm

    def h2(self, text, x=None, y=None):
        x = MARGIN_L if x is None else x
        if y is not None:
            self.y = y
        self.c.setFillColor(C_BLUE)
        self.c.rect(x, self.y - 0.8, 2.8, 2.8, fill=1, stroke=0)
        self.c.setFont("WQY", 9)
        self.c.setFillColor(C_TEXT)
        self.c.drawString(x + 5, self.y - 0.6, text)
        self.y -= 4.8 * mm

    def body_at(self, text, x, y, width, size=7.2, leading=9.2, color=C_BODY):
        self.c.setFont("WQY", size)
        self.c.setFillColor(color)
        ty = y
        for line in wrap_text(self.c, text, "WQY", size, width):
            self.c.drawString(x, ty, line)
            ty -= leading
        return ty

    def metrics_row(self, items, y=None, height=16 * mm):
        if y is not None:
            self.y = y
        n = len(items)
        gap = 2 * mm
        box_w = (CONTENT_W - gap * (n - 1)) / n
        y0 = self.y - height
        for i, (big, sub, note) in enumerate(items):
            x = MARGIN_L + i * (box_w + gap)
            self.c.setFillColor(C_GRAY_BG)
            self.c.roundRect(x, y0, box_w, height, 2, fill=1, stroke=0)
            self.c.setFillColor(C_BLUE)
            self.c.rect(x, y0 + height - 1.5, box_w, 1.5, fill=1, stroke=0)
            self.c.setFont("WQY", 11)
            self.c.setFillColor(C_TEXT)
            self.c.drawString(x + 2.2 * mm, y0 + height - 6.5 * mm, big)
            self.c.setFont("WQY", 6.8)
            self.c.setFillColor(C_BODY)
            ty = y0 + height - 10.5 * mm
            for line in wrap_text(self.c, sub, "WQY", 6.8, box_w - 4.5 * mm)[:2]:
                self.c.drawString(x + 2.2 * mm, ty, line)
                ty -= 8.2
            self.c.setFont("WQY", 6)
            self.c.setFillColor(C_MUTED)
            for line in wrap_text(self.c, note, "WQY", 6, box_w - 4.5 * mm)[:2]:
                self.c.drawString(x + 2.2 * mm, ty, line)
                ty -= 7.5
        self.y = y0 - 2 * mm
        return self.y

    def filled_box(self, x, y, w, h, title, body, bg=C_CARD, title_color=C_TEXT, body_size=6.8):
        self.c.setFillColor(bg)
        self.c.setStrokeColor(C_LINE)
        self.c.setLineWidth(0.5)
        self.c.roundRect(x, y, w, h, 2, fill=1, stroke=1)
        self.c.setFillColor(C_BLUE)
        self.c.rect(x, y + h - 1.2, w, 1.2, fill=1, stroke=0)
        self.c.setFont("WQY", 7.5)
        self.c.setFillColor(title_color)
        self.c.drawString(x + 2 * mm, y + h - 5.2 * mm, title)
        self.c.setFont("WQY", body_size)
        self.c.setFillColor(C_BODY)
        ty = y + h - 9.2 * mm
        for line in wrap_text(self.c, body, "WQY", body_size, w - 4 * mm):
            if ty < y + 2 * mm:
                break
            self.c.drawString(x + 2 * mm, ty, line)
            ty -= body_size + 2.0

    def callout_bar(self, title, text, kind="blue", height=11 * mm):
        bg = C_BLUE_LIGHT if kind == "blue" else (C_GREEN_LIGHT if kind == "green" else C_ORANGE_BG)
        y0 = self.y - height
        self.c.setFillColor(bg)
        self.c.roundRect(MARGIN_L, y0, CONTENT_W, height, 2, fill=1, stroke=0)
        self.c.setFont("WQY", 7.5)
        tc = C_BLUE if kind == "blue" else (Color(35 / 255, 100 / 255, 65 / 255) if kind == "green" else Color(160 / 255, 90 / 255, 20 / 255))
        self.c.setFillColor(tc)
        self.c.drawString(MARGIN_L + 2.5 * mm, y0 + height - 4 * mm, title)
        self.c.setFont("WQY", 6.8)
        self.c.setFillColor(C_BODY)
        ty = y0 + height - 7.8 * mm
        for line in wrap_text(self.c, text, "WQY", 6.8, CONTENT_W - 5 * mm)[:3]:
            self.c.drawString(MARGIN_L + 2.5 * mm, ty, line)
            ty -= 8.2
        self.y = y0 - 1.5 * mm

    def table(self, headers, rows, col_ws=None, row_h=5.4 * mm, font=6.6):
        n = len(headers)
        col_ws = col_ws or [CONTENT_W / n] * n
        # header
        self.c.setFillColor(C_BLUE)
        self.c.rect(MARGIN_L, self.y - row_h, CONTENT_W, row_h, fill=1, stroke=0)
        self.c.setFont("WQY", font)
        self.c.setFillColor(Color(1, 1, 1))
        x = MARGIN_L
        for i, h in enumerate(headers):
            self.c.drawString(x + 1.2 * mm, self.y - row_h + 1.6 * mm, h)
            x += col_ws[i]
        self.y -= row_h
        for r_i, row in enumerate(rows):
            wrapped = []
            max_lines = 1
            for i, cell in enumerate(row):
                lines = wrap_text(self.c, str(cell), "WQY", font, col_ws[i] - 2.4 * mm)
                wrapped.append(lines)
                max_lines = max(max_lines, len(lines))
            h = max(row_h, max_lines * (font + 1.8) + 2.2 * mm)
            if r_i % 2 == 0:
                self.c.setFillColor(C_GRAY_BG)
                self.c.rect(MARGIN_L, self.y - h, CONTENT_W, h, fill=1, stroke=0)
            else:
                self.c.setFillColor(C_CARD)
                self.c.rect(MARGIN_L, self.y - h, CONTENT_W, h, fill=1, stroke=0)
            x = MARGIN_L
            self.c.setFont("WQY", font)
            self.c.setFillColor(C_BODY)
            for i, lines in enumerate(wrapped):
                ty = self.y - 2.8 * mm
                for line in lines:
                    self.c.drawString(x + 1.2 * mm, ty, line)
                    ty -= font + 1.8
                x += col_ws[i]
            self.y -= h
        self.y -= 1.5 * mm

    def save(self):
        self._footer()
        self.c.save()


def build(path):
    d = Deck(path)
    c = d.c
    gap = 2.2 * mm

    # ========== P01 封面+决策 ==========
    d.new_page("封面", "决策摘要")
    d.title("NIMO × 台湾市场｜上市 GTM 汇报（横版密排）", 13)
    d.lead(
        "台湾柜面已被切成四块：Eagle 占繁中摄像日常｜Rokid×宝岛占视光有屏｜Even×iNNOHOME 占无摄像 Quiet Tech（3C/电信）｜Meta 有心智无正规。"
        "NIMO 与 Even 哲学同构——只喊「无摄像头」即变平替。主推：视光主场（A）→ 验证后双轨（B）；电信/3C 对撞（C）慎用。"
    )
    d.metrics_row(
        [
            ("主推 A", "视光主场打法", "宝岛等 KA · 含镜套餐"),
            ("升 B", "3–6 月后双轨", "精品 3C + 预约电商"),
            ("慎用 C", "电信/3C 对撞", "易成 Even 平替"),
            ("保底 D", "精品慢火", "KA 卡关时过渡"),
            ("北星", "配镜完成/NPS", "非 3C 铺货数"),
        ],
        height=15 * mm,
    )

    # three columns stretch to callout
    callout_h = 10 * mm
    col_w = (CONTENT_W - 2 * gap) / 3
    y0 = MARGIN_B + 5.5 * mm + callout_h + 1.5 * mm
    box_h = d.y - y0
    d.filled_box(
        MARGIN_L,
        y0,
        col_w,
        box_h,
        "已被占位",
        "· 繁中摄像日常 → HTC Eagle（台哥大+眼镜伙伴）\n"
        "· 视光有屏有摄像 → Rokid×宝岛（~NT$19,999）\n"
        "· 无摄像 Quiet Tech → Even G2×iNNOHOME（全国电子/法雅客/诚品/momo/台哥大）\n"
        "· 全球时尚心智 → Meta 水货（无保固难验配）\n"
        "· 影音巨幕 → RayNeo/XREAL/VITURE（非日常镜）\n"
        "含义：教育已被做完；后发者买的是缝，不是热闹。",
        C_BLUE_LIGHT,
    )
    d.filled_box(
        MARGIN_L + col_w + gap,
        y0,
        col_w,
        box_h,
        "仍可争夺的空位",
        "· 视光连锁深度的无摄像 HUD（Even 未占宝岛主场）\n"
        "· ≤30g + 含配镜更亲民正规价\n"
        "· 门店即时验配 vs Even 实验室邮寄\n"
        "· 「会议室也敢戴」的本命近视镜叙事\n"
        "→ 武器=更轻+验配+含镜透明，不是复读无摄像头\n"
        "→ 对宝岛谈分品类增量，不谈再进一个AI镜",
        C_GREEN_LIGHT,
    )
    d.filled_box(
        MARGIN_L + 2 * (col_w + gap),
        y0,
        col_w,
        box_h,
        "默认决策",
        "1. 资源向视光 KA/培训售后倾斜\n"
        "2. 价格打含镜套餐 1.3–1.6 万带（策略）\n"
        "3. 对宝岛谈「分品类增量」非再进一个 AI 镜\n"
        "4. C 最多局部体验，不作品牌定义\n"
        "5. Go 条件：认证+繁中App+处方SLA+KA MOU\n"
        "6. 路径固定：A→B；D保底；C不扛KPI",
        C_ORANGE_BG,
    )
    d.y = y0 - 1.5 * mm
    d.callout_bar(
        "操盘视角",
        "路径：A 为骨 → 数据健康升 B；D 保底；C 不扛 KPI。北星=配镜完成率·愿天天戴·NPS，不是全国电子柜面数。",
        "blue",
        callout_h,
    )

    # ========== P02 市场+消费者 ==========
    d.new_page("PART I · 洞察", "市场 × 消费者")
    d.title("市场分割 × 消费者 JTBD：要本命镜，不要又一台 3C", 12.5)
    left_w = CONTENT_W * 0.48
    right_w = CONTENT_W * 0.50
    x_r = MARGIN_L + left_w + gap

    # 左右等高铺满：上区到指标条之上
    band_bottom = MARGIN_B + 5.5 * mm + 14 * mm + 2 * mm + 10 * mm + 2 * mm  # footer+metrics+callout
    band_top = d.y
    mid_h = band_top - band_bottom - 2 * mm
    # left stack as one tall box + embedded mini tables drawn inside
    d.filled_box(
        MARGIN_L,
        band_bottom + 14 * mm + 12 * mm,
        left_w,
        mid_h - 14 * mm - 12 * mm,
        "市场：三条赛道勿混战 + 价格带",
        "赛道A 摄像日常｜Eagle/Meta水货 → NIMO不硬刚\n"
        "赛道B 轻显示HUD｜Rokid/Even/NIMO → 主战场\n"
        "赛道C 影音巨幕｜RayNeo/XREAL/VITURE → 不进入\n"
        "———— 价格带心智 ————\n"
        "1.5–1.6万 Eagle＝正规入门｜~2.0万 Rokid/Even＝有显示旗舰\n"
        "0.9–1.8万 水货＝便宜不保｜影音0.8–3.5万＝另一品类横评场不进\n"
        "渠道含义：视光=处方信任｜电信=绑约密度｜3C=看见试用｜精品=调性｜电商=预约\n"
        "Even已占3C+电信+精品；后发最优切口=视光深度，不是再铺全国电子。",
        C_GRAY_BG,
        body_size=6.6,
    )
    d.filled_box(
        x_r,
        band_bottom + 14 * mm + 12 * mm,
        right_w,
        mid_h - 14 * mm - 12 * mm,
        "消费者 JTBD / 人群 / 旅程槽点",
        "JTBD：换一副能天天戴的近视镜，必要信息出现在眼前——不要拍别人，不要像电子设备。\n"
        "· 办公会议族：提词/过滤 → 怕摄像漏音 → 无摄像静默HUD\n"
        "· 高度近视换镜：反正要配 → 怕重丑不准 → 29g+验配本命镜\n"
        "· 双语跨境：要字幕 → 讨厌只「念出来」 → 看得见的翻译\n"
        "· 反感水货尝鲜：要正规 → Meta无保 → 本地售后\n"
        "旅程：种草→恐隐私/度数/保固→试戴→验光专业与取镜时效=成交点\n"
        "槽点：电信锁链试戴差｜会议室不敢戴摄像｜Even交期长｜总价不透明\n"
        "营销只答三句：会议室敢戴？能当本命镜？含镜到底多少钱？",
        C_CARD,
        body_size=6.6,
    )
    d.y = band_bottom + 14 * mm + 10 * mm
    d.metrics_row(
        [
            ("高度近视", "台湾刚需底色", "验配非可选项"),
            ("Even渠道", "3C+电信+精品", "未深绑视光连锁"),
            ("宝岛窗口", "Rokid已教育", "可谈第二品牌分品类"),
            ("营销焦点", "三句问答", "会议室？本命镜？含镜价？"),
        ],
        height=14 * mm,
    )
    d.callout_bar(
        "市场判断",
        "品类教育已被做完；进场买的是差异化柜面与验配信任，不是科普预算。渠道上后发最优切口=视光深度，不是再铺全国电子。",
        "green",
        10 * mm,
    )

    # ========== P03 竞争+SWOT ==========
    d.new_page("PART I · 洞察", "竞争 × SWOT")
    d.title("竞争主敌 Even / 同柜 Rokid｜SWOT 即资源分配指令", 12.5)
    d.table(
        ["对手", "强", "弱", "NIMO打法"],
        [
            ["Even G2", "Quiet Tech心智、已上市、高端叙事", "3C为主、处方中心制、总价易冲高", "视光主场+更轻+含镜套餐"],
            ["Rokid@宝岛", "验配网、字幕、连锁背书", "有摄像、更重、价高", "同店分流「隐私日常版」"],
            ["HTC Eagle", "繁中、门市密度、本土情感", "无显示屏", "不拼语音，拼看得见"],
            ["Meta水货", "外型心智", "无保、难验配", "正规化对照"],
        ],
        [26 * mm, 55 * mm, 55 * mm, CONTENT_W - 136 * mm],
        row_h=5.2 * mm,
        font=6.5,
    )
    sw = (CONTENT_W - 3 * gap) / 4
    sh = 38 * mm
    y0 = d.y - sh
    d.filled_box(MARGIN_L, y0, sw, sh, "S 优势", "无摄像+HUD同向空位\n~29g可感知差异\n含配镜锚可迁移台\n适配眼镜店旅程", C_GREEN_LIGHT, body_size=6.6)
    d.filled_box(MARGIN_L + sw + gap, y0, sw, sh, "W 劣势", "台零品牌资产\n繁中App/售后/认证待补\n无电信级密度\n无摄像被Even稀释", C_ORANGE_BG, body_size=6.6)
    d.filled_box(MARGIN_L + 2 * (sw + gap), y0, sw, sh, "O 机会", "宝岛可谈分品类\n隐私/全天戴槽点真实\nEven未占视光主场\n企业校园合规场景", C_BLUE_LIGHT, body_size=6.6)
    d.filled_box(MARGIN_L + 3 * (sw + gap), y0, sw, sh, "T 威胁", "Even专案固化心智\n宝岛排他加深\n水货拉低预期\n处方良率伤连锁", C_GRAY_BG, body_size=6.6)
    d.y = y0 - 2 * mm
    d.callout_bar(
        "Even 通路怎么读",
        "iNNOHOME独家=代理商统筹；全国电子(综合3C前二)看得到｜法雅客(百货精品3C)抬调性｜诚品(生活风格)种草｜momo(本土电商龙头)下单｜台哥大绑约降门槛。"
        "解决买得到，不默认解决验光——这正是NIMO错位点。",
        "blue",
        11 * mm,
    )
    d.callout_bar(
        "战略约束",
        "主信息必须绑「更轻/门店验配/含镜透明」｜预算优先验光师内容与门店体验｜上市Go：认证+繁中App+处方SLA+KA MOU缺一不上量｜禁止羞辱战，只做结构对照。",
        "green",
        9.5 * mm,
    )

    # ========== P04 四套打法 ==========
    d.new_page("PART II · 打法", "四套GTM对照")
    d.title("四套打法：选缝，不选热闹｜推荐 A→B，D保底，C慎用", 12.5)
    d.table(
        ["维度", "A 视光主场★", "B 双轨", "C 电信3C", "D 精品慢火"],
        [
            ["定义", "本命智能近视镜", "同上+破圈", "数码新品", "精品科技镜"],
            ["主竞品", "Even/Rokid", "Even", "Even/Eagle", "Even"],
            ["产品", "含镜主SKU+Demo+认证SOP", "A+Plano展示款", "偏无度数冲量", "限量高体验"],
            ["价格", "含镜1.3–1.6万带", "3C不挖空套餐", "绑约数千", "可略高溢价"],
            ["渠道", "宝岛20–40→80–120", "A+精选精品/预约", "全国电子+台哥大", "8–15精品店"],
            ["营销", "会议室也敢戴/验光师", "A+算上配镜等待", "大曝光促销", "小圈长测"],
            ["速度/毛利", "中 / 高", "中快 / 中高", "快 / 低", "慢 / 高"],
            ["推荐", "主推", "验证后升级", "慎用", "保底"],
        ],
        [22 * mm, 42 * mm, 38 * mm, 38 * mm, CONTENT_W - 140 * mm],
        row_h=5.1 * mm,
        font=6.4,
    )
    cw = (CONTENT_W - 3 * gap) / 4
    ch = 28 * mm
    y0 = d.y - ch
    d.filled_box(MARGIN_L, y0, cw, ch, "A 何时", "能谈进视光KA\n处方SLA可承诺\n接受先密度后广度", C_GREEN_LIGHT)
    d.filled_box(MARGIN_L + cw + gap, y0, cw, ch, "B 何时", "A转化/NPS达标\n备机池与增长团队齐\n再开精品柜", C_BLUE_LIGHT)
    d.filled_box(MARGIN_L + 2 * (cw + gap), y0, cw, ch, "C 红线", "不承诺电信主销量\n不用专案价定义品牌\n局部体验可", C_ORANGE_BG)
    d.filled_box(MARGIN_L + 3 * (cw + gap), y0, cw, ch, "D 价值", "KA卡关保活\n并行第二连锁\n维持验配叙事", C_GRAY_BG)
    d.y = y0 - 2 * mm
    d.callout_bar(
        "定位句（对外统一）",
        "NIMO：无摄像头、轻到忘记的智能近视镜。信息只在需要时出现——在眼镜门市完成专业验配。",
        "blue",
        9 * mm,
    )

    # ========== P05 方案A详解 ==========
    d.new_page("PART II · 打法", "方案A详解")
    d.title("方案A｜视光主场：用宝岛打Even，用无摄像打Rokid", 12.5)
    d.lead("做成能在验光台成交的本命智能近视镜。话术铁律：不是多买一台3C，是升级你每天那副眼镜。")

    col = (CONTENT_W - 3 * gap) / 4
    h1 = 42 * mm
    y1 = d.y - h1
    d.filled_box(
        MARGIN_L,
        y1,
        col,
        h1,
        "产品",
        "· 主SKU含基础单光套餐+Demo\n· 增值：防蓝光/变色/偏光\n· 繁中App+场景预设\n· 验配+14天调整+保修\n· 序列号绑门店\n· 首发不做巨幕配件",
        C_CARD,
        body_size=6.5,
    )
    d.filled_box(
        MARGIN_L + col + gap,
        y1,
        col,
        h1,
        "价格",
        "· 含镜套餐1.3–1.6万带\n· 升级片门店加价公示\n· 总拥有成本对照页\n  NIMO含镜 vs Even框+片+R1\n· MAP纪律\n· 上市礼：延保/片折扣\n  避免打到水货带",
        C_BLUE_LIGHT,
        body_size=6.5,
    )
    d.filled_box(
        MARGIN_L + 2 * (col + gap),
        y1,
        col,
        h1,
        "渠道",
        "· 0–3月：20–40标杆店\n  每店认证验光≥2\n· 3–9月：加密80–120\n· LINE/官网预约到店\n· 不做电信主KPI\n· 旅程25–35分钟：\n  问诊→验光→试戴→方案→建档",
        C_GREEN_LIGHT,
        body_size=6.5,
    )
    d.filled_box(
        MARGIN_L + 3 * (col + gap),
        y1,
        col,
        h1,
        "营销",
        "· 会议室也敢戴的智能近视镜\n· 三片：会议无摄像/\n  全天无压痕/验光师讲解\n· 科技+眼镜媒体，避巨幕场\n· Mobile01/ePrice长测\n· KOL：验光师/职场/双语\n· 宝岛积分+校园企业巡展",
        C_ORANGE_BG,
        body_size=6.5,
    )
    d.y = y1 - 2.5 * mm

    d.h2("门店SOP与90天里程碑")
    d.table(
        ["环节", "动作", "标准"],
        [
            ["问诊3min", "隐私场景/全天戴镜/会议旅行需求", "导流无摄像卖点"],
            ["验光10min", "度数+瞳距按成像要求", "参数入库"],
            ["试戴8min", "抬头唤醒→导航/提词/翻译三选二", "Demo开机率100%"],
            ["成交建档", "含镜方案+App绑定+回访", "配镜完成率北星"],
            ["90天KPI", "认证≥90%｜转化达标｜NPS｜售后7日关单", "进入KA下季主推"],
        ],
        [28 * mm, 85 * mm, CONTENT_W - 113 * mm],
        row_h=5 * mm,
        font=6.5,
    )
    d.callout_bar(
        "适用条件",
        "能谈进宝岛或同等视光KA｜处方交期与售后SLA可书面承诺｜接受前两季密度优先于铺货广度。",
        "green",
        8.5 * mm,
    )

    # ========== P06 BCD + 执行节奏 ==========
    d.new_page("PART II · 打法", "B/C/D × 执行节奏")
    d.title("B/C/D 要点 × 主推组合六个月节奏 × 预算", 12.5)
    col = (CONTENT_W - 2 * gap) / 3
    h = 36 * mm
    y0 = d.y - h
    d.filled_box(
        MARGIN_L,
        y0,
        col,
        h,
        "B 双轨（升级）",
        "眼镜店赚钱口碑；精品3C/内容破圈。\nPlano展示款+预约验配码。\n3C价不得挖空含镜套餐。\n辅线仅法雅客/诚品级+momo预约。\n不对撞全国电子+台哥大全面铺货。",
        C_BLUE_LIGHT,
        body_size=6.5,
    )
    d.filled_box(
        MARGIN_L + col + gap,
        y0,
        col,
        h,
        "C 电信3C（陷阱）",
        "学Eagle/Even：密度+专案价。\n产品偏无度数、营销偏促销。\n风险：丢本命镜定义、同质价格战、毛利塌。\n仅局部曝光/员工购，不定义品牌。",
        C_ORANGE_BG,
        body_size=6.5,
    )
    d.filled_box(
        MARGIN_L + 2 * (col + gap),
        y0,
        col,
        h,
        "D 精品慢火（保底）",
        "8–15精品店高体验控货。\n价格可略高；小圈长测。\nKA卡关过渡，或A的高端补充。\n并行接触得恩堂/小林等二链。",
        C_GREEN_LIGHT,
        body_size=6.5,
    )
    d.y = y0 - 2.5 * mm

    d.h2("A为骨·B为翼｜六个月")
    d.table(
        ["月", "重点", "产出"],
        [
            ["M0", "KA签约、体验桌、闭门媒体、TOT认证", "店清单+神秘客脚本"],
            ["M1", "会员软开业→正式开卖", "首月转化基线"],
            ["M2–3", "转化优化、差评闭环、第二批店", "配镜完成率拉升"],
            ["M4–5", "开启B：精选体验柜+momo预约", "破圈不破价"],
            ["M6", "复盘扩岛/第二连锁", "是否进入主推清单"],
        ],
        [18 * mm, 95 * mm, CONTENT_W - 113 * mm],
        row_h=5 * mm,
        font=6.5,
    )
    d.metrics_row(
        [
            ("预算30%", "门店体验+培训", "验光台是主战场"),
            ("25%", "内容/KOL/论坛长测", "真实佩戴非参数"),
            ("25%", "KA联合档期物料", "会员与巡展"),
            ("10%+10%", "公关+售后预备金", "差评与置换池"),
        ],
        height=13.5 * mm,
    )

    # ========== P07 宝岛+话术+Go ==========
    d.new_page("PART III · 落地", "KA · 话术 · Go/No-Go")
    d.title("宝岛谈判 · 对外话术 · 上市清单 · 决策五句", 12.5)

    left = CONTENT_W * 0.52
    right = CONTENT_W - left - gap
    h = 40 * mm
    y0 = d.y - h
    d.filled_box(
        MARGIN_L,
        y0,
        left,
        h,
        "给宝岛的谈判句",
        "宝岛用Rokid打下「看得见的AI」；HTC打下「听得懂繁中」；Even已在3C/电信占「无摄像Quiet Tech」。\n"
        "NIMO增量=视光主场上的无摄像日常镜：更轻、可门店验配、含镜更亲民——把Quiet Tech从数码柜拉回验光台。\n"
        "商务：试点20–40店｜品类优先非盲目独家｜寄售/小批量滚动｜阶梯返利｜品牌保修门店初检｜认证不合格不下放｜月度经营会。",
        C_BLUE_LIGHT,
        body_size=6.4,
    )
    d.filled_box(
        MARGIN_L + left + gap,
        y0,
        right,
        h,
        "电梯稿 + 三句区隔",
        "电梯：Meta在拍世界；Even证明不拍也可贵。NIMO第三条——像近视镜一样轻，店里验配，信息静默出现。\n"
        "vs Even：更轻+当场验配+含镜总价清\n"
        "vs Rokid：去摄像，当本命镜\n"
        "vs Eagle：多一块只给你看的显示\n"
        "禁止：山寨抄袭/吊打Meta/不用验光",
        C_CARD,
        body_size=6.4,
    )
    d.y = y0 - 2.5 * mm

    d.h2("Go / No-Go 与风险")
    d.table(
        ["项", "Go标准", "风险→应对"],
        [
            ["合规", "NCC/BSMI到手", "被叫平替→重量/验配/总价对照片"],
            ["软件", "繁中App核心场景稳定", "宝岛谈不拢→启动D+二链"],
            ["供应", "处方SLA书面+备机池", "交期爆→快配清单+超时补偿"],
            ["渠道", "≥1家视光KA MOU+店清单", "窜货破价→序列号锁+停货"],
            ["价格/培训", "含镜对照过财务｜TOT+神秘客", "繁中差评→周OTA+论坛值班"],
        ],
        [22 * mm, 55 * mm, CONTENT_W - 77 * mm],
        row_h=5.1 * mm,
        font=6.4,
    )
    d.callout_bar(
        "决策会五句话",
        "①采用A主案，资源向视光KA倾斜　②预留B内容与Plano，3C控量从属　③拒绝以C定义品牌　"
        "④价格打含镜透明套餐　⑤北星=验配完成与愿天天戴——不是铺了多少3C柜。",
        "green",
        10.5 * mm,
    )

    # ========== P08 一页作战纸 ==========
    d.new_page("附录", "一页作战纸")
    d.title("一页作战纸｜可直接贴会报", 12.5)
    d.metrics_row(
        [
            ("战场", "赛道B·隐私HUD", "视光主场非3C货架"),
            ("主敌", "Even + Rokid", "Eagle/Meta作对照"),
            ("武器", "29g·验配·含镜价", "非无摄像头口号"),
            ("主案", "A→B", "D保底·C慎用"),
            ("KA", "宝岛优先", "20–40店试点加密"),
        ],
        height=15 * mm,
    )
    cells = [
        ("产品", "含镜主SKU｜Demo三场景｜功能片升级｜繁中场景预设｜14天舒适调整｜序列号绑店"),
        ("价格", "套餐1.3–1.6万带｜升级片公示｜TCO对照Even｜MAP｜预约核销不破价｜上市延保/片折扣"),
        ("渠道", "宝岛标杆→加密｜LINE预约｜后期精选诚品/法雅客｜禁电信主KPI｜二链备胎并行"),
        ("营销", "会议室也敢戴｜验光师Vlog｜论坛长测｜会员积分｜校园企业巡展｜避巨幕横评场"),
        ("组织", "渠道BD+培训认证+区域备件+本地售后SLA｜神秘客稽核｜周OTA论坛值班"),
        ("里程碑", "M1开卖｜M3转化健康｜M5启动B｜M6复盘二链｜认证≥90%｜NPS达标｜进入KA主推"),
    ]
    footer_top = MARGIN_B + 5.5 * mm
    callout_h = 12 * mm
    grid_bottom = footer_top + callout_h + 2 * mm
    grid_top = d.y
    rows_n, cols_n = 3, 2
    cw = (CONTENT_W - gap) / cols_n
    ch = (grid_top - grid_bottom - (rows_n - 1) * 1.5 * mm) / rows_n
    for i, (t, b) in enumerate(cells):
        col_i = i % cols_n
        row_i = i // cols_n
        x = MARGIN_L + col_i * (cw + gap)
        y = grid_top - (row_i + 1) * ch - row_i * 1.5 * mm
        d.filled_box(x, y, cw, ch, t, b, C_CARD if i % 2 == 0 else C_GRAY_BG, body_size=6.8)
    d.y = grid_bottom
    d.callout_bar(
        "收束",
        "A视光主场：宝岛20–40店→含镜套餐→会议隐私内容→验配SOP。路径A→B；D保底；C慎用。"
        "定位：无摄像头、轻到忘记的智能近视镜——在眼镜门市完成专业验配。",
        "blue",
        callout_h,
    )

    d.save()
    print("wrote", path, "pages will be counted after open")


if __name__ == "__main__":
    out = "/workspace/docs/nimo-smart-glasses/NIMO台湾上市GTM汇报手册.pdf"
    build(out)
    import fitz

    doc = fitz.open(out)
    print("pages", doc.page_count, "size", doc[0].rect)
