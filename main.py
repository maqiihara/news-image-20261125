#!/usr/bin/env python3
"""The World in One Page -- 25 November 2026.

A one-day world-news front page, drawn pixel by pixel with the standard
library only. No Pillow, no network, no randomness: the same bytes come
out of every run. Writes /output/entry.png (or $MAKEFUN_OUTPUT_DIR).
"""

import os
import struct
import zlib

W, H = 1024, 1024
PAPER = (251, 248, 241)
INK = (22, 22, 22)
RED = (176, 42, 30)
GREY = (120, 116, 108)
RULE = (90, 86, 78)

# ---------------------------------------------------------------- font ----
# A 5x7 bitmap font, one row of five bits per list entry.
FONT = {
    "A": [0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11],
    "B": [0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E],
    "C": [0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E],
    "D": [0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E],
    "E": [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F],
    "F": [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10],
    "G": [0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F],
    "H": [0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11],
    "I": [0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E],
    "J": [0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C],
    "K": [0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11],
    "L": [0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F],
    "M": [0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11],
    "N": [0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11],
    "O": [0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E],
    "P": [0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10],
    "Q": [0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D],
    "R": [0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11],
    "S": [0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E],
    "T": [0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04],
    "U": [0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E],
    "V": [0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04],
    "W": [0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11],
    "X": [0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11],
    "Y": [0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04],
    "Z": [0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F],
    "0": [0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E],
    "1": [0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E],
    "2": [0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F],
    "3": [0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E],
    "4": [0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02],
    "5": [0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E],
    "6": [0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E],
    "7": [0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08],
    "8": [0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E],
    "9": [0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C],
    " ": [0, 0, 0, 0, 0, 0, 0],
    ".": [0, 0, 0, 0, 0, 0x0C, 0x0C],
    ",": [0, 0, 0, 0, 0x0C, 0x04, 0x08],
    "-": [0, 0, 0, 0x0E, 0, 0, 0],
    ":": [0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0],
    "'": [0x04, 0x04, 0x08, 0, 0, 0, 0],
    "(": [0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02],
    ")": [0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08],
    "/": [0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10],
    "%": [0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13],
    "&": [0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D],
    "?": [0x0E, 0x11, 0x01, 0x02, 0x04, 0, 0x04],
    "!": [0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04],
    ";": [0, 0x0C, 0x0C, 0, 0x0C, 0x04, 0x08],
    '"': [0x0A, 0x0A, 0x0A, 0, 0, 0, 0],
    "$": [0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04],
    "+": [0, 0x04, 0x04, 0x0E, 0x04, 0x04, 0],
    "=": [0, 0, 0x1F, 0, 0x1F, 0, 0],
}

# ------------------------------------------------------------- stories ----
# (headline, body). All 48 ran on 25 November 2026 except the four marked
# 24 NOV, which are labelled on their headlines. The lead is story zero.
LEAD_HEAD = ["PUTIN VOWS REVENGE AS UKRAINE",
             "HITS TWO REFINERIES"]
LEAD_BODY = ("UKRAINIAN DRONES SET SYZRAN AND KUIBYSHEV PLANTS ABLAZE "
             "OVERNIGHT; THE KREMLIN CHIEF CALLS RETALIATION INEVITABLE "
             "DESPITE TRUMP'S PLEA TO STOP.")

