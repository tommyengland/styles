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


SKY = (f"$if({DAWN} | {DUSK}, #FFB0705A,\n"
       f"  {NIGHT}, if(wi(icon) = CLEAR | wi(icon) = PCLOUDY, #FF1E2B3A, #FF29313A),\n"
       "  wi(icon) = CLEAR, #FF4C86A8,\n"
       "  wi(icon) = PCLOUDY | wi(icon) = MCLOUDY, #FF5B819A,\n"
       "  wi(icon) = CLOUDY, #FF66777F,\n"
       "  wi(icon) = RAIN | wi(icon) = SHOWER, #FF52646F,\n"
       "  wi(icon) = TSTORM, #FF434B57,\n"
       "  wi(icon) = SNOW | wi(icon) = SLEET | wi(icon) = HAIL, #FF7D8E99,\n"
       "  wi(icon) = FOG, #FF77858A,\n"
       "  #FF5B819A)$")

APP = lambda comp, label: ("intent:#Intent;action=android.intent.action.MAIN;category=android.intent.category.LAUNCHER;"
                           f"component={comp};S.org.kustom.intent.label={label};end")
APP_CLOCK = APP("com.oneplus.deskclock/com.oplus.alarmclock.AlarmClock", "Clock")
APP_WEATHER = APP("com.weawow/.GoldenIcon", "Weawow")
APP_CAL = APP("biz.codespark.xcalendarapp/crc64c040fa4b38b83970.MainActivity", "OneCalendar")
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

BANNER_H = SKY_H + INSET * 2
banner = overlap([
    rect(W, BANNER_H, C(SURFACE), 22, anchor="TOP"),
    rect(W, BANNER_H / 2, C(SURFACE), anchor="BOTTOM"),
    rect(SKY_W, SKY_H, SKY, 16, anchor="TOP", position_padding_top=float(INSET)),
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
E = lambda i: f"ci(end, {i})"
DAY = lambda d: f"df(yyyyMMdd, {d})"
TODAY_N, NOW_N = "df(yyyyMMdd)", "df(yyyyMMddHHmm)"
HAS = lambda i: f'ci(title, {i}) != ""'
IS_ON = lambda i: f"({HAS(i)} & df(yyyyMMddHHmm, {S(i)}) <= {NOW_N})"   # on now


def row(j):
    i = f"(gv(calidx) + {j})"
    # the next thing today: not started yet, and everything before it has
    nxt = f"({HAS(i)} & {DAY(S(i))} = {TODAY_N} & df(yyyyMMddHHmm, {S(i)}) > {NOW_N} & ({i} = 0 | {IS_ON(f'({i} - 1)')}))"
    when = (f'$if({DAY(S(i))} <= {TODAY_N}, "Today", {DAY(S(i))} = df(yyyyMMdd, a1d), "Tomorrow", df("EEE d MMM", {S(i)}))'
            f' + " · " + if(ci(allday, {i}) = 1, "All day",\n'
            f'  {IS_ON(i)}, "Now · until " + if({DAY(E(i))} = {TODAY_N}, df(HH:mm, {E(i)}), df("EEE HH:mm", {E(i)})),\n'
            f'  df(HH:mm, {S(i)}) + " – " + df(HH:mm, {E(i)}))'
            f' + if({nxt}, "  [c=" + {CI(LAKE)} + "][b]" + tf({S(i)}) + "[/b][/c]", "")$')
    chip = overlap([
        rect(IW, 64, f"$if({IS_ON(i)}, if({NIGHT}, {FILL_ON[1]}, {FILL_ON[0]}), if({NIGHT}, {FILL[1]}, {FILL[0]}))$", 12),
        rect(4, 34, f"$ci(ccolor, {i})$", 2, anchor="CENTERLEFT", position_padding_left=14.0),
        pad(stack([txt(f"[b]$ci(title, {i})$[/b]", 16, C(TEXT), text_size_type="FIXED_WIDTH",
                       text_width=float(IW - 48), text_lines=1),
                   txt(when, 13, C(MUTED), text_size_type="FIXED_WIDTH", text_width=float(IW - 48), text_lines=1)],
                  "VERTICAL_LEFT", 3), "CENTERLEFT", l=30),
    ])
    return tap(visible(strip(72, chip, title=f"Row {j + 1}"), HAS(i)), APP_CAL)


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
