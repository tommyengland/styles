"""Builds misty-forest.kustomclip: the phone home-screen widget in the style of the
Home Kiosk dashboard (main.dash, Misty Forest v2 "open sections").

  - One calm surface, day #EEF2F2 / night #18212A, swapped by the sun
    (night from 30 min after sunset until sunrise, as page_theme: mistforest).
  - The clock / weather banner is the only box with its own panel: its sky colour follows
    the weather and the sun. Date (17) with the day under it, the time, a bar filling each
    minute; now, wind (compass + Beaufort name, mph), the next sunrise/sunset, the next 6 hours.
  - "What's on" (lake accent) is an open section: a small tick before the title, today big
    (on now has the accent mixed into its fill, next has a countdown), then "Coming up" small.

The widget is a stack of full-width strips painted in the surface colour, so the
background always fits whatever is showing. Run:  python3 generate.py
"""
import json, os

OUT = os.path.dirname(os.path.abspath(__file__)) + "/misty-forest.kustomclip"
W = 480          # widget width (KWGT units)
INSET = 16       # gap between the surface edge and the content
IW = W - 2 * INSET


# ---------- sun: minutes since midnight ----------
MIN_NOW = "(df(H)*60 + df(m))"
SR = "(df(H, ai(sunrise))*60 + df(m, ai(sunrise)))"
SS = "(df(H, ai(sunset))*60 + df(m, ai(sunset)))"
NIGHT = f"({MIN_NOW} >= {SS} + 30 | {MIN_NOW} < {SR})"
DAWN = f"({MIN_NOW} >= {SR} - 30 & {MIN_NOW} < {SR})"
DUSK = f"({MIN_NOW} >= {SS} & {MIN_NOW} < {SS} + 30)"

# ---------- Misty Forest tokens (day, night) ----------
SURFACE = ("#FFEEF2F2", "#FF18212A")
FILL    = ("#BFFFFFFF", "#FF222D38")   # soft fill, no border
FILL_ON = ("#FFD5E5E9", "#FF213F4A")   # fill with the lake accent mixed in (active)
TEXT    = ("#FF1F4846", "#FFDCE7E5")
MUTED   = ("#FF4A6B66", "#FF8FA9A5")
LAKE    = ("#FF2F7487", "#FF7FC0CF")   # What's on
DIVIDER = ("#264A6B66", "#338FA9A5")
AMBER   = "#FFB7791F"
ON_SKY, ON_SKY_MUTED, SKY_LINE = "#FFFFFFFF", "#D9FFFFFF", "#40FFFFFF"


def C(tok):
    return f"$if({NIGHT}, {tok[1]}, {tok[0]})$"


def CI(tok):  # the same, for use inside a larger expression
    return f"if({NIGHT}, \"{tok[1]}\", \"{tok[0]}\")"


# Sky: a vertical gradient, top colour -> horizon colour, chosen by the sun and the weather
def sky(top):
    k = 0 if top else 1
    pick = lambda pair: pair[k]
    return (f"$if({DAWN} | {DUSK}, {pick(('#FF5A4E7A', '#FFD98B6A'))},\n"
            f"  {NIGHT}, if(wi(icon) = CLEAR | wi(icon) = PCLOUDY, {pick(('#FF0E1726', '#FF243650'))}, {pick(('#FF1C232C', '#FF333C47'))}),\n"
            f"  wi(icon) = CLEAR, {pick(('#FF34709E', '#FF79A9C8'))},\n"
            f"  wi(icon) = PCLOUDY | wi(icon) = MCLOUDY, {pick(('#FF4A7290', '#FF86A3B6'))},\n"
            f"  wi(icon) = CLOUDY, {pick(('#FF56666F', '#FF86939A'))},\n"
            f"  wi(icon) = RAIN | wi(icon) = SHOWER, {pick(('#FF3E4F60', '#FF66788A'))},\n"
            f"  wi(icon) = TSTORM, {pick(('#FF2B313B', '#FF4F5865'))},\n"
            f"  wi(icon) = SNOW | wi(icon) = SLEET | wi(icon) = HAIL, {pick(('#FF667A89', '#FF94A3AD'))},\n"
            f"  wi(icon) = FOG, {pick(('#FF6B797E', '#FF919DA1'))},\n"
            f"  {pick(('#FF4A7290', '#FF86A3B6'))})$")


SKY, SKY_LOW = sky(True), sky(False)

