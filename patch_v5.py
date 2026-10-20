# -*- coding: utf-8 -*-
"""
NIGHT MAFIA - ADDON v5 avtomatik o'rnatuvchi.

ISHLATISH (mafbot.py shu fayl bilan bir papkada, ichida ADDON v4 bor bo'lsin):
    python patch_v5.py            (yoki: python patch_v5.py bot.py)

Qiladi: zaxira (mafbot.py.bak) -> ADDON v5 ni ensure_https dan oldin qo'shadi -> sintaksisni tekshiradi.
Ikki marta ishlatsangiz ham xavfsiz.
"""
import os, shutil, sys

TARGET = sys.argv[1] if len(sys.argv) > 1 else "mafbot.py"
MARK = "async def ensure_https():"

BLOCK5 = r'''
# ═══════════════════════════════════════════════════════════════════════════
#  NIGHT MAFIA - ADDON v5
#  Yangi sozlamalar tizimi (/sozlamalar) - rollar, qurollar, ruxsatlar, yozish cheklovi, modelar,
#  boshqa sozlamalar | kanalga majburiy obuna | 11 ta mode | 2 ta yangi rol (Kuzatuvchi, Folbin)
# ═══════════════════════════════════════════════════════════════════════════
r5 = Router()                                   # hammasidan oldin ishlaydi
dp.include_router(r5)
try:
    dp.sub_routers.remove(r5)
    dp.sub_routers.insert(0, r5)
except Exception:
    logging.warning("r5 router ustuvorligini o'rnatib bo'lmadi")

# tugma ranglari: sozlamalar va obuna oynalarida tugmalar rangsiz (faqat Orqaga qizil)
_NOCOL = _NOCOL + ("s5:", "sub:")

# ───────── 1) Guruh sozlamalari (JSON, groups.cfg) ─────────
addcol("groups", "cfg", "TEXT DEFAULT '{}'")
db.commit()
CFG_DEF = dict(maxp=30, mvote=1, ko=1, rg=1, wolf="bori", game=1, auto=1, ban=[],
               perm=dict(start="admin", stop="admin", game="all"), wr=dict(n="admin", d="all"))
CFGC = {}


def cfg(chat):
    c = CFGC.get(chat)
    if c is None:
        try: raw = json.loads(Gr(chat)["cfg"] or "{}")
        except Exception: raw = {}
        c = json.loads(json.dumps(CFG_DEF))
        if isinstance(raw, dict):
            for k, v in raw.items():
                if isinstance(v, dict) and isinstance(c.get(k), dict): c[k].update(v)
                else: c[k] = v
        CFGC[chat] = c
    return c


def cfg_save(chat):
    gset(chat, cfg=json.dumps(cfg(chat)))


# ───────── 2) Yangi rollar: Kuzatuvchi va Folbin ─────────
_KZ = "Tunda bir o'yinchini tanlaysiz va u bu tunda kimni tanlaganini (kimning oldiga borganini) bilib olasiz."
_FB = "Tunda bir o'yinchini tanlaysiz va uning roli xavfli (tunda o'ldira oladigan) yoki xavfsiz ekanini bilib olasiz."
RL.append(("kuzatuvchi", "🔭", "Kuzatuvchi", _KZ))
RL.append(("folbin", "🧿", "Folbin", _FB))
RD["kuzatuvchi"] = ("🔭", "Kuzatuvchi", _KZ)
RD["folbin"] = ("🧿", "Folbin", _FB)
RT["kuzatuvchi"] = ("Наблюдатель", "Observer", "Ночью выбираете игрока и узнаёте, кого он выбрал этой ночью.",
                    "At night you pick a player and learn whom they targeted tonight.")
RT["folbin"] = ("Предсказатель", "Fortune teller", "Ночью выбираете игрока и узнаёте, опасна ли его роль.",
                "At night you pick a player and learn whether their role is dangerous.")
ARP["kuzatuvchi"] = ("m", 400)
ARP["folbin"] = ("m", 400)
ACT["kuzatuvchi"] = [("u", "🔭")]
ACT["folbin"] = [("p", "🧿")]
NQ["kuzatuvchi"] = "Kimni kuzatasiz?"
NQ["folbin"] = "Kimni tekshirasiz?"
ROLE_SIZ["kuzatuvchi"] = "Kuzatuvchisiz"
ROLE_SIZ["folbin"] = "Folbinsiz"
ROLE_TXT["kuzatuvchi"] = _KZ
ROLE_TXT["folbin"] = _FB
ACTN["u"] = "Kuzatish"
ACTN["p"] = "Xavfni aniqlash"
try:
    RA["kuzatuvchi"] = [("🔭", "Kuzatish", "Tanlagan o'yinchingiz bu tunda kimni tanlaganini bilasiz.")]
    RA["folbin"] = [("🧿", "Bashorat", "Tanlagan o'yinchingiz roli xavfli yoki xavfsiz ekanini bilasiz.")]
    NEWR.update({"kuzatuvchi", "folbin"})
except Exception:
    pass
DANGER = {"don", "mafia", "manyak", "komissar", "ubiytsa", "kimyogar", "tentak", "mergan", "ovchi", "kamikaze", "zombi", "sehrgar"}

_resolve_v4 = resolve


async def resolve(g):
    P = g.p; N = g.night
    if not g.vs:
        # a) Mafiya ovozi sozlamasi
        mv = {u: x for u, (k, x) in N.items() if k == "k" and u in P and P[u]["a"] and P[u]["r"] in ("don", "mafia")}
        if mv:
            don = next((u for u in mv if P[u]["r"] == "don"), None)
            top, cnt = Counter(mv.values()).most_common(1)[0]
            pick = None
            if cfg(g.chat)["mvote"] and cnt >= 3: pick = top
            elif don is not None: pick = mv[don]
            if pick is not None:
                for u in mv: N[u] = ("k", pick)
        # b) Kuzatuvchi va Folbin
        blk = {x for u, (k, x) in N.items() if k == "b" and u in P and P[u]["a"]}
        for u, (k, x) in list(N.items()):
            if k not in ("u", "p"): continue
            N.pop(u, None)
            if u not in P or not P[u]["a"] or x not in P or u in blk: continue
            xn = lk(x, P[x]["n"])
            if k == "u":
                t_ = N.get(x)
                if t_ and t_[1] in P: await pm(u, f"🔭 {xn} bu tun {lk(t_[1], P[t_[1]]['n'])} ning oldiga bordi.")
                else: await pm(u, f"🔭 {xn} bu tun hech kimning oldiga bormadi.")
            else:
                await pm(u, f"🧿 {xn} - " + ("⚠️ xavfli rol" if P[x]["r"] in DANGER else "✅ xavfsiz rol"))
    return await _resolve_v4(g)


# ───────── 3) Modelar (11 ta) ─────────
MODEI = {"classic": ("classic", 0, 0), "zombie": ("zombie", 0, 0), "night": ("night", 0, 0), "mega": ("mega", 0, 0),
         "zclassic": ("classic", 1, 0), "znight": ("night", 1, 0), "zmega": ("mega", 1, 0),
         "pclassic": ("classic", 0, 1), "pzombie": ("zombie", 0, 1), "pnight": ("night", 0, 1), "pmega": ("mega", 0, 1)}
MODE_ORDER = ["classic", "zombie", "night", "mega", "zclassic", "znight", "zmega", "pclassic", "pzombie", "pnight", "pmega"]
MODE_NAME = {"classic": "Classic", "zombie": "Zombie", "night": "Night", "mega": "Mega", "zclassic": "Zombie x Classic",
             "znight": "Zombie x Night", "zmega": "Zombie x Mega", "pclassic": "Para x Classic", "pzombie": "Para x Zombie",
             "pnight": "Para x Night", "pmega": "Para x Mega"}
for _k in MODE_ORDER: MODES[_k] = (MODE_NAME[_k], 35)
db.execute("UPDATE groups SET mode='classic' WHERE mode NOT IN (%s)" % ",".join("?" * len(MODEI)), tuple(MODEI))
db.commit()


def modeinfo(key): return MODEI.get(key, ("classic", 0, 0))


CL_POOL = ["tinch", "don", "mafia", "komissar", "doktor", "serjant", "daydi", "mashuqa", "advokat", "kamikaze", "hamshira", "rais"]
NI_EXTRA = ["manyak", "omadli", "jurnalist"]
ZB_CITY = ["komissar", "doktor", "serjant", "daydi", "mashuqa", "kamikaze", "hamshira", "rais"]


def assign(g):
    ids = list(g.p); random.shuffle(ids); n = len(ids)
    base, zf, pf = modeinfo(g.mode); off = goff(g.chat)
    ok = lambda k: (k in RD) and (k not in off)
    safe = [k for k in ("omadli", "janob", "daydi", "serjant", "mashuqa", "qoriqchi", "jurnalist", "hamshira") if ok(k)]

    def filler(mega=False):
        if not mega and ok("tinch"): return "tinch"
        return random.choice(safe) if safe else "tinch"

    roles = []
    if base == "zombie":
        if ok("zombi"): roles += ["zombi"] * max(1, n // 6)
        pri = [k for k in ("komissar", "doktor") if ok(k)] if n >= 5 else (["doktor"] if ok("doktor") else [])
        roles += pri
        pool = [k for k in ZB_CITY if ok(k) and k not in pri]
        random.shuffle(pool)
        while len(roles) < n:
            roles.append(pool.pop() if pool and random.random() < .6 else filler())
    else:
        nm = max(1, n // 4)
        roles += [k for k in (["don"] + ["mafia"] * (nm - 1)) if ok(k)]
        if not roles and ok("mafia"): roles.append("mafia")
        if base == "classic": src = CL_POOL
        elif base == "night": src = CL_POOL + NI_EXTRA
        else: src = [k for k, _, _, _ in RL]
        pool = [k for k in src if ok(k) and k not in ("don", "mafia", "tinch", "zombi", "jangchi", "qoy")]
        if zf and ok("zombi"): roles += ["zombi"] * max(1, n // 8)
        must = ["doktor", "daydi"] if n < 5 else ["komissar", "doktor"]
        if base == "night" and n >= 7: must.append("manyak")
        for k in must:
            if k in pool and len(roles) < n: roles.append(k); pool.remove(k)
        sc = sum(1 for x in roles if x in SOLO and x != "zombi")
        mc = sum(1 for x in roles if x in MAF and x not in ("don", "mafia"))
        solo_cap, maf_cap = max(1, n // 8), max(1, n // 4)
        random.shuffle(pool)
        for k in pool:
            if len(roles) >= n: break
            if k in SOLO:
                if sc >= solo_cap: continue
                sc += 1
            elif k in MAF:
                if mc >= maf_cap: continue
                mc += 1
            roles.append(k)
        while len(roles) < n: roles.append(filler(base == "mega"))
    roles = roles[:n]; random.shuffle(roles)
    for u, rl in zip(ids, roles): g.p[u]["r"] = rl
    for u in ids:                                   # faol rollar 100% tushadi
        lst = aroles(U(u))
        pick = next((x for x in lst if ok(x) and x != "zombi" and not (base == "zombie" and (x in MAF or x in SOLO))), None)
        if pick:
            g.p[u]["r"] = pick; lst.remove(pick); S(u, arole=",".join(lst))
    for d in g.p.values(): d["r0"] = d["r"]


def win(g):
    P = g.p; al = [d for d in P.values() if d["a"]]
    if g.vs:
        rc = sum(1 for d in al if d["t"] == "r"); bc = sum(1 for d in al if d["t"] == "b")
        if rc == 0 and bc == 0: return "draw"
        if bc == 0: return "r"
        if rc == 0: return "b"
        if g.round >= 15: return "r" if rc > bc else ("b" if bc > rc else "draw")
        return None
    if getattr(g, "suid", None): return "suidsid"
    base = modeinfo(g.mode)[0]
    mf = sum(d["r"] in MAF for d in al); mn = sum(d["r"] == "manyak" for d in al); z = sum(d["r"] == "zombi" for d in al)
    if base == "zombie":
        if z == 0: return "tinch"
        if z >= len(al) - z: return "zombi"
        return None
    if mf == 0 and mn == 0 and z == 0: return "tinch"
    if z and mf == 0 and mn == 0 and z >= len(al) - z: return "zombi"
    if mf and mf >= len(al) - mf: return "mafia"
    if mf == 0 and z == 0 and mn and len(al) <= 2: return "manyak"
    return None


async def finish(g, w):
    mins = max(1, round((time.time() - g.t0) / 60))
    base = modeinfo(g.mode)[0]

    def won(d):
        rl = d["r"]
        if d.get("kw") and w != "suidsid": return True
        if g.vs: return w == d["t"]
        if w == "zombi": return rl == "zombi"
        if base == "zombie": return w == "tinch" and rl != "zombi"
        return (w == "mafia" and rl in MAF) or (w == "manyak" and rl == "manyak") or \
               (w == "tinch" and rl not in MAF and rl not in SOLO and rl != "qoy") or (w == "suidsid" and rl == "suidsid")

    tag = {"r": "🔴 ", "b": "🔵 "}

    def fmt(u, d):
        s = f"{tag.get(d['t'], '') if g.vs else ''}{lk(u, d['n'])} - {rname(d['r0'])}"
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


# Para modlarida faqat parasi borlar qo'shila oladi; max o'yinchilar sozlamasi
async def join_game(m: Message, chat):
    g = games.get(chat); uid = m.from_user.id
    if not g or g.state != "reg" or g.vs or len(g.p) >= cfg(chat)["maxp"]:
        return await m.answer("Kechirasiz, bu o'yinga qo'shilib bo'lmaydi!")
    if uid in g.p: return await m.answer("Siz o'yinga qo'shilib bo'ldingiz.", reply_markup=to_group_kb(g))
    if modeinfo(g.mode)[2] and not pairs_of(uid):
        return await m.answer("💞 Bu modda faqat parasi bor o'yinchilar qatnasha oladi. Guruhda odamga reply qilib /para yozing.",
                              reply_markup=to_group_kb(g))
    g.p[uid] = newp(m.from_user.full_name)
    await m.answer("✅ Siz o'yinga qo'shildingiz!", reply_markup=to_group_kb(g))
    await upd_reg(g)


# Vaqtli avto-start sozlamasi
async def wait_reg(g):
    while True:
        try: await asyncio.wait_for(g.start_ev.wait(), 20)
        except asyncio.TimeoutError: pass
        if g.start_ev.is_set(): return "start"
        if cfg(g.chat)["auto"] and time.time() >= g.reg_end: return "start"      # yetarli o'yinchi bo'lmasa run_game bekor qiladi
        if time.time() - g.t_create >= IDLE_STOP: return "idle"


_reg_text_v4 = reg_text


def reg_text(g):
    t_ = _reg_text_v4(g)
    if g.vs: return t_
    ic = "🐺 Bo'ri" if cfg(g.chat)["wolf"] == "bori" else "🦊 Tulki"
    return t_ + f"\nMax: {cfg(g.chat)['maxp']} · {ic}"


# Advokatni ko'rish / rollarni guruhlash sozlamalari
_mates_v4 = mates_of


def mates_of(g, u):
    ms = _mates_v4(g, u)
    if not g.vs and not cfg(g.chat)["ko"]: ms = [(x, y) for x, y in ms if y["r"] != "advokat"]
    return ms


_plist_v4 = G.plist


def _plist5(s):
    t_ = _plist_v4(s)
    if cfg(s.chat)["rg"]: return t_
    cut = [i for i in (t_.find("\n\n<b>Tinchlar"), t_.find("\n\n<b>Mafiyalar"), t_.find("\n\n<b>Yakkalar")) if i >= 0]
    return t_[:min(cut)] if cut else t_


G.plist = _plist5

# ───────── 4) Qurollar taqiqi (o'yin davomida U() natijasini o'zgartiradi) ─────────
BANCOL = {"himoya": "t_h", "hujjat": "t_d", "osish": "t_o", "geroyd": "t_g", "dori": "t_dori", "sirp": "t_sirp"}
_U_v4 = U


def _bans_for(uid):
    for g_ in list(games.values()):
        if uid in g_.p and g_.state != "reg": return cfg(g_.chat)["ban"] or None
    return None


def U(uid, name=None):
    row = _U_v4(uid, name)
    b = _bans_for(uid)
    if not b: return row
    d = dict(row)
    for k in b:
        if k in BANCOL: d[BANCOL[k]] = 0
        elif k == "hero": d["has_hero"] = 0
        elif k == "arole": d["arole"] = ""
    return d


# ───────── 5) Yozishni cheklash + buyruqlarga ruxsat ─────────
_RC5 = {}


async def _role_of(chat, uid):
    k = (chat, uid); c_ = _RC5.get(k)
    if c_ and time.time() - c_[0] < 60: return c_[1]
    try: st = (await bot.get_chat_member(chat, uid)).status
    except Exception: st = "member"
    _RC5[k] = (time.time(), st); return st


async def can_write(g, event):
    uid = event.from_user.id
    if is_admin(uid): return True
    ph = "n" if g.state in ("night", "resolving") else ("d" if g.state in ("talk", "vote", "confirm", "post") else None)
    if ph is None: return True
    lvl = cfg(g.chat)["wr"][ph]
    st = await _role_of(event.chat.id, uid); adm = st in ("creator", "administrator")
    if ph == "n" and (event.text or event.caption or "").startswith("!") and adm: return True
    if lvl == "owner": return st == "creator"
    if lvl == "admin": return adm
    if lvl == "alive":
        p = g.p.get(uid)
        if p and p["a"]: return True
        return ph == "n" and vlevel(U(uid)) > 0
    return True


async def _msgmw_call(self, handler, event, data):
    txt = event.text or ""
    if txt.startswith("/") and event.chat.id not in KBCLR: asyncio.create_task(rm_kb(event.chat.id))
    if event.chat.type in ("group", "supergroup") and event.from_user and not event.from_user.is_bot and not event.sender_chat:
        g = games.get(event.chat.id)
        if (g and not txt.startswith("/")
                and event.content_type in ("text", "photo", "sticker", "voice", "video", "animation", "video_note", "document", "audio")):
            if not await can_write(g, event):
                try: await event.delete()
                except Exception: pass
                return
    return await handler(event, data)


MsgMW.__call__ = _msgmw_call
CMDK = {"game": "game", "vsgame": "game", "start": "start", "stop": "stop"}


async def cmd_denied(m: Message) -> bool:
    t_ = (m.text or "")
    if not t_.startswith("/") or not m.from_user: return False
    first = t_.split()[0][1:]
    if "@" in first and first.split("@")[1].lower() != (BOTNAME or "").lower(): return False
    w = first.split("@")[0].lower()
    if w.endswith(SUF): w = w[:-len(SUF)]
    key = CMDK.get(w)
    if not key or (key == "start" and len(t_.split()) > 1): return False
    if is_admin(m.from_user.id): return False
    lvl = cfg(m.chat.id)["perm"][key]
    if lvl == "all": return False
    st = await _role_of(m.chat.id, m.from_user.id)
    ok_ = (st == "creator") if lvl == "owner" else (st in ("creator", "administrator"))
    return not ok_


def game_blocked(m: Message) -> bool:
    return bool(m.from_user) and not cfg(m.chat.id)["game"]


@r5.message(F.text.startswith("/"), GROUP, cmd_denied)
async def h_denied(m: Message):
    await m.reply("⛔️ Bu buyruqdan foydalanishga sizga ruxsat berilmagan.")


@r5.message(C("game", "vsgame"), GROUP, game_blocked)
async def h_blocked(m: Message):
    await m.reply(f"⚠️ {lk(m.from_user.id, m.from_user.full_name)}, bu guruhda o'yin o'ynashga ruxsat berilmagan!")


# ───────── 6) Kanalga majburiy obuna (/start) ─────────
SUBOK = {}; PSTART = {}


async def is_sub(uid):
    if is_admin(uid): return True
    t_ = SUBOK.get(uid)
    if t_ and time.time() - t_ < 600: return True
    try:
        mem = await bot.get_chat_member("@" + NEWS_USER, uid)
        ok_ = mem.status in ("member", "administrator", "creator") or (mem.status == "restricted" and getattr(mem, "is_member", False))
    except Exception as e:
        logging.warning("Obunani tekshirib bo'lmadi (bot kanalda admin bo'lishi kerak): %s", e)
        return True
    if ok_: SUBOK[uid] = time.time()
    return ok_


GATE_TXT = ("⚠️ <b>O'yinni davom ettirish uchun rasmiy kanalimizga obuna bo'ling!</b>\n\n"
            "📢 Bizning news kanalimizda eng so'nggi yangiliklar, aksiyalar va sovg'alar e'lon qilib boriladi.\n\n"
            "<i>Obuna bo'lgach, \"✅ Obunani tekshirish\" tugmasini bosing.</i>")


def gate_kb():
    b = InlineKeyboardBuilder()
    b.button(text="📢 Kanalga a'zo bo'lish ↗️", url=NEWS)
    b.button(text="✅ Obunani tekshirish", callback_data="sub:chk")
    b.adjust(1); return b.as_markup()


async def need_gate(m: Message) -> bool:
    return bool(m.from_user) and not await is_sub(m.from_user.id)


@r5.message(CommandStart(), F.chat.type == "private", need_gate)
async def gate_start(m: Message, command: CommandObject):
    if command.args: PSTART[m.from_user.id] = command.args
    await m.answer(GATE_TXT, reply_markup=gate_kb())


@r5.callback_query(F.data == "sub:chk")
async def cb_subchk(c: CallbackQuery):
    uid = c.from_user.id; SUBOK.pop(uid, None)
    if not await is_sub(uid):
        return await c.answer("⚠️ Hali kanalga obuna bo'lmadingiz!\nIltimos, a'zo bo'lib qayta tekshiring.", show_alert=True)
    await c.answer("✅ Rahmat! Obuna tasdiqlandi.", show_alert=True)
    U(uid, c.from_user.full_name)
    pend = PSTART.pop(uid, "")
    try: await c.message.edit_text(tt(uid, "start"), reply_markup=start_kb(uid))
    except Exception: pass
    if pend: await pm(uid, "👆 Obuna tasdiqlandi. Avval bosgan havolangizni (o'yinga qo'shilish va h.k.) qayta bosing.")


# ───────── 7) Sozlamalar menyusi (shaxsiy chatda) ─────────
PG = 15


def sq(v): return "⬛" if v else "⬜"


def sb(text, chat, code): return InlineKeyboardButton(text=text, callback_data=f"s5:{chat}:{code}")


def bk(chat, to): return InlineKeyboardButton(text="⬅️ Orqaga", callback_data=f"s5:{chat}:{to}", **sty("danger"))


def mk(rows): return InlineKeyboardMarkup(inline_keyboard=rows)


def s5_main(chat):
    rows = [[sb("🎭 Rollar", chat, "r:0")], [sb("🔫 Qurollar", chat, "w")], [sb("🔒 Buyruqlarga ruxsatlar", chat, "p")],
            [sb("✍️ Yozishni cheklash", chat, "t")], [sb("🎮 O'yin rejimi", chat, "g")], [sb("⚙️ Boshqa sozlamalar", chat, "o")],
            [sb("❌ Chiqish", chat, "x")]]
    return "Guruh o‘yin sozlamalariga xush kelibsiz!", mk(rows)


def s5_roles(chat, page):
    ks = [k for k, _, _, _ in RL if k != "qoy"]
    tot = max(1, (len(ks) + PG - 1) // PG); page = max(0, min(page, tot - 1))
    off = goff(chat); cur = ks[page * PG:(page + 1) * PG]; rows = []
    for i in range(0, len(cur), 3):
        rows.append([sb(f"{RD[k][0]} {RD[k][1]}" + (" ⛔" if k in off else ""), chat, f"R:{k}:{page}") for k in cur[i:i + 3]])
    nav = []
    if page > 0: nav.append(sb("⬅️", chat, f"r:{page - 1}"))
    nav.append(sb(f"📄 {page + 1}/{tot}", chat, f"r:{page}"))
    if page < tot - 1: nav.append(sb("Keyingi ➡️", chat, f"r:{page + 1}"))
    rows.append(nav); rows.append([bk(chat, "m")])
    return "Qaysi rolni sozlamoqchisiz?", mk(rows)


def s5_role(chat, k, page):
    banned = k in goff(chat)
    rows = [[sb(f"Taqiqlash {sq(banned)}", chat, f"Rb:{k}:{page}:1"), sb(f"Ruxsat berish {sq(not banned)}", chat, f"Rb:{k}:{page}:0")],
            [bk(chat, f"r:{page}")]]
    return f"{RD[k][0]} {RD[k][1]} roli taqiqlansinmi?", mk(rows)


WPN = [("himoya", "🛡", "Himoya"), ("hujjat", "📁", "Soxta hujjat"), ("osish", "⚖️", "Ovozdan himoya"), ("geroyd", "🔰", "Geroydan himoya"),
       ("dori", "💊", "Doridan himoya"), ("sirp", "🪤", "Sirpanishdan himoya"), ("hero", "🥷", "Geroy"), ("arole", "🃏", "Faol rol")]
WPNK = {k: (e, n) for k, e, n in WPN}


def s5_weapons(chat):
    rows = [[sb(f"{e} {n}", chat, f"W:{k}")] for k, e, n in WPN] + [[bk(chat, "m")]]
    return "Qaysi qurolni sozlamoqchisiz?", mk(rows)


def s5_weapon(chat, k):
    banned = k in cfg(chat)["ban"]; e, n = WPNK[k]
    rows = [[sb(f"Ruxsat berish {sq(not banned)}", chat, f"Wb:{k}:0"), sb(f"Taqiqlash {sq(banned)}", chat, f"Wb:{k}:1")], [bk(chat, "w")]]
    return f"{e} {n} yoqilganmi?", mk(rows)


PLVL = [("admin", "Admin"), ("all", "Obunachilar"), ("owner", "Ega")]


def s5_perms(chat):
    rows = [[sb(c_, chat, f"P:{c_}")] for c_ in ("start", "stop", "game")] + [[bk(chat, "m")]]
    return "Qaysi buyruqqa ruxsat bermoqchisiz?", mk(rows)


def s5_perm(chat, cmd):
    cur = cfg(chat)["perm"][cmd]
    rows = [[sb(f"{n} {sq(cur == k)}", chat, f"Pc:{cmd}:{k}")] for k, n in PLVL] + [[bk(chat, "p")]]
    return f"{cmd} buyrug'ini kimlar ishlata oladi?", mk(rows)


WLVL = [("owner", "Ega"), ("admin", "Admin"), ("alive", "Tirik o'yinchilar"), ("all", "Hamma")]


def s5_write(chat):
    return "Qaysi paytni sozlaymiz?", mk([[sb("🌙 Tun", chat, "T:n")], [sb("☀️ Kun", chat, "T:d")], [bk(chat, "m")]])


def s5_wr(chat, ph):
    cur = cfg(chat)["wr"][ph]
    rows = [[sb(f"{n} {sq(cur == k)}", chat, f"Tc:{ph}:{k}")] for k, n in WLVL] + [[bk(chat, "t")]]
    return ("🌙 Tun" if ph == "n" else "☀️ Kun") + "\nKimlar yozishi mumkin?", mk(rows)


ABOUT = ("O'yin modlari haqida ma'lumot:\n\n"
         "<b>Classic</b>: Klassik qoidalarga asoslangan oddiy mode. Tinch aholi, Don, Mafia, Komissar, Doktor, Serjant, Daydi, Mashuqa, "
         "Advokat, Kamikaze, Hamshira, Rais kabi oddiy rollar tushadi. Kuchli rollar (Убийца va h.k.) va zombi tushmaydi. "
         "O'yinchi kam bo'lsa Don, Doktor, Daydi kabi asosiy rollar tushadi.\n"
         "<b>Zombie</b>: Classicdagi shahar rollari va zombilar. Mafia yo'q: zombilar hammani zombiga aylantirishga harakat qiladi.\n"
         "<b>Night</b>: Classicga o'xshash, ammo yana Manyak, Omadli, Jurnalist kabi rollar qo'shiladi.\n"
         "<b>Mega</b>: Rollardagi hamma rollar tushadi (Tinch aholidan tashqari), o'yinchilar soniga qarab.\n"
         "<b>Zombie x Classic / Night / Mega</b>: tanlangan modening rollari va unga qo'shimcha zombi - mafia va zombi bir o'yinda.\n"
         "<b>Para x Classic / Zombie / Night / Mega</b>: o'yinda faqat parasi bor odamlar qatnasha oladi. "
         "Guruhda reply qilib /para buyrug'i bilan o'zingizga sherik toping, u qabul qilsa keyin sizlar sherik bo'lasiz.")


def s5_game(chat, about=False):
    rows = [[sb("📖 Modelar haqida", chat, "gi")], [sb("🎮 Mode tanlash", chat, "gm")], [bk(chat, "m")]]
    return (ABOUT if about else "Nima qilamiz?"), mk(rows)


def s5_modes(chat):
    cur = Gr(chat)["mode"]
    rows = [[sb(f"{MODE_NAME[k]} {sq(cur == k)}", chat, f"G:{k}")] for k in MODE_ORDER] + [[bk(chat, "g")]]
    return "Qaysi o'yin modini tanlaysiz?", mk(rows)


def s5_other(chat):
    rows = [[sb("🎭 Mafiya ovozi", chat, "O:ov")], [sb("👁 Ko'rinish", chat, "O:ko")], [sb("👥 Maks o'yinchilar", chat, "O:mx")],
            [sb("📁 Rollarni guruhlash", chat, "O:rg")], [sb("🐺 Bo'ri yoki Tulki", chat, "O:bt")], [sb("🚫 O'yinni cheklash", chat, "O:lg")],
            [sb("⏱ Vaqtli avto-start", chat, "O:au")], [bk(chat, "m")]]
    return "Qaysi boshqa sozlamani o'zgartirmoqchisiz?", mk(rows)


YN = {"ov": ("mvote", "3 ta mafianing ovozi donnikidan ustun kelsinmi??"),
      "ko": ("ko", "Advokatni ko'rishga ruxsat berilsinmi?"),
      "rg": ("rg", "Rollarni guruhlashga ruxsat berilsinmi?"),
      "lg": ("game", "Guruhda o'yin o'ynashga ruxsat berilsinmi?"),
      "au": ("auto", "⏱ Vaqtli avto-start yoqilsinmi? Yoqilsa, o'yin ma'lum vaqtdan so'ng o'zi boshlanadi (yoki yetarli o'yinchi bo'lmasa bekor bo'ladi). "
                     "/extend buyrug'i bilan taymerni cheksizga to'xtatish mumkin.")}


def s5_opt(chat, f):
    cf = cfg(chat)
    if f in YN:
        key, q = YN[f]; v = bool(cf[key])
        return q, mk([[sb(f"Ha {sq(v)}", chat, f"Oc:{f}:1"), sb(f"Yo'q {sq(not v)}", chat, f"Oc:{f}:0")], [bk(chat, "o")]])
    if f == "mx":
        nums = [10, 15, 20, 25, 30, 35]; rows = []
        for i in range(0, len(nums), 3): rows.append([sb(f"{n} {sq(cf['maxp'] == n)}", chat, f"Oc:mx:{n}") for n in nums[i:i + 3]])
        rows.append([bk(chat, "o")])
        return "Maksimal o'yinchilar sonini tanlang:", mk(rows)
    return "Bo'ri yoki tulki qaysi biri?", mk([[sb(f"Bo'ri {sq(cf['wolf'] == 'bori')}", chat, "Oc:bt:bori")],
                                                [sb(f"Tulki {sq(cf['wolf'] == 'tulki')}", chat, "Oc:bt:tulki")], [bk(chat, "o")]])


@r5.message(C("sozlamalar"), GROUP)
async def cmd_settings5(m: Message):
    if not await is_gadmin(m): return
    uid = m.from_user.id; txt, kb = s5_main(m.chat.id)
    b = InlineKeyboardBuilder(); b.button(text="Botga o'tish", url=f"https://t.me/{BOTNAME}")
    if await pm(uid, txt, reply_markup=kb): await m.reply("⚙️ Sozlamalar shaxsiy chatga yuborildi.", reply_markup=b.as_markup())
    else: await m.reply("⚠️ Sozlamalarni yuborib bo'lmadi. Avval botga o'tib /start bosing.", reply_markup=b.as_markup())


@r5.callback_query(F.data.startswith("s5:"))
async def cb_s5(c: CallbackQuery):
    a = c.data.split(":")
    try: chat = int(a[1]); code = a[2]
    except (ValueError, IndexError): return await c.answer()
    args = a[3:]; uid = c.from_user.id
    if not await chat_admin(chat, uid): return await c.answer("Faqat adminlar", show_alert=True)
    if code == "x":
        try: await c.message.delete()
        except Exception: pass
        return await c.answer()
    cf = cfg(chat); view = None
    try:
        if code == "m": view = s5_main(chat)
        elif code == "r": view = s5_roles(chat, int(args[0]))
        elif code == "R" and args[0] in RD: view = s5_role(chat, args[0], int(args[1]))
        elif code == "Rb" and args[0] in RD:
            off = goff(chat)
            if args[2] == "1": off.add(args[0])
            else: off.discard(args[0])
            gset(chat, off=",".join(sorted(off))); view = s5_role(chat, args[0], int(args[1]))
        elif code == "w": view = s5_weapons(chat)
        elif code == "W" and args[0] in WPNK: view = s5_weapon(chat, args[0])
        elif code == "Wb" and args[0] in WPNK:
            b_ = cf["ban"]
            if args[1] == "1":
                if args[0] not in b_: b_.append(args[0])
            else:
                while args[0] in b_: b_.remove(args[0])
            cfg_save(chat); view = s5_weapon(chat, args[0])
        elif code == "p": view = s5_perms(chat)
        elif code == "P" and args[0] in cf["perm"]: view = s5_perm(chat, args[0])
        elif code == "Pc" and args[0] in cf["perm"] and args[1] in dict(PLVL):
            cf["perm"][args[0]] = args[1]; cfg_save(chat); view = s5_perm(chat, args[0])
        elif code == "t": view = s5_write(chat)
        elif code == "T" and args[0] in ("n", "d"): view = s5_wr(chat, args[0])
        elif code == "Tc" and args[0] in ("n", "d") and args[1] in dict(WLVL):
            cf["wr"][args[0]] = args[1]; cfg_save(chat); view = s5_wr(chat, args[0])
        elif code == "g": view = s5_game(chat)
        elif code == "gi": view = s5_game(chat, True)
        elif code == "gm": view = s5_modes(chat)
        elif code == "G" and args[0] in MODEI:
            gset(chat, mode=args[0]); view = s5_modes(chat)
        elif code == "o": view = s5_other(chat)
        elif code == "O" and (args[0] in YN or args[0] in ("mx", "bt")): view = s5_opt(chat, args[0])
        elif code == "Oc":
            f, v = args[0], args[1]
            if f in YN: cf[YN[f][0]] = 1 if v == "1" else 0
            elif f == "mx" and v.isdigit() and 10 <= int(v) <= 35: cf["maxp"] = int(v)
            elif f == "bt" and v in ("bori", "tulki"): cf["wolf"] = v
            else: return await c.answer()
            cfg_save(chat); view = s5_opt(chat, f)
    except (ValueError, IndexError, KeyError):
        return await c.answer()
    if view: await sedit(c, view[0], view[1])
    await c.answer()
'''