STORIES = [
    ("HOUTHI DRONE HITS RIYADH TOWER, 11 HURT",
     "A Houthi drone hit a Riyadh financial-district tower; Saudi civil defence calls it terrorism."),
    ("GAZA STRIKES KILL HAMAS SECURITY CHIEF",
     "Israeli strikes kill Naeem Abu Nahal and six others in Gaza despite the year-old ceasefire."),
    ("HOSTAGES HELD IN CARTAGENA SUPERMARKET",
     "Gunmen seize a supermarket after a failed cash-truck robbery; about 30 people held in Colombia."),
    ("CIA AND ODNI HIT BY HACK",
     "A hack hits unclassified CIA and ODNI systems; officials say classified networks were untouched."),
    ("TRUMP PARDONS TURKEYS, HONOURS GIULIANI",
     "Freedom and Feathers are spared at the White House; Giuliani receives the Medal of Freedom."),
    ("ASIAN STOCKS SLIDE AS AI DOUBTS SPREAD",
     "Kospi falls 5.9%, Taiwan 6% and Nikkei 2.9% as the Nvidia rally fades and tariff fears return."),
    ("US READIES NEW TARIFF HIKES",
     "Washington prepares fresh duties on China, the EU and others, replacing struck-down levies."),
    ("IRAN RIAL HITS RECORD LOW",
     "The rial sinks to 2.856 million per dollar after fresh US sanctions hit Iran's shadow banks."),
    ("RUSSIAN JETS ENTER KOREAN AIR ZONE",
     "Seoul says Russian jets breached its air zone."),
    ("IRAQ MOVES TO SEIZE KURDISH OILFIELDS",
     "Baghdad orders federal forces to take oilfields and crossings in Kurdish-run regions."),
    ("SENEGAL GETS AFCON TITLE BACK",
     "CAS restores the 2025 Africa Cup title on appeal."),
    ("BRITAIN SANCTIONS THE HOUTHIS",
     "London blacklists Yemen's Houthis and four rebel leaders over torture and sexual violence."),
    ("XIAMEN AIRLINES ORDERS 50 BOEINGS",
     "China Southern's Xiamen unit buys 50 Boeing 737-8s."),
    ("HUAWEI HARMONYOS TOPS 100 MILLION",
     "Huawei says its Android-free HarmonyOS has passed 100 million device installations."),
    ("NIGERIAN EMIR SUSPENDED",
     "Suspended after a sexual assault allegation."),
    ("BANGLADESH GARMENT PROTESTS SHUT FACTORIES",
     "Workers reject a Tk 15,000 minimum wage offer; police fire tear gas as dozens of plants close."),
    ("POPE LEO XIV SEEKS MAIL-IN BALLOT",
     "The pope, a dual US-Vatican citizen, applies to vote by mail in the US midterms."),
    ("IRAN MEDICINE SHORTAGE BITES",
     "Pharmacies shut and hospitals run dry as Iranians hunt for drugs or cut doses."),
    ("EU DEBATES ISRAEL SANCTIONS",
     "The European Parliament demands Gaza aid access and debates sanctions on Israel."),
    ("GAZA STORM FLOODS 70,000 TENTS",
     "The season's first storm floods tents, kills five, and a meningitis alert follows."),
    ("HANOI BLAST KILLS SIX",
     "An explosion in a Hanoi residential area kills six and injures 10; a gas leak is suspected."),
    ("LAOS LEAVES LEAST-DEVELOPED LIST",
     "Laos graduates from the least-developed category."),
    ("COLOMBIA CAR BOMB WOUNDS 23",
     "A car bomb injures at least 23 people in Colombia."),
    ("CAMEROON SEPARATIST FACES WAR COURT",
     "A Cameroon separatist leader appears in a Norway court on war crimes charges."),
    ("DRONES HIT UN HQ IN KHARTOUM",
     "Drones hit houses and the UN headquarters."),
    ("TWO HELD AFTER BREAK-IN AT WILLIAM'S HOME",
     "Two men arrested after the break-in."),
    ("NORTH KOREA THREATENS SWISS OFFICE",
     "Kim Yo-jong threatens to close Switzerland's Pyongyang office over youth-camp sanctions."),
    ("NATO VOWS SPACE DEFENCE",
     "NATO pledges to defend space after reports Russia may launch a nuclear-armed satellite."),
    ("ZELENSKYY: RUSSIA PLANS NEW STRIKES",
     "Kyiv says Russia is preparing fresh strikes."),
    ("UKRAINE SEEKS 115 BILLION EUROS FOR 2027 (24 NOV)",
     "Zelenskyy says Kyiv needs at least 115 billion euros next year; Norway pledges $7 billion."),
    ("RUSSIA BUDGET: DEFENCE UP 27 PERCENT (24 NOV)",
     "The Duma passes the 2027-29 budget with defence at a record 17.1 trillion roubles."),
    ("UK WARNS OF RUSSIAN SABOTAGE (24 NOV)",
     "Britain tells firms supplying Ukraine to harden defences against Russian sabotage."),
    ("REAL MADRID ROUT PSV 5-1 (24 NOV)",
     "Bellingham's stunner, Mbappe's brace seal a comeback; Arsenal 1-1 Dortmund, City 2-2 Napoli."),
    ("NVIDIA GIVES BACK 5.9 PERCENT",
     "Nvidia slides after Monday's 31.5% surge; Bitcoin falls below $60,000 as ETF outflows hit a record."),
    ("INDIA: SP OFFERS CONGRESS 26 SEATS",
     "Akhilesh Yadav's unilateral UP candidate list sparks a row with Congress."),
    ("US ENVOY FAULTS AUSTRALIA WEB LAW",
     "Washington says Australia's digital duty of care will curb free speech; Canberra holds firm."),
    ("EISENKOT SECURES COALITION PARTNER",
     "Yashar and Lieberman's Israel Our Home agree a pact in Eisenkot's bid to form a government."),
    ("NETANYAHU OFFERS EISENKOT UNITY DEAL",
     "Netanyahu offers a unity government if he stays premier and a new Iran offensive begins."),
    ("PAKISTAN WARNS OF ENERGY CRISIS",
     "Islamabad says spreading conflicts threaten global energy and food supplies."),
    ("DR CONGO REBELS PULL BACK",
     "Rebel group retreats after heavy clashes."),
    ("FRENCH STUDENTS PLAN PROTESTS",
     "France braces for nationwide student protests over education reforms."),
    ("SWIMMER CROSSES HORMUZ FOR OCEANS",
     "Pugh swims 15 km through Hormuz for the oceans."),
    ("EU AND CANADA DEEPEN AI TIES",
     "Brussels and Ottawa plan closer cooperation on artificial intelligence."),
    ("QATAR URGES HORMUZ SHIPPING RETURN",
     "Doha calls for shipping routes to reopen and US-Iran talks to resume."),
    ("IRAN SINGER GETS 74 LASHES",
     "Parastoo Ahmadi is sentenced to 74 lashes for singing without a hijab in an online concert."),
    ("INDONESIA VICE-PRESIDENT RESIGNS",
     "Indonesia's vice-president quits amid political strain."),
    ("BANGLADESH OPENS CHINA TRADE OFFICE",
     "Invest Bangladesh office opens in Guangzhou."),
    ("INDIA BARS ACTIVIST FROM LONDON FLIGHT",
     "Drive leader stopped from flying to London."),
]