# Taps open whatever the phone uses by default, so they work whichever apps are installed:
# the default clock (alarms) and calendar apps, and Google's weather forecast.
APP_CLOCK = "intent:#Intent;action=android.intent.action.SHOW_ALARMS;end"
APP_CAL = "intent:#Intent;action=android.intent.action.MAIN;category=android.intent.category.APP_CALENDAR;end"
APP_WEATHER = "https://www.google.com/search?q=weather#Intent;action=android.intent.action.VIEW;end"
LIGHT = "kfile://org.kustom.provider/fonts/Roboto-Light.ttf"


# ---------- module helpers ----------
def tap(m, intent):
    m["internal_events"] = [{"type": "SINGLE_TAP", "action": "LAUNCH_APP", "intent": intent}]
    return m


def visible(m, cond):
    m.setdefault("internal_toggles", {})["config_visible"] = 10
    m.setdefault("internal_formulas", {})["config_visible"] = f"$if({cond}, ALWAYS, REMOVE)$"
    return m


def txt(expr, size, color, **kw):
    m = {"internal_type": "TextModule", "text_expression": expr, "text_size": float(size)}
    if color.startswith("$"):
        m["internal_toggles"] = {"paint_color": 10}
        m["internal_formulas"] = {"paint_color": color}
    else:
        m["paint_color"] = color
    m.update(kw)
    return m


def rect(w, h, color, corners=0, anchor="CENTER", **kw):
    m = {"internal_type": "ShapeModule", "shape_type": "RECT", "shape_width": float(w),
         "shape_height": float(h), "shape_corners": float(corners), "position_anchor": anchor}
    if str(color).startswith("$"):
        m["internal_toggles"] = {"paint_color": 10}
        m["internal_formulas"] = {"paint_color": color}
    else:
        m["paint_color"] = color
    m.update(kw)
    return m


def stack(items, stacking="VERTICAL_LEFT", margin=0, **kw):
    m = {"internal_type": "StackLayerModule", "config_stacking": stacking,
         "config_margin": float(margin), "viewgroup_items": items}
    m.update(kw)
    return m


def overlap(items, **kw):
    m = {"internal_type": "OverlapLayerModule", "viewgroup_items": items}
    m.update(kw)
    return m


def pad(m, anchor, l=0, t=0, r=0, b=0):
    m.update(position_anchor=anchor, position_padding_left=float(l), position_padding_top=float(t),
             position_padding_right=float(r), position_padding_bottom=float(b))
    return m


def icon(formula, size, color):
    m = {"internal_type": "FontIconModule", "icon_set": "iconify://wi?name=Weather%20Icons",
         "icon_size": float(size), "internal_toggles": {"icon_icon": 10},
         "internal_formulas": {"icon_icon": formula}}
    if color.startswith("$"):
        m["internal_toggles"]["paint_color"] = 10
        m["internal_formulas"]["paint_color"] = color
    else:
        m["paint_color"] = color
    return m


def strip(h, *items, title=None):
    """A full-width band of the surface colour; the widget is a column of these."""
    m = overlap([rect(W, h, C(SURFACE))] + list(items))
    if title:
        m["internal_title"] = title
    return m


def weather_icon(code, isday):
    pairs = [("CLEAR", "day-sunny", "night-clear"), ("PCLOUDY", "day-cloudy", "night-alt-cloudy"),
             ("MCLOUDY", "day-cloudy", "night-alt-cloudy"), ("CLOUDY", "cloudy", "cloudy"),
             ("RAIN", "day-rain", "night-alt-rain"), ("SHOWER", "day-showers", "night-alt-showers"),
             ("TSTORM", "day-thunderstorm", "night-alt-thunderstorm"), ("SNOW", "day-snow", "night-alt-snow"),
             ("SLEET", "day-sleet", "night-alt-sleet"), ("FOG", "day-fog", "night-fog"),
             ("WINDY", "day-windy", "night-alt-cloudy-windy"), ("TORNADO", "tornado", "tornado"),
             ("HAIL", "hail", "hail")]
    parts = [f'{code} = {c}, ' + (f'"{d}"' if d == n else f'if({isday}, "{d}", "{n}")') for c, d, n in pairs]
    return "if(" + ",\n  ".join(parts) + ',\n  "na")'


# ================= 1. Banner: clock + weather on one sky =================
SKY_W, SKY_H, SP = IW, 268, 18