def main():
    if not os.path.exists(TARGET):
        print(f"❌ {TARGET} topilmadi. Bu faylni mafbot.py bilan bir papkaga qo'ying."); return
    src = open(TARGET, encoding="utf-8").read()
    if "ADDON v5" in src:
        print("ℹ️ ADDON v5 allaqachon o'rnatilgan."); return
    if "ADDON v4" not in src:
        print("❌ Faylda ADDON v4 topilmadi. Avval:  python patch_v4.py"); return
    if MARK not in src:
        print(f"❌ '{MARK}' qatori topilmadi."); return
    i = src.index(MARK)
    new = src[:i].rstrip() + "\n\n\n" + BLOCK5.strip("\n") + "\n\n\n" + src[i:]
    try: compile(new, TARGET, "exec")
    except SyntaxError as e:
        print(f"❌ Sintaksis xatosi (fayl o'zgarmadi): qator {e.lineno}: {e.msg}"); return
    shutil.copy(TARGET, TARGET + ".bak")
    with open(TARGET, "w", encoding="utf-8") as f: f.write(new)
    print(f"✅ Tayyor! ADDON v5 {TARGET} ichiga qo'shildi. Zaxira: {TARGET}.bak")
    print("Botni qayta ishga tushiring:  python mafbot.py")


if __name__ == "__main__":
    main()