# ------------------------------------------------------------- canvas -----
class Page:
    def __init__(self):
        self.px = bytearray(PAPER * W * H)

    def set(self, x, y, color):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x0, y0, x1, y1, color):
        for y in range(y0, y1):
            for x in range(x0, x1):
                self.set(x, y, color)

    def hline(self, x0, x1, y, color, thick=1):
        for t in range(thick):
            self.rect(x0, y + t, x1, y + t + 1, color)

    def vline(self, x, y0, y1, color):
        self.rect(x, y0, x + 1, y1, color)

    def glyph(self, ch, x, y, scale, color):
        rows = FONT.get(ch, FONT[" "])
        for r, bits in enumerate(rows):
            for c in range(5):
                if bits & (1 << (4 - c)):
                    self.rect(x + c * scale, y + r * scale,
                              x + (c + 1) * scale, y + (r + 1) * scale, color)

    def text(self, s, x, y, scale, color):
        s = (s.upper()
             .replace("\u2019", "'").replace("\u2018", "'")
             .replace("\u2014", "-").replace("\u2013", "-"))
        cx = x
        for ch in s:
            self.glyph(ch, cx, y, scale, color)
            cx += 6 * scale
        return cx

    def text_width(self, s, scale):
        return len(s) * 6 * scale

    def centered(self, s, cx, y, scale, color):
        self.text(s, cx - self.text_width(s, scale) // 2, y, scale, color)


def wrap(text, max_chars):
    """Greedy word wrap; returns a list of lines, each <= max_chars."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# -------------------------------------------------------------- png ------
def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    return out + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def write_png(page, path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += page.px[y * W * 3:(y + 1) * W * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# -------------------------------------------------------------- draw -----
def draw():
    p = Page()
    # Masthead.
    p.centered("THE WORLD IN ONE PAGE", W // 2, 10, 4, INK)
    p.centered("WEDNESDAY, 25 NOVEMBER 2026", W // 2, 48, 2, RED)
    p.hline(24, 1000, 70, INK, 3)
    p.hline(24, 1000, 76, RULE, 1)

    # Lead box.
    p.rect(20, 86, 1004, 87, INK)
    p.rect(20, 219, 1004, 220, INK)
    p.rect(20, 86, 21, 220, INK)
    p.rect(1003, 86, 1004, 220, INK)
    p.text("LEAD STORY", 36, 98, 1, RED)
    y = 114
    for line in LEAD_HEAD:
        p.text(line, 36, y, 3, INK)
        y += 25
    for line in wrap(LEAD_BODY, 78):
        p.text(line, 36, y, 2, INK)
        y += 16

    # Section label.
    p.centered("- THE DAY IN BRIEF -", W // 2, 228, 1, GREY)

    # Three columns, 16 stories each.
    col_w = 314
    col_x = [24, 354, 684]
    for gx in (346, 676):
        p.vline(gx, 240, 1000, RULE)
    top = 240
    for ci in range(3):
        stories = STORIES[ci * 16:(ci + 1) * 16]
        y = top
        x = col_x[ci]
        for head, body in stories:
            for line in wrap(head, 26):
                p.text(line, x, y, 2, INK)
                y += 16
            for line in wrap(body, 52):
                p.text(line, x, y, 1, (58, 56, 50))
                y += 8
            y += 3
        if y > 1000:
            raise SystemExit("column %d overflow: %d" % (ci, y))

    # Footer.
    p.hline(24, 1000, 1002, RULE, 1)
    p.centered("ALL STORIES REPORTED ON 25 NOVEMBER 2026 UNLESS MARKED "
               "24 NOV - 49 STORIES", W // 2, 1008, 1, GREY)
    return p


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    page = draw()
    path = os.path.join(out_dir, "entry.png")
    size = write_png(page, path)
    print("wrote %s (%d bytes, %d stories + lead)" % (path, size, len(STORIES)))


if __name__ == "__main__":
    main()