clock = stack([
    txt("$df(d MMMM)$", 17, ON_SKY),
    txt("$df(EEEE)$", 13, ON_SKY_MUTED),
    txt("$df(HH:mm)$", 66, ON_SKY, text_family=LIGHT, position_padding_top=2.0),
    overlap([rect(190, 4, SKY_LINE, 2, anchor="CENTERLEFT"),
             rect(190, 4, ON_SKY, 2, anchor="CENTERLEFT",
                  internal_toggles={"shape_width": 10},
                  internal_formulas={"shape_width": "$max(4, df(s) / 60 * 190)$"})],
            internal_title="Minute bar"),
], "VERTICAL_LEFT", 2, internal_title="Clock")
tap(clock, APP_CLOCK)

MS = ('(wi(wspeed) * if(wi(speedu) = "mph", 0.44704, wi(speedu) = "m/s", 1, '
      'wi(speedu) = "kn" | wi(speedu) = "kt", 0.51444, 0.27778))')
BEAUFORT = ("if(" + ", ".join(f"{MS} < {lim}, \"{name}\"" for lim, name in zip(
    [0.3, 1.6, 3.4, 5.5, 8.0, 10.8, 13.9, 17.2, 20.8, 24.5, 28.5, 32.7],
    ["Calm", "Light air", "Light breeze", "Gentle breeze", "Moderate breeze", "Fresh breeze",
     "Strong breeze", "Near gale", "Gale", "Strong gale", "Storm", "Violent storm"])) + ', "Hurricane force")')
COMPASS = ('if(wi(wdir) < 22.5, "N", wi(wdir) < 67.5, "NE", wi(wdir) < 112.5, "E", wi(wdir) < 157.5, "SE", '
           'wi(wdir) < 202.5, "S", wi(wdir) < 247.5, "SW", wi(wdir) < 292.5, "W", wi(wdir) < 337.5, "NW", "N")')
WIND = f'$if({MS} < 0.3, "Calm", {COMPASS} + " " + mu(round, {MS} / 0.44704) + " mph · " + {BEAUFORT})$'
NOW_ICON = f'$if({DAWN}, "sunrise", {DUSK}, "sunset", {weather_icon("wi(icon)", f"({MIN_NOW} >= {SR} & {MIN_NOW} < {SS})")})$'
NEXT_SUN = (f'$if({MIN_NOW} < {SR} | {MIN_NOW} >= {SS}, "Sunrise " + df(HH:mm, ai(sunrise)), '
            f'"Sunset " + df(HH:mm, ai(sunset)))$')

now_block = stack([
    stack([icon(NOW_ICON, 50, ON_SKY), txt("$wi(temp)$°", 46, ON_SKY, text_family=LIGHT)], "HORIZONTAL_CENTER", 6),
    txt("$wi(cond)$", 14, ON_SKY, text_size_type="FIXED_WIDTH", text_width=200.0, text_align="RIGHT", text_lines=1),
    txt(WIND, 12, ON_SKY_MUTED, text_size_type="FIXED_WIDTH", text_width=200.0, text_align="RIGHT", text_lines=1),
    txt(NEXT_SUN, 12, ON_SKY_MUTED),
], "VERTICAL_RIGHT", 3, internal_title="Now")
tap(now_block, APP_WEATHER)

HW = (SKY_W - 2 * SP) / 6


def hour(h):
    hr = f"df(H, a{h}h)*60"
    isday = f"({hr} >= {SR} & {hr} < {SS})"
    return overlap([rect(HW, 76, "#00000000"),
                    stack([txt(f"$df(HH:00, a{h}h)$", 12, ON_SKY_MUTED),
                           icon(f"${weather_icon(f'wf(icon, 0, {h})', isday)}$", 26, ON_SKY),
                           txt(f"$wf(temp, 0, {h})$°", 15, ON_SKY)], "VERTICAL_CENTER", 4,
                          position_anchor="CENTER")])


hours = stack([rect(SKY_W - 2 * SP, 1, SKY_LINE, anchor="TOPLEFT"),
               stack([hour(h) for h in range(1, 7)], "HORIZONTAL_TOP", 0)],
              "VERTICAL_LEFT", 8, internal_title="Next 6 hours")
tap(hours, APP_WEATHER)

# ---------- the atmosphere drawn on the sky (all still shapes; positions fixed, shown by the weather) ----------
import random
rnd = random.Random(7)          # fixed seed: the same scatter every build
# Keep drops, flakes and stars off the writing: the date/time, the "now" block, and the forecast row.
# Tight boxes round each piece of writing / icon, so the rest of the sky stays evenly scattered.
_HC = [SP + (SKY_W - 2 * SP) / 6 * (k + 0.5) for k in range(6)]          # forecast column centres
TEXT_BOXES = ([(SP - 4, 10, 130, 50), (SP - 4, 52, 170, 126),                # date + day, time
               (SKY_W - 140, 8, SKY_W - SP + 4, 74), (SKY_W - 175, 74, SKY_W - SP + 4, 134)]  # now block
              + [(c - 24, 180, c + 24, 256) for c in _HC])                    # each forecast hour


