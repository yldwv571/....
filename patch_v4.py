# -*- coding: utf-8 -*-
"""
NIGHT MAFIA — ADDON v4 avtomatik o'rnatuvchi.

ISHLATISH (mafbot.py shu fayl bilan bir papkada):
    python patch_v4.py            (yoki: python patch_v4.py bot.py)

Qiladi:
  1) zaxira nusxa: mafbot.py.bak
  2) ADDON v3 yo'q bo'lsa — uni ham qo'shadi, keyin ADDON v4 ni qo'shadi
  3) sintaksisni tekshiradi (xato bo'lsa fayl o'zgarmaydi)
Natija: bitta mafbot.py ichida asosiy kod + v2 + v3 + v4 — hammasi.
Ikki marta ishlatsangiz ham xavfsiz.
"""
import os, shutil, sys

TARGET = sys.argv[1] if len(sys.argv) > 1 else "mafbot.py"
MARK = "async def ensure_https():"

BLOCK3 = r'''
# ═══════════════════════════════════════════════════════════════════════════
#  NIGHT MAFIA — ADDON v3
#  NightCoin 100/100 · dollar xaridi (olmos/Stars) · /boylar faqat adminlar ·
#  tugma ranglari · premium emoji paketlari · operator javobi tuzatilgan
# ═══════════════════════════════════════════════════════════════════════════
r3 = Router()                                   # r2 dan ham oldin ishlaydi
dp.include_router(r3)
try:
    dp.sub_routers.remove(r3)
    dp.sub_routers.insert(0, r3)
except Exception:
    logging.warning("r3 router ustuvorligini o'rnatib bo'lmadi")

NC_BUY, NC_SELL = 100, 100

EMOJI_PACKS = ["FinanceEmoji", "chatmaf_by_TgEmojiBot", "pk_6172168_by_Ctikerubot",
               "AR_PREMIUM", "gifts_emoji_by_gifts_changes_bot", "HalloweenTeamEmoji"]
_TGE = re.compile(r"(<tg-emoji\b.*?</tg-emoji>)", re.S)


def prem(text):
    """Oddiy emoji -> premium emoji (tg-emoji ichidagilarga tegmaydi; 1 xabarda max 90 ta)."""
    if not PE_RE or not isinstance(text, str): return text
    cnt = [0]

    def rep(m_):
        if cnt[0] >= 90: return m_.group(0)
        cnt[0] += 1
        return f'<tg-emoji emoji-id="{PE[m_.group(0)]}">{m_.group(0)}</tg-emoji>'
    parts = _TGE.split(text)
    for i in range(0, len(parts), 2): parts[i] = PE_RE.sub(rep, parts[i])
    return "".join(parts)


def _emoji_variants(ch):
    base = ch.replace("\ufe0f", "")
    out = {ch}
    if base and not all(ord(x) < 128 for x in base):
        out |= {base, base + "\ufe0f"}
    return out


async def load_emoji_packs():
    found = {}
    for nm in EMOJI_PACKS:
        try: ss = await bot.get_sticker_set(nm)
        except Exception as e:
            logging.warning("Emoji paketi o'qilmadi %s: %s", nm, e); continue
        for st in ss.stickers:
            if getattr(st, "custom_emoji_id", None) and st.emoji:
                for v in _emoji_variants(st.emoji): found.setdefault(v, st.custom_emoji_id)
    manual = {}
    try:
        if os.path.exists("premium_emoji.json"): manual = json.load(open("premium_emoji.json", encoding="utf-8"))
    except Exception: manual = {}
    if found:
        d = dict(found); d.update(manual); set_pe(d)
        logging.info("Premium emoji yuklandi: %d ta", len(PE))
    return len(found)


@r3.message(Command("emojipack"))
async def cmd_emojipack(m: Message):
    if not (m.from_user and is_admin(m.from_user.id)): return
    n = await load_emoji_packs()
    await m.reply(f"✅ Paketlardan {n} ta emoji topildi. Jami faol: {len(PE)} ta." if n
                  else "⚠️ Paketlar o'qilmadi. Paket nomlarini tekshiring.")


_NEG = ("❌", "⬅️", "orqaga", "назад", "back", "rad ", "rad etish", "yo'q", "нет", "o'chir", "to'xtat", "🔴", "💔", "🚫", "qaytish", "chetlat")
_POS = ("✅", "sotib ol", "qabul", "qo'shil", "🎁", "🟢", "💕", "купить", "buy", "yes", "да")


def _pick_style(b):
    t_ = (b.text or "").lower()
    if any(x in t_ for x in _NEG): return "danger"
    if any(x in t_ for x in _POS): return "success"
    return "primary"


def color_markup(mk):
    changed = False; rows = []
    for row in mk.inline_keyboard:
        nr = []
        for b in row:
            if getattr(b, "style", None): nr.append(b)
            else: nr.append(b.model_copy(update={"style": _pick_style(b)})); changed = True
        rows.append(nr)
    return mk.model_copy(update={"inline_keyboard": rows}) if changed else mk


class StyleMW(BaseRequestMiddleware):
    async def __call__(self, make_request, bot_, method):
        mk = getattr(method, "reply_markup", None)
        if _HAS_STYLE and isinstance(mk, InlineKeyboardMarkup):
            try: return await make_request(bot_, method.model_copy(update={"reply_markup": color_markup(mk)}))
            except TelegramBadRequest: pass
        return await make_request(bot_, method)


bot.session.middleware(StyleMW())


@r3.message(C("boylar"))
async def boylar3(m: Message):
    if not (m.from_user and is_admin(m.from_user.id)): return
    ids = ",".join(str(int(i)) for i in ADMIN_IDS) or "0"
    mon = db.execute(f"SELECT id,name,money FROM users WHERE blocked=0 AND id NOT IN ({ids}) AND money>0 ORDER BY money DESC LIMIT 15").fetchall()
    dia = db.execute(f"SELECT id,name,diamonds FROM users WHERE blocked=0 AND id NOT IN ({ids}) AND diamonds>0 ORDER BY diamonds DESC LIMIT 15").fetchall()
    t1 = "\n".join(f"{i}. {lk(x['id'], x['name'])} — {n_(x['money'])} 💶" for i, x in enumerate(mon, 1)) or "—"
    t2 = "\n".join(f"{i}. {lk(x['id'], x['name'])} — {n_(x['diamonds'])} 💎" for i, x in enumerate(dia, 1)) or "—"
    await m.answer(f"💰 <b>Eng boy o'yinchilar (pul)</b>\n\n{t1}\n\n💎 <b>Eng boy o'yinchilar (olmos)</b>\n\n{t2}")


@r3.callback_query(F.data.startswith("ds:"))
async def cb_ds(c: CallbackQuery):
    try: money = int(c.data[3:])
    except ValueError: return await c.answer()
    if money not in DOLLAR_S: return await c.answer()
    await bot.send_invoice(c.from_user.id, title=f"{n_(money)} 💶 dollar", description="Stars orqali dollar xaridi",
                           payload=f"usd:{money}", currency="XTR", prices=[LabeledPrice(label=f"{money} dollar", amount=DOLLAR_S[money])])
    await c.answer()


@r3.message(F.successful_payment.invoice_payload.startswith("usd:"))
async def paid_usd(m: Message):
    try: money = int(m.successful_payment.invoice_payload.split(":")[1])
    except Exception: return
    if money not in DOLLAR_S: return
    A(m.from_user.id, "money", money)
    await m.answer(f"✅ To'lov qabul qilindi! +{n_(money)} 💶")


@dp.startup()
async def _v3_startup():
    await load_emoji_packs()


@r3.message(is_sup_reply, F.text | F.photo)
async def sup_reply3(m: Message):
    WAIT.pop(m.from_user.id, None)
    await admin_support_reply(m)
'''

