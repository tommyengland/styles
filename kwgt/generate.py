import json
import os
OUT=os.path.dirname(os.path.abspath(__file__))+"/"
W=480
CARD="#CC1E1F24"; TILE="#CC2A2C33"; ACCENT="#FFFFB74D"
def txt(expr, size=None, glob_color="txt", glob_font=None, **kw):
    m={"internal_type":"TextModule","text_expression":expr}
    if size: m["text_size"]=float(size)
    t={};g={}
    if glob_color: t["paint_color"]=100; g["paint_color"]=glob_color
    if glob_font: t["text_family"]=100; g["text_family"]=glob_font
    if t: m["internal_toggles"]=t; m["internal_globals"]=g
    m.update(kw); return m
def shape(w,h,color,corners=24.0,**kw):
    m={"internal_type":"ShapeModule","shape_type":"RECT","shape_width":float(w),"shape_height":float(h),"shape_corners":float(corners),"paint_color":color,"position_anchor":"TOPLEFT"}
    m.update(kw); return m
def stack(items, stacking="VERTICAL_LEFT", margin=0, **kw):
    m={"internal_type":"StackLayerModule","config_stacking":stacking,"config_margin":float(margin),"viewgroup_items":items}
    m.update(kw); return m
def card(w,h,color,content,pad=20,title=None,tap=None,anchor="TOPLEFT"):
    content.update({"position_anchor":anchor,"position_padding_left":float(pad),"position_padding_top":float(pad),"position_padding_right":float(pad),"position_padding_bottom":float(pad)})
    if anchor=="CENTER": content.update(position_padding_top=0.0,position_padding_bottom=0.0,position_padding_left=0.0,position_padding_right=0.0)
    m={"internal_type":"OverlapLayerModule","viewgroup_items":[shape(w,h,color),content]}
    if title: m["internal_title"]=title
    if tap: m["internal_events"]=[{"type":"SINGLE_TAP","action":"LAUNCH_APP","intent":tap}]
    return m
def icon(formula, size=None, color_formula=None, color=None):
    m={"internal_type":"FontIconModule","icon_set":"iconify://wi?name=Weather%20Icons",
       "internal_toggles":{"icon_icon":10},"internal_formulas":{"icon_icon":formula}}
    if size: m["icon_size"]=float(size)
    if color_formula: m["internal_toggles"]["paint_color"]=10; m["internal_formulas"]["paint_color"]=color_formula
    elif color: m["paint_color"]=color
    return m
def wmap(src):
    pairs=[("CLEAR","day-sunny","night-clear"),("PCLOUDY","day-cloudy","night-alt-cloudy"),("MCLOUDY","day-cloudy","night-alt-cloudy"),
           ("CLOUDY","cloudy","cloudy"),("RAIN","day-rain","night-alt-rain"),("SHOWER","day-showers","night-alt-showers"),
           ("TSTORM","day-thunderstorm","night-alt-thunderstorm"),("SNOW","day-snow","night-alt-snow"),("SLEET","day-sleet","night-alt-sleet"),
           ("FOG","day-fog","night-fog"),("WINDY","day-windy","night-alt-cloudy-windy"),("TORNADO","tornado","tornado"),("HAIL","hail","hail")]
    parts=[]
    for c,d,n in pairs:
        parts.append(f'{src} = {c}, ' + (f'"{d}"' if d==n else f'if(ai(isday), "{d}", "{n}")'))
    return "$if(" + ",\n  ".join(parts) + ',\n  "na")$'
TEMPCOL=lambda t: f"$if({t} >= 30, #FFFF7043, {t} >= 20, #FFFFCA28, {t} >= 10, #FF9CCC65, {t} >= 0, #FF81D4FA, #FF5C9DFF)$"

APP_CLOCK="intent:#Intent;action=android.intent.action.MAIN;category=android.intent.category.LAUNCHER;component=com.oneplus.deskclock/com.oplus.alarmclock.AlarmClock;S.org.kustom.intent.label=Clock;end"
APP_WEAWOW="intent:#Intent;action=android.intent.action.MAIN;category=android.intent.category.LAUNCHER;component=com.weawow/.GoldenIcon;S.org.kustom.intent.label=Weawow;end"
APP_WEATHER="intent:#Intent;action=android.intent.action.MAIN;category=android.intent.category.LAUNCHER;component=net.oneplus.weather/com.oplus.weather.main.view.WeatherMainActivity;S.org.kustom.intent.label=Weather;end"
APP_CAL="intent:#Intent;action=android.intent.action.MAIN;category=android.intent.category.LAUNCHER;component=biz.codespark.xcalendarapp/crc64c040fa4b38b83970.MainActivity;S.org.kustom.intent.label=OneCalendar;end"