def spot(w, h, top=6, bottom=None):
    bottom = bottom or SKY_H - h - 6
    while True:
        x, y = rnd.uniform(10, SKY_W - w - 10), rnd.uniform(top, bottom)
        if not any(x + w > a and x < c and y + h > b and y < d for a, b, c, d in TEXT_BOXES):
            return x, y
IC = "wi(icon)"
WET = f"({IC} = RAIN | {IC} = SHOWER | {IC} = TSTORM | {IC} = SLEET)"
WHITE = lambda a: f"#{a:02X}FFFFFF"


def dot(x, y, d, color, cond=None, **kw):
    m = rect(d, d, color, d / 2, anchor="TOPLEFT", position_offset_x=float(x), position_offset_y=float(y), **kw)
    return visible(m, cond) if cond else m


def glyph(name, x, y, size, color, title):
    """A Weather Icons shape (raindrop / snowflake) placed on the sky."""
    return {"internal_type": "FontIconModule", "internal_title": title,
            "icon_set": "iconify://wi?name=Weather%20Icons", "icon_icon": name, "icon_size": float(size),
            "paint_color": color, "position_anchor": "TOPLEFT",
            "position_offset_x": float(x), "position_offset_y": float(y)}


def raindrop(x, y, size, n):
    """A real drop shape (teardrop), sizes varied; the first N show, N by how heavy the rain is."""
    shown = f"{WET} & {n} < if({IC} = TSTORM, 44, {IC} = RAIN, 32, 18)"
    return visible(glyph("raindrop", x, y, size, WHITE(0x8C), "Raindrop"), shown)


def flake(x, y, size, n):
    """A six-armed snowflake (hail: small solid stones)."""
    shown = f"({IC} = SNOW & {n} < 40) | ({IC} = SLEET & {n} < 16) | ({IC} = HAIL & {n} < 26)"
    m = visible(glyph("snowflake-cold", x, y, size, WHITE(0xD0), "Snowflake"), shown)
    m["internal_toggles"]["icon_icon"] = 10
    m["internal_formulas"]["icon_icon"] = f'$if({IC} = HAIL, "hail", "snowflake-cold")$'
    return m


def cloud(x, y, scale, alpha, cond):
    """A soft cloud: overlapping translucent circles on a flat base."""
    puffs = [(0, 14, 26), (16, 4, 34), (40, 10, 28), (58, 18, 20)]
    parts = [rect(d * scale, d * scale, WHITE(alpha), d * scale / 2, anchor="TOPLEFT",
                  position_offset_x=float(px * scale), position_offset_y=float(py * scale))
             for px, py, d in puffs]
    parts.append(rect(74 * scale, 12 * scale, WHITE(alpha), 6 * scale, anchor="TOPLEFT",
                      position_offset_x=0.0, position_offset_y=float(28 * scale)))
    return visible(overlap(parts, position_anchor="TOPLEFT", position_offset_x=float(x),
                           position_offset_y=float(y), internal_title="Cloud"), cond)


# Sun / moon along a low arc across the sky: x by how far through the day (or night) it is,
# height a parabola peaking mid-arc.
ARC_L, ARC_R, ARC_BASE, ARC_H = 36, SKY_W - 36, 168, 112
DAY_F = f"(({MIN_NOW} - {SR}) / mu(max, 1, {SS} - {SR}))"
NIGHT_LEN = f"(1440 - {SS} + {SR})"
NIGHT_F = f"(if({MIN_NOW} >= {SS}, {MIN_NOW} - {SS}, {MIN_NOW} + 1440 - {SS}) / {NIGHT_LEN})"


def body(frac, d, color, cond, glow):
    x = f"${ARC_L} + {frac} * {ARC_R - ARC_L} - {glow / 2}$"
    y = f"${ARC_BASE} - 4 * {ARC_H} * {frac} * (1 - {frac}) - {glow / 2}$"
    m = overlap([rect(glow, glow, "#33FFE9A8" if color == "sun" else WHITE(0x22), glow / 2, anchor="CENTER"),
                 rect(d, d, "#FFFFE9A8" if color == "sun" else "#FFF1EEE2", d / 2, anchor="CENTER")],
                position_anchor="TOPLEFT", internal_title="Sun" if color == "sun" else "Moon",
                internal_toggles={"position_offset_x": 10, "position_offset_y": 10},
                internal_formulas={"position_offset_x": x, "position_offset_y": y})
    return visible(m, cond)