BLOCK4 = r'''
# ═══════════════════════════════════════════════════════════════════════════
#  NIGHT MAFIA — ADDON v4
#  Xarid oynalari (qora tugmalar) · buyruqlar menyusi · rollar matnlari · tun/kun qayta yozildi
#  geroy (ertalab, +2 ball) · aferist · minior · sehrgar · kamikadze · /para (bot) · /send pin · /vip
# ═══════════════════════════════════════════════════════════════════════════
from aiogram.types import BotCommandScopeAllChatAdministrators, BotCommandScopeDefault

r4 = Router()                                   # hammasidan oldin ishlaydi
dp.include_router(r4)
try:
    dp.sub_routers.remove(r4)
    dp.sub_routers.insert(0, r4)
except Exception:
    logging.warning("r4 router ustuvorligini o'rnatib bo'lmadi")

# ───────── Konfiguratsiya ─────────
MODES["mega"] = ("Mega Night", 45)              # Mega Night: max 45 o'yinchi
SELL = {"himoya": ("🛡", 150), "hujjat": ("📁", 100), "osish": ("⚖️", 500),
        "geroyd": ("🔰", 1500), "dori": ("💊", 150), "sirp": ("🪤", 100)}
D2M, M2D = 1000, 1275                           # 1 💎 = 1000 💵 ;  1 💎 = 1275 💵 (pulni olmosga)
DOLLAR_S = {200: 3, 800: 12, 1600: 24, 2000: 28, 3000: 37, 5000: 50, 10000: 1000}     # pul: stars
ACT["mergan"] = [("k", "🎯")]
ACT["ovchi"] = [("o", "🏹")]
HOW["slip"] = "kondagi sirpanish"
HOW["sehrgar"] = "sehrgar"
PARA_TTL = 300
LW_SEC = 45


def sp(x): return f"{int(x):,}".replace(",", " ")


def add_group_row(g, mk=None):
    rows = [list(r_) for r_ in mk.inline_keyboard] if mk else []
    if getattr(g, "url", None): rows.append([InlineKeyboardButton(text="Guruhga o'tish", url=g.url)])
    return InlineKeyboardMarkup(inline_keyboard=rows) if rows else None


def _nb(text, cd): return InlineKeyboardButton(text=text, callback_data=cd)


# ───────── 1) Tugma ranglari: xarid oynalarida hamma tugma qora (rangsiz) ─────────
_NOCOL = ("xd:", "xe:", "xm:", "ds:")
_color_markup_v3 = color_markup


def color_markup(mk):
    for row in mk.inline_keyboard:
        for b in row:
            if (getattr(b, "callback_data", None) or "").startswith(_NOCOL): return mk
    return _color_markup_v3(mk)


# ───────── 2) Xarid qilish 💵 oynalari ─────────
def xm_view(uid, page):
    u = U(uid)
    bal = f"👛 <b>Balansingiz:</b>\n💵 {sp(u['money'])}\n💎 {sp(u['diamonds'])}\n\n👇 Miqdorni tanlang"
    rows = []
    if page == "d":
        txt = f"💎 ➜ 💵 <b>Olmosni pulga almashtirish</b>\n\n<blockquote>📊 Kurs: 1 💎 = {sp(D2M)} 💵</blockquote>\n\n{bal}"
        ns = [1, 2, 4, 5, 10, 20]
        for i in range(0, len(ns), 2): rows.append([_nb(f"💎 {n} ➜ {sp(n * D2M)} $", f"xd:{n}") for n in ns[i:i + 2]])
        rows.append([_nb("💎 Pulni olmosga almashtirish", "xm:m")])
        rows.append([_nb("⭐ Star orqali dollar olish", "xm:s")])
        rows.append([_nb("⬅️ Orqaga", "m:profile")])
    elif page == "m":
        txt = f"💵 ➜ 💎 <b>Pulni olmosga almashtirish</b>\n\n<blockquote>📊 Kurs: 1 💎 = {sp(M2D)} 💵</blockquote>\n\n{bal}"
        ns = [1, 5, 10, 30]
        for i in range(0, len(ns), 2): rows.append([_nb(f"💵 {sp(n * M2D)} $ ➜ {n} 💎", f"xe:{n}") for n in ns[i:i + 2]])
        rows.append([_nb("💵 Olmosni pulga almashtirish", "xm:d")])
        rows.append([_nb("⬅️ Orqaga", "m:profile")])
    else:
        txt = "💵 <b>Qancha dollar olmoqchisiz?</b>\n\n⭐ Stars orqali to'g'ridan-to'g'ri dollar xarid qiling!"
        items = list(DOLLAR_S.items())
        for i in range(0, len(items) - 1, 2):
            rows.append([_nb(f"💵 {m_} $ - ⭐ {s_}", f"ds:{m_}") for m_, s_ in items[i:i + 2]])
        if len(items) % 2: rows.append([_nb(f"💵 {items[-1][0]} $ - ⭐ {items[-1][1]}", f"ds:{items[-1][0]}")])
        rows.append([_nb("Orqaga", "xm:d")])
    return txt, InlineKeyboardMarkup(inline_keyboard=rows)


@r4.callback_query(F.data == "m:buym")
async def xm_open(c: CallbackQuery):
    t_, k = xm_view(c.from_user.id, "d"); await sedit(c, t_, k); await c.answer()


@r4.callback_query(F.data.startswith("xm:"))
async def xm_page(c: CallbackQuery):
    pg = c.data[3:]
    if pg not in ("d", "m", "s"): return await c.answer()
    t_, k = xm_view(c.from_user.id, pg); await sedit(c, t_, k); await c.answer()


@r4.callback_query(F.data.startswith("xd:"))
async def xd_do(c: CallbackQuery):
    uid = c.from_user.id
    try: n = int(c.data[3:])
    except ValueError: return await c.answer()
    if n not in (1, 2, 4, 5, 10, 20): return await c.answer()
    if U(uid)["diamonds"] < n: return await c.answer(tt(uid, "no_dia"), show_alert=True)
    A(uid, "diamonds", -n); A(uid, "money", n * D2M)
    await c.answer(f"✅ +{sp(n * D2M)} 💵", show_alert=True)
    t_, k = xm_view(uid, "d"); await sedit(c, t_, k)


@r4.callback_query(F.data.startswith("xe:"))
async def xe_do(c: CallbackQuery):
    uid = c.from_user.id
    try: n = int(c.data[3:])
    except ValueError: return await c.answer()
    if n not in (1, 5, 10, 30): return await c.answer()
    if U(uid)["money"] < n * M2D: return await c.answer(tt(uid, "no_money"), show_alert=True)
    A(uid, "money", -n * M2D); A(uid, "diamonds", n)
    await c.answer(f"✅ +{n} 💎", show_alert=True)
    t_, k = xm_view(uid, "m"); await sedit(c, t_, k)


# ───────── 3) Buyruqlar menyusi: faqat asosiy 8 ta; qolganlari menyuda ko'rinmaydi, lekin yozilganda ishlaydi ─────────
@dp.startup()
async def _v4_menu():
    gap = [("start", "O'yinni boshlash"), ("game", "O'yin yaratish"), ("vsgame", "Jamoaviy o'yin (VS)"),
           ("roles", "O'yin rollarini ko'rish"), ("leave", "O'yindan chiqish"), ("sozlamalar", "Sozlamalarni ochish"),
           ("stop", "O'yinni to'xtatish"), ("gtop", "Geroylar reytingi")]
    for sc in (BotCommandScopeDefault(), BotCommandScopeAllChatAdministrators(), BotCommandScopeAllGroupChats()):
        try: await bot.delete_my_commands(scope=sc)
        except Exception: pass
    try: await bot.set_my_commands([BotCommand(command=c_, description=d_) for c_, d_ in gap], scope=BotCommandScopeAllGroupChats())
    except Exception: logging.exception("v4 buyruqlar o'rnatilmadi")


# ───────── 4) Ro'yxatdan o'tish: ismlar bosiladigan ─────────
def reg_text(g):
    if g.vs:
        def tm(t_):
            ns = [lk(u, d["n"]) for u, d in g.p.items() if d["t"] == t_]
            return ", ".join(ns) or "—", len(ns)
        (rn, rc), (bn, bc) = tm("r"), tm("b")
        return (f"<b>⚔️ VS mode — ro'yxatdan o'tish davom etmoqda!</b>\n\n🔴 Qizil jamoa ({rc}): {rn}\n\n"
                f"🔵 Ko'k jamoa ({bc}): {bn}\n\nJami: {len(g.p)} ta\nJamoani tanlash uchun pastdagi tugmalarni bosing.")
    names = ", ".join(lk(u, d["n"]) for u, d in g.p.items()) or "—"
    return f"<b>Ro'yxatdan o'tish davom etmoqda!</b>\nRejim: {MODES[g.mode][0]}\nRo'yxatdan o'tganlar: {names}\n\nJami: {len(g.p)} ta"


# ───────── 5) Rollar: matnlar, sheriklar ─────────
ROLE_SIZ = {"tinch": "Tinch axolisiz", "don": "Donsiz", "mafia": "Mafiasiz", "manyak": "Manyaksiz", "komissar": "Komissarsiz",
            "doktor": "Doktorsiz", "serjant": "Serjantsiz", "daydi": "Daydisiz", "mashuqa": "Mashuqasiz", "advokat": "Advokatsiz",
            "suidsid": "Suidsidsiz", "ubiytsa": "Убийцаsiz", "kamikaze": "Kamikadzesiz", "aferist": "Aferistsiz", "minior": "Miniorsiz",
            "donxotin": "Donning xotinisiz", "zombi": "Zombisiz", "kimyogar": "Kimyogarsiz", "tentak": "Tentaksiz",
            "buqalamun": "Buqalamunsiz", "sotuvchi": "Sotuvchisiz", "muxlis": "Muxlissiz", "omadli": "Omadlisiz", "rais": "Raissiz",
            "sehrgar": "Sehrgarsiz", "mergan": "Mergansiz", "janob": "Janobsiz", "qoy": "Qo'ysiz", "jurnalist": "Jurnalistsiz",
            "qoriqchi": "Qo'riqchisiz", "hamshira": "Hamshirasiz", "ovchi": "Ovchisiz", "konchi": "Konchisiz", "jangchi": "Jangchisiz"}
ROLE_TXT = {
    "tinch": "Sizning vazifangiz mafiani topish va ovoz berish jarayonida ularni osish.",
    "don": "Bu tunda kim o'lishini siz hal qilasiz. Siz Mafialar sardorisiz.",
    "mafia": "Siz Donga bo'ysunasiz va sizga qarshilik qilganlarni o'ldirasiz. Don o'lsa, siz yangi Don bo'lishingiz mumkin.",
    "manyak": "Shahardagi hamma o'lishi kerak, sizdan tashqari :)",
    "komissar": "Siz shaharning asosiy himoyachisi va mafia qo'shandasisiz. Tunda tekshirasiz yoki otasiz.",
    "doktor": "Tunda kimnidir qutqarib qolishingiz mumkin... O'zingizni ham bir marta davolay olasiz.",
    "serjant": "Siz Komissar Katanining yordamchisisiz. Komissar o'lsa, uning o'rnini egallaysiz.",
    "daydi": "Siz xohlagan odamning uyiga ichkilik uchun borib, qotillikning guvohi bo'lib qolishingiz mumkin.",
    "mashuqa": "Siz mehmonga borgan odamingizga uyqu dorisini berasiz va u 1 kun uxlaydi.",
    "advokat": "Tunda mafialardan birini himoya qilasiz: Komissar uni tekshirsa tinch aholi deb ko'radi, kunduzi esa u osilmaydi.",
    "suidsid": "Seni osib o'ldirishsa, sen yutasan :)",
    "ubiytsa": "Siz mafialar tarafda o'ynaysiz va odamlarni o'ldira olasiz. Sizni hech kim o'ldira olmaydi — faqat osish yordamida o'ldirish mumkin.",
    "kamikaze": "Kechasi kimdir sizni o'ldirsa, u ham o'ladi. Sizni kimdir osib qo'ysa, bir o'yinchini o'zingiz bilan olib keta olasiz.",
    "aferist": "Erkin rol. Maqsad — tirik qolish! Tunda tanlagan odamingizdan «Jonmi? Hamyonmi?» deb so'raysiz.",
    "minior": "Siz erkinsiz. Tunda tanlagan odamingiz eshigiga mina qo'yasiz — o'sha tunda uning uyiga kelgan sizdan boshqa hamma o'ladi.",
    "donxotin": "Siz mafialar tarafdasiz. Tunda bir o'yinchining rolini bilib, mafialarga oshkor qilasiz.",
    "zombi": "Vazifangiz hammani zombiga aylantirish.",
    "kimyogar": "Siz mafialar tarafdasiz. Mafia a'zosini tanlasangiz — himoya qilasiz, boshqalarni tanlasangiz — o'ldirasiz.",
    "tentak": "Tunda bir o'yinchini tanlaysiz. Tinch taraf bo'lsa, uni o'sha kuni hech kim osa olmaydi; mafia yoki yakka bo'lsa, uni o'ldirasiz.",
    "buqalamun": "Tun payti bir marta kimnidir tanlab, uning tarafida o'yinni davom ettirasiz.",
    "sotuvchi": "Tunda kimnidir tanlab, ertasi kuni unga bot mahsulotlarini yarim narxda taklif qilasiz. Sotib olsa, 10% ishlaysiz.",
    "muxlis": "Har kuni kimgadir muxlislik qilasiz. Siz tanlagan odam o'lsa, manyakka aylanib qasos olasiz.",
    "omadli": "Omadi kulsa suiqasddan omon qolishi mumkin. Tinch aholi uni otib o'ldira olmaydi.",
    "rais": "Tunda kimnidir tanlab, unga 50–300 dollar sovg'a berasiz.",
    "sehrgar": "Sizni o'ldirishga urinishsa, hujumchini o'ldirish yoki kechirish tanlovi beriladi.",
    "mergan": "Yakkalar ichida eng kuchlisi. Yakkalar uni o'ldira olmaydi. Tunda o'yinchilardan birini nishonga olasiz.",
    "janob": "Kunduzgi ovozda ovozingiz ikkitaga teng, shaxsingiz esa oshkor bo'lmaydi.",
    "jurnalist": "Tunda bir o'yinchini tekshirib, u qaysi tomonda ekanini (tinch / mafia / yakka) bilib olasiz.",
    "qoriqchi": "Tunda bir o'yinchini qo'riqlaysiz: unga hujum bo'lsa, uning o'rniga siz o'lasiz. Shitingiz bo'lsa, har o'yinda bir marta hayotingizni saqlab qoladi.",
    "hamshira": "Siz Doktor jamoasidasiz. Doktor o'lsa, uning o'rnini egallab, odamlarni qutqarasiz.",
    "ovchi": "Sizni kimdir osishsa yoki o'ldirishsa, tasodifiy bitta mafia yoki yakka o'yinchini o'zingiz bilan olib ketasiz.",
    "konchi": "Tunda 8 ta kondan birini tanlaysiz: 4 tasida sirpanib o'lish, 2 tasida 1–2 ta olmos, 2 tasida 50–200 pul bor.",
}


def mates_of(g, u):
    d = g.p[u]; rl = d["r"]
    if g.vs: return [(x, y) for x, y in g.p.items() if y["t"] == d["t"] and x != u]
    if rl in MAF: grp = MAF
    elif rl in ("komissar", "serjant"): grp = {"komissar", "serjant"}
    elif rl in ("doktor", "hamshira"): grp = {"doktor", "hamshira"}
    else: return []
    return [(x, y) for x, y in g.p.items() if y["r"] in grp and x != u]


async def send_roles(g):
    bad = []
    for u, d in g.p.items():
        rl = d["r"]
        if U(u)["lang"] == "uz" and rl in ROLE_SIZ:
            txt = f"Siz - {RD[rl][0]} {ROLE_SIZ[rl]}!\n\n{ROLE_TXT.get(rl) or rdesc(rl, u)}"
        else:
            txt = f"{tt(u, 'you_are', role=rname(rl, u))}\n\n{rdesc(rl, u)}"
        if g.vs: txt = f"{TEAM[d['t']]}\n\n" + txt
        ms = mates_of(g, u)
        if ms: txt += f"\n\n<b>{tt(u, 'mates')}</b>\n\n" + "\n".join(f"{lk(x, y['n'])} - {rname(y['r'], u)}" for x, y in ms)
        if not await pm_g(g, u, txt): bad.append(lk(u, d["n"]))
    if bad: await gm(g, "⚠️ Quyidagi o'yinchilarga xabar yuborib bo'lmadi (botga /start bosing): " + ", ".join(bad))


# ───────── 6) Mega Night: Tinch axoli tushmaydi ─────────
_assign_old = assign


def assign(g):
    _assign_old(g)
    if g.mode == "mega":
        off = goff(g.chat)
        pool = [k for k in ("omadli", "daydi", "serjant", "janob", "qoriqchi", "jurnalist", "hamshira", "mashuqa", "rais", "sotuvchi") if k not in off]
        for d in g.p.values():
            if d["r"] == "tinch" and pool: d["r"] = random.choice(pool)
        for d in g.p.values(): d["r0"] = d["r"]


# ───────── 7) Yordamchi: tirik o'yinchilar ro'yxati, o'lim matni ─────────
def _plist4(s):
    tag = {"r": "🔴 ", "b": "🔵 "}
    out = []
    for i, u in enumerate(s.alive(), 1):
        d = s.p[u]; hp = f" ({d['hp']}%)" if d.get("hp", 100) < 100 else ""
        out.append(f"{i}. {tag.get(d['t'], '') if s.vs else ''}{vemoji(u)}{lk(u, d['n'])}{hp}")
    base = "\n".join(out)
    if s.vs or s.state == "night": return base
    al = [s.p[u]["r"] for u in s.alive()]

    def fm(lst):
        c_ = Counter(lst)
        return ", ".join(rname(k) + (f" x{v}" if v > 1 else "") for k, v in c_.items())
    city = [x for x in al if x not in MAF and x not in SOLO]
    maf = [x for x in al if x in MAF]; solo = [x for x in al if x in SOLO]
    txt = base
    if city: txt += f"\n\n<b>Tinchlar - {len(city)}:</b>\n{fm(city)}"
    if maf: txt += f"\n\n<b>Mafiyalar - {len(maf)}:</b>\n{fm(maf)}"
    if solo: txt += f"\n\n<b>Yakkalar - {len(solo)}:</b>\n{fm(solo)}"
    return txt


G.plist = _plist4


def death_text(g, dead):
    P = g.p; txt = ""
    for tg, how, kl in dead:
        if tg not in P or P[tg].get("_dd"): continue
        P[tg]["a"] = False; P[tg]["_dd"] = True
        nm = lk(tg, P[tg]["n"])
        if how == "hero":
            kr = P[kl]["r"] if kl in P else "tinch"
            txt += f"\n⚰️ {rname(P[tg]['r'])} {nm} ni {rname(kr)} o'zining jasur geroyi bilan yer tishlatdi!"
        elif how == "slip":
            txt += f"\n💀 {nm} — {rname(P[tg]['r'])} konda sirpanib halok bo'ldi."
        elif how == "mine":
            txt += f"\n💣 {nm} — {rname(P[tg]['r'])} minaga tushib halok bo'ldi."
        else:
            txt += (f"\n💀 {nm} — {rname(P[tg]['r'])} vahshiylarcha o'ldirildi. "
                    f"Aytishlaricha, uni {HOW.get(how, how)} tomonidan o'ldirishgan.")
    return txt


# ───────── 8) So'nggi so'zlar ─────────
LW = {}


async def open_lw(g, uid, hang=False):
    if uid not in g.p: return
    p = g.p[uid]; WAIT.pop(uid, None)
    LW[uid] = (g.chat, time.time() + LW_SEC, p["r"], p["n"])
    pre = "Sizni osib o'ldirishdi! " if hang else "Sizni shavqatsizlarcha o'ldirishdi! "
    await pm(uid, pre + f"So'nggi so'zingizni aytish uchun sizda {LW_SEC} soniya vaqt bor.")


async def last_words(g, dead):
    for tg, _, _ in dead:
        if tg in g.p: await open_lw(g, tg)


def _is_lw(m: Message):
    if m.chat.type != "private" or not m.from_user: return False
    v = LW.get(m.from_user.id)
    if not v: return False
    if time.time() > v[1]: LW.pop(m.from_user.id, None); return False
    return bool(m.text) and not m.text.startswith("/")


@r4.message(_is_lw)
async def got_lw(m: Message):
    ch, _, rl, nm = LW.pop(m.from_user.id)
    await say(ch, f"{rname(rl)} {lk(m.from_user.id, nm)} so'nggi so'zlari quyidagicha edi:\n\n{esc(m.text[:300])}")
    await m.answer("✅ So'zingiz guruhga yuborildi.")


# ───────── 9) Promosyonlar (Don, Komissar, Doktor) ─────────
async def promote_all(g):
    if g.vs: return
    P = g.p; al = [u for u, d in P.items() if d["a"]]
    if not any(P[u]["r"] == "don" for u in al):
        cand = [u for u in al if P[u]["r"] == "mafia"]
        if cand:
            x = random.choice(cand); P[x]["r"] = "don"
            await pm_g(g, x, "🤵🏻 Don o'ldi — siz yangi Donsiz!")
            for z in al:
                if z != x and P[z]["r"] in MAF: await pm_g(g, z, f"🤵🏻 Yangi Don: {lk(x, P[x]['n'])}")
    if not any(P[u]["r"] == "komissar" for u in al):
        for u in al:
            if P[u]["r"] == "serjant": P[u]["r"] = "komissar"; await pm_g(g, u, "🕵🏻‍♂️ Siz endi Komissarsiz!"); break
    if not any(P[u]["r"] == "doktor" for u in al):
        for u in al:
            if P[u]["r"] == "hamshira": P[u]["r"] = "doktor"; await pm_g(g, u, "👨🏼‍⚕️ Siz endi Doktorsiz!"); break


# ───────── 10) TUN ─────────
NQ = {"don": "Kimni o'ldirasiz?", "mafia": "Kimni o'ldirasiz?", "manyak": "Kimni o'ldirasiz?", "ubiytsa": "Kimni o'ldirasiz?",
      "mergan": "Kimni nishonga olasiz?", "doktor": "Kimni davolaysiz?", "daydi": "Kimnikiga shisha olgani borasiz?",
      "mashuqa": "Kimnikiga mehmonga borasiz?", "advokat": "Kimni himoya qilasiz?", "aferist": "Kimning oldiga borasiz?",
      "minior": "Bu tunda kimni minalaysiz?", "donxotin": "Kimning rolini bilmoqchisiz?", "zombi": "Bugun kimni tishlaysiz?",
      "kimyogar": "Kimga eleksir berasiz?", "tentak": "Kimni tanlaysiz?", "buqalamun": "Kimning tarafini tanlaysiz?",
      "sotuvchi": "Kimga mahsulot taklif qilasiz?", "muxlis": "Kimga muxlislik qilasiz?", "rais": "Kimga sovg'a berasiz?",
      "jurnalist": "Kimni tekshirasiz?", "qoriqchi": "Kimni qo'riqlaysiz?", "ovchi": "Kimni nishonga olasiz?"}


def targets(g, u, rl):
    al = g.alive(); d = g.p[u]
    if g.vs:
        return [x for x in al if g.p[x]["t"] == d["t"]] if rl == "doktor" else [x for x in al if g.p[x]["t"] != d["t"]]
    if rl == "doktor": return [x for x in al if x != u or not d.get("sh")]
    if rl in ("don", "mafia"): return [x for x in al if g.p[x]["r"] not in ("don", "mafia")]
    if rl == "advokat": return [x for x in al if g.p[x]["r"] in MAF]
    if rl == "zombi": return [x for x in al if g.p[x]["r"] != "zombi"]
    return [x for x in al if x != u]


def night_flav(g, u, k, x):
    P = g.p; rl = P[u]["r"]; e = RD[rl][0]; t_ = None
    tr = P[x]["r"] if x in P else "tinch"
    if rl == "don": t_ = "Don o'ljasini tanladi"
    elif rl == "mafia": t_ = "Mafia o'ljasini tanladi"
    elif rl == "manyak": t_ = "Manyak butalar orasiga kirib, qinidan pichoqni chiqardi"
    elif rl == "komissar": t_ = "Komissar o'ljasini tanlab o'ldirdi" if k == "s" else "Komissar yovuzlarni qidirishga ketdi"
    elif rl == "doktor": t_ = "Doktor tungi navbatchilikka ketdi"
    elif rl == "daydi": t_ = "Daydi kimnikigadir shisha olish uchun ketdi"
    elif rl == "mashuqa": t_ = "Mashuqa kimnikigadir mehmonga ketdi"
    elif rl == "advokat": t_ = "Advokat kimnidir himoya qilish uchun ketdi"
    elif rl == "ubiytsa": t_ = "Убийца kimnidir o'ldirish uchun ketdi"
    elif rl == "aferist": t_ = "Aferist o'ljasini tanladi"
    elif rl == "minior": t_ = "Minior minasini joylashtirdi"
    elif rl == "donxotin": t_ = "Donning xotini o'z harakatlarini boshladi"
    elif rl == "zombi": t_ = "Zombi kimnidir tishlab oldi"
    elif rl == "kimyogar": t_ = "Kimyogar davolash eleksirini ishga soldi" if tr in MAF else "Kimyogar o'lim eleksirini ishga soldi"
    elif rl == "tentak": t_ = "Tentak kimgadir kalla qo'yib o'ldirdi" if (tr in MAF or tr in SOLO) else "Tentak osishdan himoya qiladi"
    elif rl == "buqalamun": t_ = "Buqalamun o'z tomonini tanladi"
    elif rl == "sotuvchi": t_ = "Sotuvchi mahsulotlarini sotishga ketdi"
    elif rl == "muxlis": t_ = "Muxlis dastxat olish uchun ketdi"
    elif rl == "rais": t_ = "Rais sovg'a berish uchun ketdi"
    elif rl == "mergan": t_ = "Mergan nishonni tanladi"
    elif rl == "jurnalist": t_ = "Jurnalist intervyu olish uchun ketdi"
    elif rl == "qoriqchi": t_ = "Qo'riqchi kimnidir qo'riqlash uchun ketdi"
    elif rl == "ovchi": t_ = "Ovchi kimnidir nishonga oldi"
    if not t_: return None
    return (rl, k), f"{e} {t_}"


async def night(g):
    g.state = "night"; g.night = {}; g.hero = {}; g.need = set(); g.night_ev = asyncio.Event(); g.offers = {}; g.seller = {}
    g.mines = {}; g.mine_dead = set(); g.afq = {}; g.hunt = {}; g.flsent = set(); g.slept = set(); g.lawyer = set(); g.sgw = {}
    for d in g.p.values(): d["act"] = False; d["shield"] = False
    al = g.alive(); g.idx = {u: i for i, u in enumerate(al, 1)}
    await gmedia(g, "night", "🌃 <b>Tun</b>\nKo'chaga faqat jasur va qo'rqmas odamlar chiqishdi. Ertalab tirik qolganlarni sanaymiz...", link_kb())
    await gm(g, f"<b>Tirik o'yinchilar:</b>\n{g.plist()}\n\nTonggacha ⏳ {NIGHT_SEC} sekund qoldi", reply_markup=link_kb())
    for u in al:
        rl = g.p[u]["r"]
        if g.vs:
            acts = ACT_VS.get(rl)
            if acts:
                tg_ = targets(g, u, rl)
                if tg_ and await pm(u, tt(u, "night_pick"), reply_markup=add_group_row(g, kb_targets(g, acts, tg_))): g.need.add((u, "r"))
            if U(u)["has_hero"]:
                if await pm(u, tt(u, "hm_prompt"), reply_markup=hero_menu(g, u)): g.need.add((u, "h"))
            continue
        if rl == "konchi":
            lay = ["die"] * 4 + ["dia"] * 2 + ["cash"] * 2; random.shuffle(lay)
            if await pm(u, "⛏ Qaysi konga tushasiz? (8 ta kon)", reply_markup=add_group_row(g, mine_kb(g))):
                g.mines[u] = lay; g.need.add((u, "r"))
            continue
        if rl == "komissar":
            b = InlineKeyboardBuilder(); b.button(text="🔍 Tekshirish", callback_data=f"nk:{g.chat}:c"); b.button(text="🔫 O'ldirish", callback_data=f"nk:{g.chat}:s"); b.adjust(1)
            if await pm(u, "Siz nima qilasiz?", reply_markup=add_group_row(g, b.as_markup())): g.need.add((u, "r"))
            continue
        acts = ACT.get(rl)
        if acts:
            tg_ = targets(g, u, rl)
            if rl == "buqalamun" and g.p[u].get("yd"): continue
            if tg_ and await pm(u, NQ.get(rl, tt(u, "night_pick")), reply_markup=add_group_row(g, kb_targets(g, acts, tg_))): g.need.add((u, "r"))
    if not g.need: g.night_ev.set()
    try: await asyncio.wait_for(g.night_ev.wait(), NIGHT_SEC)
    except asyncio.TimeoutError: pass
    g.state = "resolving"


@r4.callback_query(F.data.startswith("nk:"))
async def cb_nk(c: CallbackQuery):
    _, ch, k = c.data.split(":"); g = games.get(int(ch)); uid = c.from_user.id
    if not g or g.state != "night" or uid not in g.p or not g.p[uid]["a"] or k not in ("c", "s"):
        return await c.answer("Kech qoldingiz!", show_alert=True)
    tg_ = targets(g, uid, "komissar")
    q = "Kimni tekshirasiz?" if k == "c" else "Kimni o'ldirasiz?"
    await sedit(c, q, add_group_row(g, kb_targets(g, [(k, "🔍" if k == "c" else "🔫")], tg_))); await c.answer()


@r4.callback_query(F.data.startswith("na:"))
async def cb_night4(c: CallbackQuery):
    _, ch, tg, k = c.data.split(":"); g = games.get(int(ch)); uid, tg = c.from_user.id, int(tg)
    if not g or g.state != "night" or uid not in g.p or not g.p[uid]["a"] or tg not in g.p:
        return await c.answer("Kech qoldingiz!", show_alert=True)
    p = g.p[uid]
    if k == "h" and tg == uid and not g.vs:
        if p.get("sh"): return await c.answer("O'zingizni faqat bir marta davolay olasiz!", show_alert=True)
        p["sh"] = True
    if k == "y":
        if p.get("yd"): return await c.answer("Bu qobiliyatni faqat bir marta ishlatasiz!", show_alert=True)
        p["yd"] = True
    g.night[uid] = (k, tg); p["act"] = True
    await sedit(c, f"Sizning tanlov: {lk(tg, g.p[tg]['n'])}", add_group_row(g)); await c.answer()
    if not g.vs:
        fl = night_flav(g, uid, k, tg)
        if fl and fl[0] not in g.flsent:
            g.flsent.add(fl[0]); await gm(g, fl[1])
    done(g, uid, "r")


@r4.callback_query(F.data.startswith("mn:"))
async def cb_mine4(c: CallbackQuery):
    _, ch, i = c.data.split(":"); g = games.get(int(ch)); uid = c.from_user.id
    if not g or g.state != "night" or uid not in g.p or not g.p[uid]["a"] or uid not in getattr(g, "mines", {}):
        return await c.answer("Kech qoldingiz!", show_alert=True)
    k = g.mines.pop(uid)[int(i)]; u = U(uid); g.p[uid]["act"] = True
    if k == "dia":
        n = random.randint(1, 2); A(uid, "diamonds", n); txt = f"⛏ Siz konda {n} ta 💎 topdingiz!"
    elif k == "cash":
        n = random.randint(50, 200); A(uid, "money", n); txt = f"⛏ Siz konda {n} 💵 topdingiz!"
    elif u["sirp"] > 0 and u["t_sirp"]:
        A(uid, "sirp", -1); txt = "🪤 Siz konda sirpanib ketdingiz, lekin sirpanishdan himoyangiz sizni saqlab qoldi!"
    else:
        g.mine_dead.add(uid); txt = "💀 Siz konda sirpanib ketdingiz..."
    await sedit(c, txt, add_group_row(g)); await c.answer()
    if ("konchi", "m") not in g.flsent:
        g.flsent.add(("konchi", "m")); await gm(g, "⛏ Konchi konga tushib ketdi")
    done(g, uid, "r")


# ───────── 11) Geroy hujumi (+2 ball har urishga) ─────────
async def hero_phase(g, blocked, dead):
    P = g.p; lines = []
    for u, tg in g.hero.items():
        if u in blocked or u not in P or not P[u]["a"] or tg not in P or not P[tg]["a"] or any(d == tg for d, _, _ in dead): continue
        ud = U(u)
        if ud["charge"] <= 0: continue
        S(u, charge=ud["charge"] - 1); A(u, "points", 2)
        atk = rname(P[u]["r"]); tn = lk(tg, P[tg]["n"]); tu = U(tg)
        if tu["geroyd"] > 0 and tu["t_g"]:
            A(tg, "geroyd", -1)
            lines.append(f"🔰 {tn}, siz geroydan saqlandingiz! {atk} geroyining hujumi qaytarildi.")
            await pm_g(g, tg, "🔰 Sizga geroy bilan hujum bo'ldi, ammo geroydan himoya sizni qutqardi!")
            continue
        dmg = hero_dmg(u)
        if P[tg]["shield"] and tu["hprot"] > 0:
            ab = min(dmg, tu["hprot"]); S(tg, hprot=tu["hprot"] - ab); dmg -= ab
            if dmg <= 0:
                lines.append(f"⚜️ {tn} geroy himoyasi bilan {atk} geroyining hujumini qaytardi!"); continue
        P[tg]["hp"] = max(0, P[tg]["hp"] - dmg)
        if P[tg]["hp"] <= 0: dead.append((tg, "hero", u))
        else:
            lines.append(f"{tn} ga {atk} geroyi bilan hujum qildi va {dmg}% jonini oldi, {P[tg]['hp']}% joni bor.")
            await pm_g(g, tg, f"🥷 Sizga geroy bilan hujum qilindi! Joningiz: {P[tg]['hp']}%")
    return lines


# ───────── 12) Sehrgar tanlovi ─────────
@r4.callback_query(F.data.startswith("sg:"))
async def cb_sg(c: CallbackQuery):
    _, ch, y = c.data.split(":"); g = games.get(int(ch)); uid = c.from_user.id
    w = getattr(g, "sgw", {}).get(uid) if g else None
    if not w: return await c.answer("Kech qoldingiz!", show_alert=True)
    w["res"] = y; w["ev"].set()
    await sedit(c, "🧙‍♀️ Siz hujumchini kechirdingiz." if y == "y" else "🧙‍♀️ Siz hujumchini o'ldirishni tanladingiz."); await c.answer()


async def sehrgar_forgive(g, sg, atk_role):
    ev = asyncio.Event(); g.sgw[sg] = {"ev": ev, "res": None}
    b = InlineKeyboardBuilder(); b.button(text="🪄 Kechirish", callback_data=f"sg:{g.chat}:y"); b.button(text="💀 O'ldirish", callback_data=f"sg:{g.chat}:n"); b.adjust(1)
    await pm(sg, f"🧙‍♀️ Sizga {rname(atk_role)} hujum qildi!\nUni o'ldirasizmi yoki kechirasizmi?", reply_markup=add_group_row(g, b.as_markup()))
    try: await asyncio.wait_for(ev.wait(), 15)
    except asyncio.TimeoutError: pass
    return g.sgw.pop(sg)["res"] != "n"


# ───────── 13) TUN NATIJASI ─────────
async def resolve(g):
    P = g.p; N = dict(g.night); dead = []; shield_used = False; saved = False
    g.immune = set(); g.wit = []

    def dids(): return {d for d, _, _ in dead}

    # 1) Mashuqa (Doridan himoya)
    blocked = set()
    for u, (k, x) in list(N.items()):
        if k == "b" and P[u]["a"] and x in P:
            tu = U(x)
            if tu["dori"] > 0 and tu["t_dori"]:
                A(x, "dori", -1)
                await pm_g(g, x, "💃🏻 Sizga Mashuqa keldi va doridan himoyangiz sizni saqlab qoldi.")
            else:
                blocked.add(x); await pm_g(g, x, "💃🏻 Sizga Mashuqa keldi va siz 1 kun uxladingiz.")
    g.slept = set(blocked)
    for b_ in blocked: N.pop(b_, None)
    # 2) Minior: minaga kelgan hamma o'ladi (shit saqlaydi)
    mines = {x: u for u, (k, x) in N.items() if k == "m" and P[u]["a"] and x in P}
    for x, mu in mines.items():
        for v, (k, y) in list(N.items()):
            if y == x and v != mu and k != "m" and P[v]["a"] and v not in dids():
                vu = U(v)
                if vu["himoya"] > 0 and vu["t_h"]:
                    A(v, "himoya", -1); shield_used = True
                    await pm_g(g, v, "💣 Siz minaga tushdingiz va sizni shit saqlab qoldi!")
                else:
                    dead.append((v, "mine", mu)); N.pop(v, None)
                    await pm_g(g, v, "💣 Siz minaga tushdingiz va halok bo'ldingiz!")
    for u in [u for u, (k, _) in N.items() if k == "m"]: N.pop(u, None)
    # 3) Xaritalar
    heal, guard, chem, hide = {}, {}, {}, set()
    for u, (k, x) in N.items():
        if not P[u]["a"] or x not in P or u in dids(): continue
        if k == "h": heal.setdefault(x, []).append(u)
        elif k == "q": guard[x] = u
        elif k == "a": hide.add(x)
        elif k == "e" and P[x]["r"] in MAF: chem.setdefault(x, []).append(u)
    g.lawyer = set(hide)
    # 4) Qotilliklar
    kills = []; votes = {}
    for u, (k, x) in N.items():
        if P[u]["a"] and x in P and k == "k" and P[u]["r"] in ("don", "mafia") and u not in dids(): votes.setdefault(x, []).append(u)
    if votes:
        mx = max(len(v) for v in votes.values()); top = [x for x, v in votes.items() if len(v) == mx]
        dp_ = [x for x in top if any(P[v]["r"] == "don" for v in votes[x])]
        pick = dp_[0] if dp_ else random.choice(top)
        kr = next((v for v in votes[pick] if P[v]["r"] == "don"), votes[pick][0])
        kills.append((kr, pick, "mafia"))
        for z, d in P.items():
            if d["a"] and d["r"] in MAF and z not in dids():
                await pm_g(g, z, f"Mafiyalarning ovoz berishi natijasida {lk(pick, P[pick]['n'])} o'ldirildi!")
    bites = []
    for u, (k, x) in N.items():
        if not P[u]["a"] or x not in P or u in dids(): continue
        rl = P[u]["r"]
        if k == "k" and rl in ("manyak", "ubiytsa", "mergan"): kills.append((u, x, rl))
        elif k == "s" and rl == "komissar": kills.append((u, x, "komissar"))
        elif k == "e" and P[x]["r"] not in MAF: kills.append((u, x, "kimyogar"))
        elif k == "t":
            if P[x]["r"] in MAF or P[x]["r"] in SOLO: kills.append((u, x, "tentak"))
            else: g.immune.add(x)
        elif k == "z": bites.append((u, x))
    # 5) Tekshiruvlar va boshqa harakatlar
    for u, (k, x) in N.items():
        if not P[u]["a"] or x not in P or u in dids(): continue
        rl = P[u]["r"]; xn = lk(x, P[x]["n"])
        if k in ("c", "w"):
            tr = P[x]["r"]; ud = U(x); fake = False
            if x in hide and tr in MAF: tr = "tinch"
            elif ud["hujjat"] > 0 and ud["t_d"] and tr != "tinch": A(x, "hujjat", -1); tr = "tinch"; fake = True
            who = "Komissar" if k == "c" else "Donning xotini"
            if k == "c": await pm(u, f"🔍 {xn} — {rname(tr, u)}")
            else:
                for z, d in P.items():
                    if d["a"] and d["r"] in MAF: await pm(z, f"👁 {xn} - {rname(tr)}")
            if fake: await pm_g(g, x, f"🕵🏻 Sizni {who} tekshirdi va siz soxta hujjat ishlatdingiz.")
            else: await pm_g(g, x, f"🕵🏻 {who} sizning rolingizga qiziqdi.")
        elif k == "j":
            tr = P[x]["r"]; side = "🤵 Mafia" if tr in MAF else ("🎭 Yakka" if tr in SOLO else "🧑🏼 Tinch")
            await pm(u, f"📰 {xn} — {side}")
        elif k == "g":
            amt = random.randint(50, 300); A(x, "money", amt)
            await pm(x, f"💰 Rais sizga {amt} 💵 sovg'a qildi!"); await pm(u, f"💰 Siz {xn} ga {amt} 💵 sovg'a berdingiz.")
        elif k == "v": g.seller[x] = u
        elif k == "f": g.fans[u] = x
        elif k == "o": g.hunt[u] = x
        elif k == "y":
            tr = P[x]["r"]
            if tr in MAF: P[u]["r"] = "mafia"; await pm_g(g, u, "🦎 Siz mafia bo'ldingiz!")
            else: P[u]["r"] = "serjant"; await pm_g(g, u, "🦎 Siz serjantga aylandingiz!")
    # 6) Hujumlarni hal qilish
    attacked = {tg for _, tg, _ in kills}
    for killer, tg, how in kills:
        if tg not in P or not P[tg]["a"] or tg in dids(): continue
        tr = P[tg]["r"]; ud = U(tg); atk = rname(P[killer]["r"]) if killer in P else how
        gd = guard.get(tg)
        if gd and gd in P and P[gd]["a"] and gd not in dids() and gd != killer and gd != tg:
            gu = U(gd)
            if gu["himoya"] > 0 and gu["t_h"] and how not in ("manyak", "ubiytsa"):
                A(gd, "himoya", -1); shield_used = True
                await pm_g(g, gd, f"💂🏻‍♂️ Sizga {atk} hujum qildi, ammo shitingiz sizni saqlab qoldi!")
                await pm_g(g, tg, "💂🏻‍♂️ Sizga hujum bo'ldi, ammo Qo'riqchi sizni himoya qildi!")
            else:
                dead.append((gd, how, killer)); await pm_g(g, tg, "💂🏻‍♂️ Sizga hujum bo'ldi, ammo Qo'riqchi o'zini qurbon qildi!")
            continue
        if tr == "ubiytsa": continue
        if tr == "mergan" and how in ("manyak", "ubiytsa"):
            await pm_g(g, tg, "🎯 Sizga yakka qotil hujum qildi, ammo siz omon qoldingiz!"); continue
        if tr == "omadli" and (how == "komissar" or random.random() < .35):
            await pm_g(g, tg, "🤞🏼 Sizga hujum bo'ldi, ammo omadingiz kuldi!"); continue
        if tg in heal:
            saved = True
            await pm_g(g, tg, f"💉 Sizga {atk} hujum qildi, Doktor hayotingizni saqlab qoldi!")
            for dc in heal[tg]: await pm_g(g, dc, f"💉 Siz {lk(tg, P[tg]['n'])}ni {atk} hujumidan qutqardingiz!")
            continue
        if tg in chem:
            saved = True
            await pm_g(g, tg, f"⚗️ Sizga {atk} hujum qildi va sizni laborant saqlab qoldi!")
            for cm in chem[tg]: await pm_g(g, cm, f"⚗️ Siz {lk(tg, P[tg]['n'])}ni qutqardingiz!")
            continue
        if how not in ("manyak", "ubiytsa") and ud["himoya"] > 0 and ud["t_h"]:
            A(tg, "himoya", -1); shield_used = True
            await pm_g(g, tg, f"🛡 Sizga {atk} hujum qildi, ammo shitingiz ishladi va hayotingizni saqlab qoldi!"); continue
        if tr == "sehrgar":
            if await sehrgar_forgive(g, tg, P[killer]["r"] if killer in P else how):
                if killer in P: await pm_g(g, killer, "🧙‍♀️ Sehrgar sizni kechirdi va siz o'ldirmadingiz!")
            elif killer in P and P[killer]["a"] and killer not in dids():
                dead.append((killer, "sehrgar", tg)); await pm_g(g, killer, "🧙‍♀️ Sehrgar sizni kechirmadi va siz o'ldingiz!")
            continue
        dead.append((tg, how, killer))
        if tr == "kamikaze" and killer in P and P[killer]["a"] and killer not in dids():
            dead.append((killer, "kamikaze", tg)); P[tg]["kw"] = True
        if tr == "ovchi":
            x = g.hunt.get(tg)
            if not (x in P and P[x]["a"] and x not in dids() and x != tg):
                cand = [y for y in g.alive() if (P[y]["r"] in MAF or P[y]["r"] in SOLO) and y not in dids() and y != tg]
                x = random.choice(cand) if cand else None
            if x: dead.append((x, "ovchi", tg))
    for x, cs in chem.items():
        if x not in attacked and P[x]["a"]:
            for _ in cs: await pm_g(g, x, "⚗️ Siznikiga laborant keldi.")
    # 7) Zombi tishlashi
    conv = []
    for u, x in bites:
        if not P[x]["a"] or P[x]["r"] == "zombi" or x in dids() or x in conv: continue
        if x in heal: await pm_g(g, x, "💉 Zombi sizga hujum qildi, ammo siz qutqarildingiz!"); continue
        if U(x)["himoya"] > 0 and U(x)["t_h"]: A(x, "himoya", -1); shield_used = True; await pm_g(g, x, "🛡 Zombi sizni tishlamoqchi bo'ldi, shit qutqardi!"); continue
        conv.append(x)
    for x in conv: P[x]["r"] = "zombi"; await pm_g(g, x, "🧟 Sizni zombi tishladi va siz zombiga aylandingiz!")
    # 8) Konchi sirpanishi
    for u in list(getattr(g, "mine_dead", ())):
        if P[u]["a"] and u not in dids(): dead.append((u, "slip", 0))
    # 9) Daydi guvohligi
    for u, (k, x) in N.items():
        if k == "d" and P[u]["a"] and u not in dids() and x in P:
            if x in dids():
                ks = [killer for killer, tg, _ in kills if tg == x and killer in P]
                if ks: await pm(u, f"🍾 Siz jonsiz jasad ustida {lk(ks[0], P[ks[0]]['n'])} - {rname(P[ks[0]]['r'])} ni turganini ko'rdingiz.")
                else: await pm(u, "🍾 Siz hech narsa ko'rmadingiz.")
            else: await pm(u, "🍾 Siz hech narsa ko'rmadingiz.")
    # 10) Aferist: "Jonmi? Hamyonmi?"
    for u, (k, x) in N.items():
        if k == "x" and P[u]["a"] and u not in dids() and x in P and P[x]["a"] and x not in dids():
            g.afq[x] = u
            b = InlineKeyboardBuilder(); b.button(text="Jon", callback_data=f"af:{g.chat}:{u}:j"); b.button(text="Hamyon", callback_data=f"af:{g.chat}:{u}:h")
            await pm(x, f"{RD['aferist'][0]} Aferist sizdan \"Jonmi? Hamyonmi?\" deb so'rayapti!", reply_markup=b.as_markup())
    # 11) Natija matni
    txt = ""
    if conv: txt += f"\n🧟 Zombilar ko'payib bormoqda! Bu tun {len(conv)} kishi zombiga aylandi."
    txt += death_text(g, dead)
    if not dead and not conv:
        txt += "\nIshonish qiyin! Lekin, bu tunda hech kim o'lmadi..." if shield_used else "\nBu tun hech kim o'lmadi."
    if shield_used: txt = "💫 Kimningdir himoyasi ishladi!\n" + txt.strip()
    await last_words(g, dead)
    for u, x in list(g.fans.items()):
        if u in P and P[u]["a"] and P[u]["r"] == "muxlis" and x in P and not P[x]["a"]:
            P[u]["r"] = "manyak"; g.fans.pop(u, None); await pm_g(g, u, "🔪 Siz borgan odam o'ldi va siz manyakka aylandingiz!")
    await promote_all(g)
    g.state = "talk"
    return txt.strip()


# ───────── 14) Aferist javobi, Kamikadze tanlovi ─────────
@r4.callback_query(F.data.startswith("af:"))
async def cb_afer(c: CallbackQuery):
    _, ch, au, y = c.data.split(":"); g = games.get(int(ch)); uid = c.from_user.id; au = int(au)
    if not g or uid not in g.p or not g.p[uid]["a"] or getattr(g, "afq", {}).get(uid) != au or au not in g.p:
        return await c.answer("Kech qoldingiz!", show_alert=True)
    g.afq.pop(uid); P = g.p
    if y == "h":
        A(au, "money", 100)
        await sedit(c, "💵 Siz Aferistga hamyoningizni berdingiz."); await c.answer()
        await pm_g(g, au, f"💵 {lk(uid, P[uid]['n'])} sizga hamyonini berdi: +100 💵")
        await gm(g, f"{RD['aferist'][0]} Aferist {lk(uid, P[uid]['n'])}dan 100 💵 oldi.")
    else:
        P[uid]["hp"] = max(0, P[uid]["hp"] - 30)
        await c.answer()
        if P[uid]["hp"] <= 0:
            P[uid]["a"] = False
            await sedit(c, "💀 Aferist joningizni olib qo'ydi...")
            await gm(g, f"💀 {lk(uid, P[uid]['n'])} — {rname(P[uid]['r'])} aferistga jonini berib qo'ydi.")
            await open_lw(g, uid); await promote_all(g)
        else:
            await sedit(c, f"🤹🏻 Aferist jonidan 30% oldi. Joningiz: {P[uid]['hp']}%")
            await pm_g(g, au, f"🤹🏻 {lk(uid, P[uid]['n'])} jonini berdi. Uning joni: {P[uid]['hp']}%")


KK = {}


@r4.callback_query(F.data.startswith("kk:"))
async def cb_kk(c: CallbackQuery):
    _, ch, x = c.data.split(":"); uid = c.from_user.id; w = KK.get(uid)
    if not w or w["g"].chat != int(ch): return await c.answer("Kech qoldingiz!", show_alert=True)
    w["pick"] = int(x); w["ev"].set()
    await sedit(c, "💣 Tanlov qabul qilindi."); await c.answer()


async def take_along(g, kid, ev_kind):
    """Osilgan Kamikadze yoki Ovchi o'zi bilan kimnidir olib ketadi."""
    P = g.p
    if ev_kind == "ovchi":
        x = g.hunt.get(kid)
        if not (x in P and P[x]["a"] and x != kid):
            cand = [y for y in g.alive() if (P[y]["r"] in MAF or P[y]["r"] in SOLO) and y != kid]
            x = random.choice(cand) if cand else None
        if x:
            P[x]["a"] = False
            await gm(g, f"🏹 Ovchi {lk(x, P[x]['n'])} ni o'zi bilan olib ketdi.\nU edi {rname(P[x]['r'])}")
            await open_lw(g, x)
        return
    al = [x for x in g.alive() if x != kid]
    if not al: return
    b = InlineKeyboardBuilder()
    for x in al: b.button(text=P[x]["n"], callback_data=f"kk:{g.chat}:{x}")
    b.adjust(2)
    ev = asyncio.Event(); KK[kid] = {"ev": ev, "g": g, "pick": None}
    if not await pm(kid, "💣 Siz osildingiz! O'zingiz bilan kimni olib ketasiz?", reply_markup=add_group_row(g, b.as_markup())):
        KK.pop(kid, None); return
    try: await asyncio.wait_for(ev.wait(), 20)
    except asyncio.TimeoutError: pass
    x = KK.pop(kid)["pick"]
    if x and x in P and P[x]["a"]:
        P[x]["a"] = False; P[kid]["kw"] = True
        await gm(g, f"💣 Kamikadze o'zi bilan {lk(x, P[x]['n'])} ni olib ketdi.\nU edi {rname(P[x]['r'])}")
        await open_lw(g, x)


# ───────── 15) KUN va ovoz berish ─────────
@r4.callback_query(F.data.startswith("vt:"))
async def cb_vote4(c: CallbackQuery):
    try: _, ch, tg = c.data.split(":"); chat = int(ch); tgi = int(tg)
    except ValueError: return await c.answer()
    g = games.get(chat); uid = c.from_user.id
    if (not g or g.state != "vote" or uid not in g.p or not g.p[uid]["a"] or uid in getattr(g, "slept", ())
            or (tgi and (tgi not in g.p or not g.p[tgi]["a"]))):
        return await c.answer("Kech qoldingiz yoki ovoz bera olmaysiz!", show_alert=True)
    if uid in g.votes: return await c.answer("Siz allaqachon ovoz berdingiz!", show_alert=True)
    g.votes[uid] = tgi; g.p[uid]["act"] = True
    await sedit(c, "Siz ovoz berdingiz: " + (esc(g.p[tgi]["n"]) if tgi else "o'tkazib yuborildi"), add_group_row(g)); await c.answer()
    voter = f"{RD['janob'][0]} Janob" if g.p[uid]["r"] == "janob" else lk(uid, g.p[uid]["n"])
    await gm(g, f"{voter} - {lk(tgi, g.p[tgi]['n'])}ga ovoz berdi" if tgi else f"{voter} - ovoz berishni o'tkazib yubordi")


async def day(g):
    if not g.vs:
        await hero_window(g)
        await promote_all(g)
        if win(g): return
    P = g.p; al = g.alive()
    await gm(g, f"<b>Tirik o'yinchilar:</b>\n{g.plist()}\n\n💬 Muhokama vaqti ⏳ {DAY_SEC} sekund", reply_markup=link_kb())
    await asyncio.sleep(DAY_SEC)
    g.state = "vote"; g.votes = {}
    await gm(g, f"⚖️ Aybdorlarni aniqlash va jazolash vaqti keldi.\nOvoz berish uchun {VOTE_SEC} sekund.", reply_markup=link_kb("Botga o'tish"))
    for u in al:
        if u in getattr(g, "slept", ()): continue
        b = InlineKeyboardBuilder()
        for x in al:
            if x != u: b.button(text=P[x]["n"], callback_data=f"vt:{g.chat}:{x}")
        b.button(text="⏭ O'tkazib yuborish", callback_data=f"vt:{g.chat}:0"); b.adjust(2)
        await pm(u, "Kimni osamiz?", reply_markup=add_group_row(g, b.as_markup()))
    await asyncio.sleep(VOTE_SEC)
    tally = {}
    for u, x in g.votes.items():
        if x: tally[x] = tally.get(x, 0) + (2 if P[u]["r"] == "janob" else 1)
    if not tally:
        g.state = "post"; return await gm(g, "Hech kim ovoz bermadi. Hech kim osilmadi, arqon osilib qoldi.")
    mx = max(tally.values()); top = [x for x, v in tally.items() if v == mx]
    if len(top) > 1:
        g.state = "post"; return await gm(g, "Bahslar tugadi, arqon osilib qoldi. Hech kim osilmadi.")
    tg = top[0]; g.cand = tg; g.yn = {}; g.state = "confirm"; nm = lk(tg, P[tg]["n"])
    await gm(g, f"⚖️ <b>{nm}</b>ni osishga rozimisiz?\nOvoz berish uchun {CONF_SEC} sekund.", reply_markup=yn_kb(g.chat))
    await asyncio.sleep(CONF_SEC)
    g.state = "post"
    y = sum(1 for v in g.yn.values() if v == 1); n = sum(1 for v in g.yn.values() if v == 0)
    head = f"<b>Ovoz berish natijalari:</b>\n{y}👍 | {n}👎\n\n"; ud = U(tg)
    if y <= n: return await gm(g, head + f"Aholi fikri bo'linib, <b>{nm}</b> osilmadi.")
    if tg in g.immune: return await gm(g, head + f"🎲 {nm} osilmadi — Tentak uni himoyaga oldi.")
    if tg in getattr(g, "lawyer", ()): return await gm(g, head + f"⚖️ {nm} osilmay, Advokat himoya qildi va osilmadi.")
    if ud["osish"] > 0 and ud["t_o"] and not P[tg]["osh"]:
        A(tg, "osish", -1); P[tg]["osh"] = True
        return await gm(g, head + f"⚖️ {nm} ovozdan himoya tufayli osilmadi!")
    P[tg]["a"] = False
    await gm(g, head + f"🪢 <b>{nm}</b> kunduzgi yig'ilishda osildi!\nU edi {rname(P[tg]['r'])}.")
    await open_lw(g, tg, True)
    rl = P[tg]["r"]
    if rl == "suidsid":
        g.suid = tg
        for u in [u for u, v in g.yn.items() if v == 1 and u in P and u != tg]:
            P[u]["r"] = "qoy"; P[u]["r0"] = "qoy"; await pm_g(g, u, "🐑 Siz suidsidni osdingiz va qo'yga aylandingiz!")
    elif rl == "kamikaze": await take_along(g, tg, "kamikaze")
    elif rl == "ovchi": await take_along(g, tg, "ovchi")
    await promote_all(g)


# ───────── 16) Sotuvchi: sotuvdan tushgan 10% ─────────
@r4.callback_query(F.data.startswith("sv:"))
async def cb_seller4(c: CallbackQuery):
    _, ch, k = c.data.split(":"); g = games.get(int(ch)); uid = c.from_user.id
    if not g or uid not in g.offers or g.state in ("night", "resolving") or k not in SELL: return await c.answer("⌛️ Taklif tugagan.", show_alert=True)
    em, p = SELL[k]
    if U(uid)["money"] < p: return await c.answer(tt(uid, "no_money"), show_alert=True)
    s_ = g.offers[uid]; A(uid, "money", -p); A(uid, k, 1); A(s_, "money", p // 10)
    await pm(s_, f"🎁 Siz {tt(s_, 'it_' + k)} sotdingiz va {p // 10} 💵 ishlab topdingiz!")
    await c.answer(tt(uid, "bought", n=tt(uid, "it_" + k)), show_alert=True)


# ───────── 17) O'yin tugashi ─────────
async def finish(g, w):
    mins = max(1, round((time.time() - g.t0) / 60))

    def won(d):
        rl = d["r"]
        if d.get("kw") and w != "suidsid": return True
        if g.vs: return w == d["t"]
        if g.mode == "zombie": return (w == "zombi" and rl == "zombi") or (w == "tinch" and rl != "zombi")
        return (w == "mafia" and rl in MAF) or (w == "manyak" and rl == "manyak") or \
               (w == "tinch" and rl not in MAF and rl not in SOLO and rl != "qoy") or (w == "suidsid" and rl == "suidsid")

    tag = {"r": "🔴 ", "b": "🔵 "}

    def fmt(u, d):
        s = f"{tag.get(d['t'], '') if g.vs else ''}{lk(u, d['n'])} — {rname(d['r0'])}"
        return s + (f" ➜ {rname(d['r'])}" if d["r"] != d["r0"] else "")

    win_l = [fmt(u, d) for u, d in g.p.items() if won(d)]
    oth_l = [fmt(u, d) for u, d in g.p.items() if not won(d)]
    txt = "<b>O'yin tugadi!</b>\n\n"
    if g.vs and w == "draw": txt += "🤝 Durang!\n\n"
    if win_l: txt += "<b>G'olib bo'lgan o'yinchilar:</b>\n" + "\n".join(win_l) + "\n\n"
    if oth_l: txt += "<b>Qolgan o'yinchilar ro'yhati:</b>\n" + "\n".join(oth_l) + "\n\n"
    txt += f"O'yin vaqti: {mins} minut"
    await gm(g, txt)
    now = int(time.time())
    for u, d in g.p.items():
        wn = won(d); money = 120 if wn else 30
        ball = random.randint(50, 150) if wn else -random.randint(1, 10)
        A(u, "games", 1); A(u, "money", money)
        if wn: A(u, "wins", 1)
        S(u, points=max(0, U(u)["points"] + ball))
        db.execute("INSERT INTO pts_log(uid,ball,ts,chat) VALUES(?,?,?,?)", (u, ball, now, g.chat)); db.commit()
        sign = f"+{ball}" if ball > 0 else str(ball)
        head = "🏆 Siz yutdingiz!" if wn else "🏁 O'yin tugadi."
        await pm(u, f"{head}\nSizga 💵 {money}, {sign} 🏁 berildi!")


# ───────── 18) /para — faqat bot orqali ─────────
PARA = {}


async def para_expire(a, tg):
    await asyncio.sleep(PARA_TTL)
    st = PARA.pop((a, tg), None)
    if not st: return
    try: await bot.edit_message_text("⌛️ Siz parani olmadingiz.", chat_id=tg, message_id=st["mid"], reply_markup=None)
    except Exception: pass
    await pm(a, "💔 Siz para taklif qilgan odamingiz parani olmadi.")


@r4.message(C("para"))
async def para4(m: Message):
    if not m.reply_to_message: return await m.reply("Para qo'shish uchun odamga reply qiling.")
    a, tg = m.from_user, m.reply_to_message.from_user
    if a.id == tg.id or tg.is_bot: return
    U(a.id, a.full_name); U(tg.id, tg.full_name)
    if tg.id in pairs_of(a.id): return await m.reply("Siz allaqachon para bo'lgansiz.")
    if len(pairs_of(a.id)) >= plim(a.id) or len(pairs_of(tg.id)) >= plim(tg.id):
        return await m.reply("Sizda yoki unda para limiti to'lgan (VIP bilan oshadi).")
    if (a.id, tg.id) in PARA: return await m.reply("Bu odamga para taklifi allaqachon yuborilgan.")
    b = InlineKeyboardBuilder(); b.button(text="💕 Qabul", callback_data=f"pa:{a.id}:{tg.id}:1"); b.button(text="💔 Rad", callback_data=f"pa:{a.id}:{tg.id}:0")
    msg = await pm(tg.id, f"💌 Sizga {lk(a.id, a.full_name)} dan para so'rovi keldi!", reply_markup=b.as_markup())
    if not msg: return await m.reply(f"⚠️ {esc(tg.full_name)} botga hali /start bosmagan. U botga o'tib /start bosishi kerak.")
    PARA[(a.id, tg.id)] = {"mid": msg.message_id}
    if not await pm(a.id, f"💌 Siz {lk(tg.id, tg.full_name)} ga para yubordingiz."):
        await m.reply("⚠️ Botga o'tib /start bosing — para holatini shu yerda ko'rasiz.")
    asyncio.create_task(para_expire(a.id, tg.id))


@r4.callback_query(F.data.startswith("pa:"))
async def para_ans4(c: CallbackQuery):
    _, a, tg, y = c.data.split(":"); a, tg = int(a), int(tg)
    if c.from_user.id != tg: return await c.answer("Bu siz uchun emas", show_alert=True)
    if not PARA.pop((a, tg), None):
        await sedit(c, "⌛️ So'rov eskirgan."); return await c.answer()
    if y == "1":
        if len(pairs_of(a)) >= plim(a) or len(pairs_of(tg)) >= plim(tg):
            await sedit(c, "Para limiti to'lgan."); return await c.answer()
        padd(a, tg)
        await sedit(c, f"💞 Siz {lk(a, U(a)['name'])} bilan para bo'ldingiz!")
        await pm(a, f"💞 {lk(tg, U(tg)['name'])} para taklifingizni qabul qildi!")
    else:
        await sedit(c, "💔 Siz parani olmadingiz.")
        await pm(a, "💔 Siz para taklif qilgan odamingiz parani olmadi.")
    await c.answer()


@r4.message(C("mypara"))
async def mypara4(m: Message):
    uid = m.from_user.id; U(uid, m.from_user.full_name); ps = pairs_of(uid)
    if not ps: return await m.answer("👫 <b>Paralarim</b>\n\nSizda para yo'q. /para orqali para qo'shing.")
    txt = f"👫 <b>Paralarim</b>\n\nSizning asosiy parangiz: {lk(ps[0], U(ps[0])['name'])}"
    if len(ps) > 1: txt += "\n\nBoshqa paralar: " + ", ".join(lk(x, U(x)["name"]) for x in ps[1:])
    await m.answer(txt)


# ───────── 19) /send, /money — pin qilinadi ─────────
def gv2_text(d, final=False):
    sym = "💎" if d["f"] == "diamonds" else "💵"; got = d["got"]; owner = lk(d["owner"], d["oname"])
    if final:
        head = f"{owner} {n_(len(got) * d['per'])} ta {sym} tarqatdi" if got else f"{owner} tarqatgan {sym} hech kimga yetmadi (qaytarildi)."
    else:
        head = f"{owner} {'olmos' if d['f'] == 'diamonds' else 'pul'} tarqatmoqda {sym}\nHar biriga: {n_(d['per'])} {sym}"
    body = ""
    if got:
        body = f"\n\nOlganlar ({len(got)}/{d['cap']}):\n" + "\n".join(
            f"{i}) {lk(u_, nm)} {d['per']}{sym}" for i, (u_, nm) in enumerate(got[-40:], max(1, len(got) - 39)))
    return head + body


async def g2_timer(k, msg):
    await asyncio.sleep(SEND_TTL)
    d = GV2.pop(k, None)
    if not d: return
    if d["left"] > 0: A(d["owner"], d["f"], d["left"])
    try: await msg.edit_text(gv2_text(d, True), reply_markup=None)
    except Exception: pass
    try: await bot.unpin_chat_message(k[0], k[1])
    except Exception: pass


async def make_gv2(m: Message, f):
    if m.chat.type == "private": return await m.answer("Bu buyruq guruhda ishlaydi.")
    uid = m.from_user.id; u = U(uid, m.from_user.full_name)
    nums = [int(x) for x in (m.text or "").split()[1:] if x.isascii() and x.isdigit()]
    if not nums or nums[0] < 1:
        return await m.answer(f"Foydalanish: /{'send' if f == 'diamonds' else 'money'} 10 1  (jami 10, har biriga 1)")
    n = nums[0]; per = nums[1] if len(nums) > 1 else (1 if f == "diamonds" else 100)
    per = max(1, min(per, n)); cap = n // per; total = cap * per
    if u[f] < total: return await m.answer("Balans yetarli emas.")
    A(uid, f, -total)
    d = dict(f=f, n=total, per=per, cap=cap, left=total, owner=uid, oname=m.from_user.full_name, users=set(), got=[])
    msg = await m.answer(gv2_text(d), reply_markup=gv2_kb())
    k = (m.chat.id, msg.message_id); GV2[k] = d
    try: await bot.pin_chat_message(m.chat.id, msg.message_id, disable_notification=False)
    except Exception: pass
    asyncio.create_task(g2_timer(k, msg))


@r4.callback_query(F.data == "g2")
async def g2_claim4(c: CallbackQuery):
    k = (c.message.chat.id, c.message.message_id); d = GV2.get(k); uid = c.from_user.id
    if not d: return await c.answer("Tarqatish tugagan!", show_alert=True)
    if uid == d["owner"]: return await c.answer("O'zingiz tarqatgan sovg'ani ola olmaysiz!", show_alert=True)
    if uid in d["users"]: return await c.answer("Siz allaqachon olgansiz!", show_alert=True)
    U(uid, c.from_user.full_name)
    d["users"].add(uid); d["left"] -= d["per"]; d["got"].append((uid, c.from_user.full_name)); A(uid, d["f"], d["per"])
    await c.answer(f"🎉 Sizga {d['per']} {'💎' if d['f'] == 'diamonds' else '💵'} berildi!")
    fin = d["left"] < d["per"]
    if fin: GV2.pop(k, None)
    try: await c.message.edit_text(gv2_text(d, fin), reply_markup=None if fin else gv2_kb())
    except Exception: pass
    if fin:
        try: await bot.unpin_chat_message(k[0], k[1])
        except Exception: pass


# ───────── 20) /vip tarqatish (guruh va news kanal) ─────────
VG = {}


def vg_text(d, final=False):
    lv = d["lv"]; vn = VIPS[lv][0]
    if final:
        head = f"{d['who']} {len(d['got'])} ta {vn} tarqatdi" if d["got"] else f"{d['who']} tarqatgan {vn} hech kimga yetmadi."
    else:
        head = f"{d['who']} {d['cnt']} ta {vn} tarqatmoqda (1 oylik)"
    body = ""
    if d["got"]:
        body = f"\n\nOlganlar ({len(d['got'])}/{d['cnt']}):\n" + "\n".join(f"{i}) {lk(u_, nm)}" for i, (u_, nm) in enumerate(d["got"][-40:], max(1, len(d["got"]) - 39)))
    return head + body


def vg_kb():
    b = InlineKeyboardBuilder(); b.button(text="🎁 Olish", callback_data="vg"); return b.as_markup()


async def vg_timer(k, msg):
    await asyncio.sleep(SEND_TTL)
    d = VG.pop(k, None)
    if not d: return
    left = d["cnt"] - len(d["got"])
    if left > 0 and d["owner"]: A(d["owner"], "diamonds", left * VIPS[d["lv"]][1])
    try: await msg.edit_text(vg_text(d, True), reply_markup=None)
    except Exception: pass
    try: await bot.unpin_chat_message(k[0], k[1])
    except Exception: pass


async def make_vg(m: Message, free=False):
    nums = [int(x) for x in (m.text or "").split()[1:] if x.isascii() and x.isdigit()]
    cnt = nums[0] if nums else 1
    lv = nums[1] if len(nums) > 1 and nums[1] in VIPS else 1
    if cnt < 1 or cnt > 50: return await m.answer("Foydalanish: /vip 3  (3 ta VIP Plus — har biri 30 💎)\n/vip 3 2  (daraja: 1-Plus 30💎, 2-Pro 60💎, 3-Ultra 90💎, 4-Promax 150💎)")
    if free:
        owner = 0; who = esc(m.chat.title or "Night Mafia")
    else:
        owner = m.from_user.id; u = U(owner, m.from_user.full_name); total = cnt * VIPS[lv][1]
        if u["diamonds"] < total: return await m.answer(f"VIP tarqatish uchun {total} 💎 kerak (eng kam VIP — 30 💎).")
        A(owner, "diamonds", -total); who = lk(owner, m.from_user.full_name)
    d = dict(cnt=cnt, lv=lv, owner=owner, who=who, got=[], users=set())
    msg = await m.answer(vg_text(d), reply_markup=vg_kb())
    k = (m.chat.id, msg.message_id); VG[k] = d
    try: await bot.pin_chat_message(m.chat.id, msg.message_id, disable_notification=False)
    except Exception: pass
    if free:
        try: await m.delete()
        except Exception: pass
    asyncio.create_task(vg_timer(k, msg))


@r4.message(C("vip"), GROUP)
async def cmd_vip4(m: Message): await make_vg(m)


@r4.channel_post(C("vip"), is_news)
async def news_vip4(m: Message): await make_vg(m, True)


@r4.callback_query(F.data == "vg")
async def vg_claim(c: CallbackQuery):
    k = (c.message.chat.id, c.message.message_id); d = VG.get(k); uid = c.from_user.id
    if not d: return await c.answer("Tarqatish tugagan!", show_alert=True)
    if uid == d["owner"]: return await c.answer("O'zingiz tarqatgan VIP ni ola olmaysiz!", show_alert=True)
    if uid in d["users"]: return await c.answer("Siz allaqachon olgansiz!", show_alert=True)
    U(uid, c.from_user.full_name); d["users"].add(uid); d["got"].append((uid, c.from_user.full_name)); grant_vip(uid, d["lv"])
    await c.answer(f"🎉 Siz {VIPS[d['lv']][0]} oldingiz! (1 oyga)", show_alert=True)
    fin = len(d["got"]) >= d["cnt"]
    if fin: VG.pop(k, None)
    try: await c.message.edit_text(vg_text(d, fin), reply_markup=None if fin else vg_kb())
    except Exception: pass
    if fin:
        try: await bot.unpin_chat_message(k[0], k[1])
        except Exception: pass
'''