# Current-weather icon: keeps the original sunrise/sunset golden-hour behaviour
cur_icon = icon("$if(df(S) >= ai(sunrise)*60 - 1800 & df(S) < ai(sunrise)*60, \"sunrise\",\n  df(S) >= ai(sunset)*60 & df(S) < ai(sunset)*60 + 1800, \"sunset\",\n  " + wmap("wi(icon)")[1:-1].replace("\n","\n  ") + ")$",
    size=90, color_formula="$if(df(S) >= ai(sunrise)*60 - 1800 & df(S) < ai(sunrise)*60,\n  ce(#FFFF8C00, #FFFFEB3B, (df(S) - (ai(sunrise)*60 - 1800)) / 18),\n  df(S) >= ai(sunset)*60 & df(S) < ai(sunset)*60 + 1800,\n  ce(#FFFFEB3B, #FFFF3D00, (df(S) - ai(sunset)*60) / 18),\n  #FFFFB74D)$")

# ---------- 1. Hero card: clock + current weather ----------
clock = stack([
    txt("$df(HH:mm)$", 64, glob_font="lead txt"),
    txt("$df(EEEE)$", 26, text_family="kfile://org.kustom.provider/fonts/Roboto-Light.ttf"),
    txt("$tc(up, df(dd MMMM))$", 16, glob_color="headers", glob_font="lead txt", position_padding_top=4.0),
], internal_events=[{"type":"SINGLE_TAP","action":"LAUNCH_APP","intent":APP_CLOCK}], internal_title="Clock")
weather_now = stack([
    stack([cur_icon,
           txt("$wi(temp)$°", 52, glob_color=None, glob_font="lead txt",
               internal_toggles={"text_family":100,"paint_color":10}, internal_globals={"text_family":"lead txt"},
               internal_formulas={"paint_color":TEMPCOL("wi(temp)")})], "HORIZONTAL_CENTER", 6),
    txt("$wi(cond)$", 16, text_size_type="FIXED_WIDTH", text_width=190.0, text_align="RIGHT", text_lines=1),
    txt("$li(loc)$", 14, glob_color="headers", text_size_type="FIXED_WIDTH", text_width=190.0, text_align="RIGHT", text_lines=1),
], "VERTICAL_RIGHT", 2, internal_events=[{"type":"SINGLE_TAP","action":"LAUNCH_APP","intent":APP_WEAWOW}], internal_title="Weather now")
hero_row = {"internal_type":"OverlapLayerModule","viewgroup_items":[
    dict(clock, position_anchor="LEFT"), dict(weather_now, position_anchor="RIGHT")],
    "position_anchor":"CENTER"}
hero = {"internal_type":"OverlapLayerModule","internal_title":"Hero card","viewgroup_items":[
    shape(W,190,CARD,28), dict(stack([shape(W-44,1,"#00000000",0), hero_row]), position_anchor="CENTER")]}
# simpler: inner overlap sized by an invisible spacer
hero["viewgroup_items"][1]={"internal_type":"OverlapLayerModule","position_anchor":"CENTER","viewgroup_items":[shape(W-44,160,"#00000000",0,position_anchor="CENTER"),
    dict(clock, position_anchor="CENTERLEFT"), dict(weather_now, position_anchor="CENTERRIGHT")]}

# ---------- 2. Chips row (HA "mushroom chips") ----------
WIND = ('$if(wi(wspeed) > 0, mu(round, wi(wspeed)) + " " + wi(speedu) + " " + '
        'if(wi(wdir)<22.5,"N",wi(wdir)<67.5,"NE",wi(wdir)<112.5,"E",wi(wdir)<157.5,"SE",wi(wdir)<202.5,"S",wi(wdir)<247.5,"SW",wi(wdir)<292.5,"W",wi(wdir)<337.5,"NW","N"), "Calm")$')
SUN = '$if(df(S) < ai(sunrise)*60 | df(S) >= ai(sunset)*60, df(HH:mm, ai(sunrise)), df(HH:mm, ai(sunset)))$'
SUNICON = '$if(df(S) < ai(sunrise)*60 | df(S) >= ai(sunset)*60, "sunrise", "sunset")$'
CW=(W-20)/3
def chip(ic, label, col):
    return card(CW,48,TILE, stack([icon(ic,22,color=col), txt(label,15)], "HORIZONTAL_CENTER", 8), anchor="CENTER")