arc = [dot(ARC_L + f * (ARC_R - ARC_L) - 1.5, ARC_BASE - 4 * ARC_H * f * (1 - f) - 1.5, 3, WHITE(0x26))
       for f in [i / 16 for i in range(17)]]
CLEARISH = f"({IC} = CLEAR | {IC} = PCLOUDY | {IC} = MCLOUDY)"
atmosphere = overlap(
    [rect(SKY_W, SKY_H, "#00000000", anchor="TOPLEFT")]
    # stars on clear nights
    + [dot(*spot(3, 3, 8, 168), rnd.choice([1.5, 2, 2, 2.5, 3]),
           WHITE(rnd.choice([0x55, 0x77, 0x99, 0xBB])), f"{NIGHT} & ({IC} = CLEAR | {IC} = PCLOUDY)",
           internal_title="Star") for _ in range(22)]
    + arc
    + [body(DAY_F, 20, "sun", f"{MIN_NOW} >= {SR} & {MIN_NOW} < {SS} & {CLEARISH}", 40),
       body(NIGHT_F, 16, "moon", f"{NIGHT} & {IC} != TSTORM", 30)]
    # clouds: one when partly cloudy, three when mostly cloudy / overcast / wet
    + [cloud(SKY_W * 0.55, 22, 1.0, 0x30, f"({IC} != CLEAR & {IC} != FOG)"),
       cloud(SKY_W * 0.18, 58, 0.8, 0x24, f"({IC} = MCLOUDY | {IC} = CLOUDY | {WET} | {IC} = SNOW)"),
       cloud(SKY_W * 0.74, 92, 0.7, 0x20, f"({IC} = CLOUDY | {WET} | {IC} = SNOW)")]
    # fog: soft bands
    + [visible(rect(SKY_W * w, 14, WHITE(0x2A), 7, anchor="TOPLEFT", position_offset_x=float(SKY_W * x),
                    position_offset_y=float(y), internal_title="Fog"), f"{IC} = FOG")
       for x, y, w in [(0.05, 60, 0.6), (0.3, 100, 0.65), (0.0, 140, 0.5), (0.45, 180, 0.5), (0.1, 222, 0.7)]]
    # raindrops and snowflakes, scattered (the first N are shown, N by how heavy it is)
    + [raindrop(*spot(sz, sz), sz, n) for n, sz in enumerate(rnd.choice([11, 13, 13, 15, 17]) for _ in range(44))]
    + [flake(*spot(sz, sz), sz, n) for n, sz in enumerate(rnd.choice([8, 10, 10, 12, 14, 16]) for _ in range(40))],
    internal_title="Atmosphere")

BANNER_H = SKY_H + INSET * 2
banner = overlap([
    rect(W, BANNER_H, C(SURFACE), 22, anchor="TOP"),
    rect(W, BANNER_H / 2, C(SURFACE), anchor="BOTTOM"),
    rect(SKY_W, SKY_H, SKY, 16, anchor="TOP", position_padding_top=float(INSET),
         fx_gradient="VERTICAL", fx_gradient_width=100.0, fx_gradient_offset=0.0,
         internal_toggles={"paint_color": 10, "fx_gradient_color": 10},
         internal_formulas={"paint_color": SKY, "fx_gradient_color": SKY_LOW}),
    pad(atmosphere, "TOP", t=INSET),
    pad(clock, "TOPLEFT", l=INSET + SP, t=INSET + SP),
    pad(now_block, "TOPRIGHT", r=INSET + SP, t=INSET + SP),
    pad(hours, "TOPLEFT", l=INSET + SP, t=INSET + SKY_H - 96),
], internal_title="Banner")

# ================= 2. What's on (lake): one list, paged with ▲ ▼ =================
# A home-screen widget can't scroll, so the list pages instead: ▲ / ▼ in the header step
# through the events PAGE at a time (KWGT "switch global" tap actions on the calpage global).
PAGE = 5          # events per page
MAX_EVENTS = 20   # events counted (4 pages)

