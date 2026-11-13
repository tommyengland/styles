# KWGT home widget: Home Assistant-style redesign

`ha-dashboard.kustomclip` is a KWGT clip. Copy the whole file, including the
`##KUSTOMCLIP##` line, then long-press inside your preset in the KWGT editor and choose **Paste**.

Layout, from top to bottom, in the style of Mushroom cards:

1. **Hero card**: the clock, weekday and date on the left. On the right are the current weather icon (it still switches to sunrise/sunset in the 30 minutes around each), the temperature colour-coded by value, the conditions and the location.
2. **Chips**: wind speed and compass direction, humidity, and the next sunrise or sunset.
3. **Forecast**: four tiles for +1h to +4h, each with the hour, an icon and the temperature.
4. **Upcoming**: up to 5 calendar events as entity rows. Each row has a bar in the calendar's colour, the title, and "Today / Tomorrow / Ddd dd MMM · time". A row with no event is removed.

The clip reuses your existing globals `txt`, `headers`, `lead txt` and `bold`. Card colours are near the top
of `generate.py` (`CARD`, `TILE`, `ACCENT`). Edit them and run `python3 generate.py` to rebuild the clip.