def main():
    if not os.path.exists(TARGET):
        print(f"❌ {TARGET} topilmadi. Bu faylni mafbot.py bilan bir papkaga qo'ying."); return
    src = open(TARGET, encoding="utf-8").read()
    if "ADDON v4" in src:
        print("ℹ️ ADDON v4 allaqachon o'rnatilgan."); return
    if "ADDON v2" not in src:
        print("❌ Faylda ADDON v2 topilmadi."); return
    if MARK not in src:
        print(f"❌ '{MARK}' qatori topilmadi."); return
    add = ""
    if "ADDON v3" not in src: add += BLOCK3.strip("\n") + "\n\n\n"
    add += BLOCK4.strip("\n")
    i = src.index(MARK)
    new = src[:i].rstrip() + "\n\n\n" + add + "\n\n\n" + src[i:]
    try: compile(new, TARGET, "exec")
    except SyntaxError as e:
        print(f"❌ Sintaksis xatosi (fayl o'zgarmadi): qator {e.lineno}: {e.msg}"); return
    shutil.copy(TARGET, TARGET + ".bak")
    with open(TARGET, "w", encoding="utf-8") as f: f.write(new)
    print(f"✅ Tayyor! v3 + v4 {TARGET} ichiga qo'shildi. Zaxira: {TARGET}.bak")
    print("Botni qayta ishga tushiring:  python mafbot.py")


if __name__ == "__main__":
    main()