GLOBALS = {
    "calpage": {"index": 0, "type": "NUMBER", "title": "Calendar page", "value": 0},
    "calcount": {"index": 1, "type": "NUMBER", "title": "Calendar events", "value": 0, "toggles": 10,
                 "global_formula": "$" + " + ".join(f'if(ci(title, {k}) != "", 1, 0)' for k in range(MAX_EVENTS)) + "$"},
    # first event shown: the page, held inside the list if events have dropped off since
    "calidx": {"index": 2, "type": "NUMBER", "title": "Calendar first event", "value": 0, "toggles": 10,
               "global_formula": f"$mu(min, gv(calpage), mu(floor, mu(max, 0, gv(calcount) - 1) / {PAGE})) * {PAGE}$"},
}

S = lambda i: f"ci(start, {i})"


def journey_globals(j, base):
    """The journey for card j, worked out once and reused by its text, visibility and height.
    Layers: trip (eligible?) -> route (OSRM seconds) -> drive (min, +15%) -> leave (drive + 10 min);
    mins (minutes until the start) and show (trip and a route found) for the card to use."""
    i = f"(gv(calidx) + {j})"
    start_m = f"(df(H, {S(i)})*60 + df(m, {S(i)}))"
    geo = lambda k: (f'wg("https://photon.komoot.io/api/?limit=1&q=" + tc(url, ci(loc, {i})), json, '
                     f'".features[0].geometry.coordinates[{k}]")')
    osrm = (f'wg("https://router.project-osrm.org/route/v1/driving/" + li(lon) + "," + li(lat) + ";" + '
            f'{geo(0)} + "," + {geo(1)} + "?overview=false", json, ".routes[0].duration")')
    f = lambda n, typ, title, formula: (f"{n}{j}", {"index": base + n_order.index(n), "type": typ,
                                                    "title": f"Card {j + 1} {title}", "value": 0 if typ == "NUMBER" else "", "toggles": 10,
                                                    "global_formula": formula})
    n_order = ["trip", "mins", "route", "drive", "leave", "show"]
    return dict([
        # today, timed, not started, has a place, starts within 4 hours
        f("trip", "NUMBER", "journey due", f'$if(ci(loc, {i}) != "" & ci(allday, {i}) = 0 & df(yyyyMMdd, {S(i)}) = df(yyyyMMdd)'
                                          f' & {start_m} > {MIN_NOW}'
                                          f' & {start_m} - {MIN_NOW} <= 240, 1, 0)$'),
        f("mins", "NUMBER", "minutes to start", f"${start_m} - {MIN_NOW}$"),
        # the only place the web lookups live; asked for only when the journey is due
        f("route", "TEXT", "route seconds", f'$if(gv(trip{j}) = 1, {osrm}, "")$'),
        f("drive", "TEXT", "drive minutes", f'$if(gv(route{j}) != "", mu(ceil, gv(route{j}) * 1.15 / 60), "")$'),
        f("leave", "TEXT", "leave allowance", f'$if(gv(drive{j}) != "", gv(drive{j}) + 10, "")$'),
        f("show", "NUMBER", "show leave-by", f'$if(gv(trip{j}) = 1 & gv(route{j}) != "", 1, 0)$'),
    ])


for _j in range(PAGE):
    GLOBALS.update(journey_globals(_j, 3 + _j * 6))
E = lambda i: f"ci(end, {i})"
DAY = lambda d: f"df(yyyyMMdd, {d})"
TODAY_N, NOW_N = "df(yyyyMMdd)", "df(yyyyMMddHHmm)"
HAS = lambda i: f'ci(title, {i}) != ""'
START_M = lambda i: f"(df(H, {S(i)})*60 + df(m, {S(i)}))"
# started: an earlier day, or today at/before now (days and minutes compared separately; 12-digit
# date numbers like 202611131605 are too big for KWGT's sums and gave wrong answers)
STARTED = lambda i: f"({DAY(S(i))} < {TODAY_N} | ({DAY(S(i))} = {TODAY_N} & {START_M(i)} <= {MIN_NOW}))"
IS_ON = lambda i: f"({HAS(i)} & {STARTED(i)})"   # on now