chips = stack([chip('$"strong-wind"$', WIND, "#FF80CBC4"),
               chip('$"humidity"$', "$wi(hum)$%", "#FF64B5F6"),
               chip(SUNICON, SUN, "#FFFFB74D")], "HORIZONTAL_TOP", 10, internal_title="Chips",
              internal_events=[{"type":"SINGLE_TAP","action":"LAUNCH_APP","intent":APP_WEATHER}])

# ---------- 3. Hourly forecast tiles ----------
TW=(W-30)/4
def hour_tile(h):
    return card(TW,118,TILE, stack([
        txt(f"$df(HH:00, a{h}h)$", 14, glob_color="headers"),
        icon(wmap(f"wf(icon, 0, {h})"), 34, color=ACCENT),
        txt(f"$wf(temp, 0, {h})$°", 20, glob_color=None, glob_font="lead txt",
            internal_toggles={"text_family":100,"paint_color":10}, internal_globals={"text_family":"lead txt"},
            internal_formulas={"paint_color":TEMPCOL(f"wf(temp, 0, {h})")}),
    ], "VERTICAL_CENTER", 6), anchor="CENTER")
forecast = stack([
    txt("Forecast", 16, glob_color="headers", glob_font="bold", position_padding_left=6.0),
    stack([hour_tile(h) for h in (1,2,3,4)], "HORIZONTAL_TOP", 10)
], "VERTICAL_LEFT", 8, internal_title="Forecast",
   internal_events=[{"type":"SINGLE_TAP","action":"LAUNCH_APP","intent":APP_WEATHER}])

# ---------- 4. Calendar: one HA-style entity row per event ----------
def when(i):
    d=f"ci(start, {i})"
    day=f'if(df(Dyyyy, {d}) = df(Dyyyy), "Today", df(Dyyyy, {d}) = df(Dyyyy, a1d), "Tomorrow", df("EEE dd MMM", {d}))'
    return f'${day} + " · " + if(ci(allday, {i}) = 1, "All day", df(HH:mm, {d}) + " – " + df(HH:mm, ci(end, {i})))$'
def event_row(i):
    row = {"internal_type":"OverlapLayerModule","internal_title":f"Event {i}",
        "internal_toggles":{"config_visible":10},
        "internal_formulas":{"config_visible":f'$if(ci(title, {i}) = "", REMOVE, ALWAYS)$'},
        "viewgroup_items":[
            shape(W,66,TILE,20),
            shape(6,38,"#FFFFFFFF",3,position_anchor="CENTERLEFT",position_offset_x=16.0,
                  internal_toggles={"paint_color":10},internal_formulas={"paint_color":f"$ci(ccolor, {i})$"}),
            stack([txt(f"$ci(title, {i})$",17,glob_font="bold",text_size_type="FIXED_WIDTH",text_width=float(W-60),text_lines=1),
                   txt(when(i),13,glob_color="headers",text_size_type="FIXED_WIDTH",text_width=float(W-60),text_lines=1)],
                  "VERTICAL_LEFT",2,position_anchor="CENTERLEFT",position_offset_x=36.0)]}
    return row
N=5
calendar = stack([
    txt('Upcoming', 16, glob_color="headers", glob_font="bold", position_padding_left=6.0),
    card(W,66,TILE, txt("No upcoming events",16), anchor="CENTER") | {
        "internal_toggles":{"config_visible":10},"internal_formulas":{"config_visible":'$if(ci(title, 0) = "", ALWAYS, REMOVE)$'}},
] + [event_row(i) for i in range(N)], "VERTICAL_LEFT", 8, internal_title="Calendar",
   internal_events=[{"type":"SINGLE_TAP","action":"LAUNCH_APP","intent":APP_CAL}])

root = stack([hero, chips, forecast, calendar], "VERTICAL_LEFT", 14,
             position_anchor="TOPLEFT", position_offset_x=10.0, position_offset_y=10.0, internal_title="HA Dashboard")
clip={"clip_version":1,"clip_cut":[],"clip_modules":[root]}
open(OUT+"ha-dashboard.kustomclip","w").write("##KUSTOMCLIP##\n"+json.dumps(clip,indent=2,ensure_ascii=False))
print("ok")