def row(j):
    i = f"(gv(calidx) + {j})"
    # the next thing today: not started yet, and everything before it has
    nxt = (f"({HAS(i)} & ci(allday, {i}) = 0 & {DAY(S(i))} = {TODAY_N} & {START_M(i)} > {MIN_NOW}"
           f" & ({i} = 0 | {IS_ON(f'({i} - 1)')}))")
    when = (f'$if({DAY(S(i))} <= {TODAY_N}, "Today", {DAY(S(i))} = df(yyyyMMdd, a1d), "Tomorrow", df("EEE d MMM", {S(i)}))'
            f' + " · " + if(ci(allday, {i}) = 1, "All day",\n'
            f'  {IS_ON(i)}, "Now · until " + if({DAY(E(i))} = {TODAY_N}, df(HH:mm, {E(i)}), df("EEE HH:mm", {E(i)})),\n'
            f'  df(HH:mm, {S(i)}) + " – " + df(HH:mm, {E(i)}))'
            f' + if({nxt}, "  [c=" + {CI(LAKE)} + "][b]" + tf({S(i)}) + "[/b][/c]", "")$')
    has_loc = f'ci(loc, {i}) != ""'
    # "Leave by 13:52 · 27 min drive" / "Leave now": from this card's journey globals (see journey_globals)
    due = (f'(ci(loc, {i}) != "" & ci(allday, {i}) = 0 & {DAY(S(i))} = {TODAY_N}'
           f' & {START_M(i)} > {MIN_NOW} & {START_M(i)} - {MIN_NOW} <= 240)')
    shows_leave = f"({due} & tc(len, gv(drive{j})) > 0)"
    left = f"({START_M(i)} - {MIN_NOW} - gv(leave{j}))"            # minutes until it's time to go
    at = f"({MIN_NOW} + {left})"                       # leave-by, as minutes since midnight
    hhmm = f'(if({at} < 600, "0", "") + mu(floor, {at} / 60) + ":" + if({at} % 60 < 10, "0", "") + ({at} % 60))'
    leave = (f'$if({START_M(i)} - {MIN_NOW} <= gv(leave{j}), "[c={AMBER}][b]Leave now[/b][/c] · " + gv(drive{j}) + " min drive",'
             f' "[c=" + {CI(LAKE)} + "][b]Leave by " + {hhmm} + "[/b][/c] · " + gv(drive{j}) + " min drive")$')
    text_w = {"internal_toggles": {"text_width": 10},
              "internal_formulas": {"text_width": f"$if({has_loc}, {IW - 104}, {IW - 48})$"}}

    def t(expr, size, color, **kw):
        m = txt(expr, size, color, text_size_type="FIXED_WIDTH", text_width=float(IW - 48), text_lines=1, **kw)
        m["internal_toggles"].update(text_w["internal_toggles"])
        m.setdefault("internal_formulas", {}).update(text_w["internal_formulas"])
        return m

    # Directions: opens Google Maps driving directions to the event's location (only when it has one)
    maps = f'$"https://www.google.com/maps/dir/?api=1&travelmode=driving&destination=" + tc(url, ci(loc, {i}))$'
    go = visible(overlap([rect(44, 44, C(FILL_ON), 12),
                          icon('$"direction-up-right"$', 22, C(LAKE))],
                         position_anchor="CENTERRIGHT", position_padding_right=10.0, internal_title="Directions",
                         internal_events=[{"type": "SINGLE_TAP", "action": "OPEN_LINK", "url": maps}]), has_loc)
    chip = overlap([
        rect(IW, 64, f"$if({IS_ON(i)}, if({NIGHT}, {FILL_ON[1]}, {FILL_ON[0]}), if({NIGHT}, {FILL[1]}, {FILL[0]}))$", 12),
        rect(4, 34, f"$ci(ccolor, {i})$", 2, anchor="CENTERLEFT", position_padding_left=14.0),
        pad(stack([t(f"[b]$ci(title, {i})$[/b]", 16, C(TEXT)),
                   t(when, 13, C(MUTED)),
                   visible(t(leave, 13, C(LAKE)), shows_leave)],
                  "VERTICAL_LEFT", 3), "CENTERLEFT", l=30),
        go,
    ])
    # a row with a "leave by" line is taller
    chip["viewgroup_items"][0].update(internal_toggles={**chip["viewgroup_items"][0]["internal_toggles"], "shape_height": 10})
    chip["viewgroup_items"][0].setdefault("internal_formulas", {})["shape_height"] = \
        f'$if({shows_leave}, 82, 64)$'
    strip_m = strip(72, chip, title=f"Row {j + 1}")
    strip_m["viewgroup_items"][0].update(internal_toggles={**strip_m["viewgroup_items"][0]["internal_toggles"], "shape_height": 10})
    strip_m["viewgroup_items"][0].setdefault("internal_formulas", {})["shape_height"] = \
        f'$if({shows_leave}, 90, 72)$'
    return tap(visible(strip_m, HAS(i)), APP_CAL)


def page_button(label, can, to):
    b = overlap([rect(44, 32, C(FILL), 10),
                 txt(label, 13, f"$if({can}, if({NIGHT}, {LAKE[1]}, {LAKE[0]}), if({NIGHT}, {DIVIDER[1]}, {DIVIDER[0]}))$",
                     position_anchor="CENTER")], internal_title=f"Page {label}")
    b["internal_events"] = [{"type": "SINGLE_TAP", "action": "SWITCH_GLOBAL", "switch": "calpage", "switch_text": to}]
    return b


UP_OK, DOWN_OK = "gv(calidx) > 0", f"gv(calidx) + {PAGE} < gv(calcount)"
pager = visible(stack([
    txt(f'$(gv(calidx) + 1) + "–" + mu(min, gv(calidx) + {PAGE}, gv(calcount)) + " of " + gv(calcount)$', 12, C(MUTED)),
    page_button("▲", UP_OK, f"$mu(max, 0, gv(calidx) / {PAGE} - 1)$"),
    page_button("▼", DOWN_OK, f"$if({DOWN_OK}, gv(calidx) / {PAGE} + 1, gv(calidx) / {PAGE})$"),
], "HORIZONTAL_CENTER", 8, internal_title="Pager"), f"gv(calcount) > {PAGE}")

header = strip(48,
               tap(pad(stack([rect(4, 16, C(LAKE), 2), txt("[b]What's on[/b]", 16, C(LAKE))], "HORIZONTAL_CENTER", 8),
                       "CENTERLEFT", l=INSET + 4), APP_CAL),
               pad(pager, "CENTERRIGHT", r=INSET),
               title="What's on")

no_events = visible(strip(36, pad(txt("No upcoming events", 14, C(MUTED)), "CENTERLEFT", l=INSET + 4),
                          title="No events"), 'ci(title, 0) = ""')

bottom = overlap([rect(W, 40, C(SURFACE), 22, anchor="TOP"), rect(W, 20, C(SURFACE), anchor="TOP")],
                 internal_title="Bottom edge")

whats_on = stack([header] + [row(j) for j in range(PAGE)] + [no_events], "VERTICAL_LEFT", 0,
                 internal_title="What's on")
items = [banner, whats_on, bottom]


def offsets_to_padding(o):
    if isinstance(o, dict):
        for a, b in (("position_offset_x", "position_padding_left"), ("position_offset_y", "position_padding_top")):
            if a in o:
                o[b] = o.pop(a)
            t, fm = o.get("internal_toggles", {}), o.get("internal_formulas", {})
            if a in t:
                t[b] = t.pop(a)
            if a in fm:
                fm[b] = fm.pop(a)
        for v in o.values():
            offsets_to_padding(v)
    elif isinstance(o, list):
        for x in o:
            offsets_to_padding(x)


offsets_to_padding(banner)

# Clip: a komponent, so the calendar globals come with it when pasted
komponent = {"internal_type": "KomponentModule", "internal_title": "Misty Forest", "globals_list": GLOBALS,
             "position_anchor": "TOPLEFT", "position_offset_x": 10.0, "position_offset_y": 10.0,
             "viewgroup_items": [stack(items, "VERTICAL_LEFT", 0)]}
with open(OUT, "w") as f:
    f.write("##KUSTOMCLIP##\n" + json.dumps({"clip_version": 1, "clip_cut": [], "clip_modules": [komponent]},
                                           separators=(",", ":"), ensure_ascii=False) + "\n##KUSTOMCLIP##\n")
print("wrote", OUT)

# The same widget as a whole preset (.kwgt = a zip holding preset.json), loaded from KWGT's
# menu instead of pasted. Layout as in presets exported by KWGT itself.
import zipfile
preset = {
    "preset_info": {"version": 13, "title": "Misty Forest",
                    "description": "Clock, weather and calendar in the style of the Home Kiosk (Misty Forest v2)",
                    "author": "", "email": "", "archive": None, "features": "WEATHER FORECAST CALENDAR",
                    "width": W, "height": 760, "xscreens": 0, "yscreens": 0,
                    "release": 377435216, "locked": False, "pflags": 0},
    "preset_root": {"internal_type": "RootLayerModule", "config_scale_value": 100.0, "globals_list": GLOBALS,
                    "viewgroup_items": [stack(items, "VERTICAL_LEFT", 0, internal_title="Misty Forest")]},
}
KWGT = os.path.join(os.path.dirname(OUT), "misty-forest.kwgt")
with zipfile.ZipFile(KWGT, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("preset.json", json.dumps(preset, indent=2, ensure_ascii=False))
print("wrote", KWGT)
