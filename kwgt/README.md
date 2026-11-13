# KWGT home widget: Misty Forest

`misty-forest.kustomclip` is a phone version of the Home Kiosk dashboard (`main.dash`, Misty Forest v2).
Copy the whole file, including the `##KUSTOMCLIP##` line, then long-press inside a preset in the KWGT editor and choose **Paste**.

- **One calm surface**: `#EEF2F2` by day and `#18212A` by night. It switches at the same times as `page_theme: mistforest`: night runs from 30 minutes after sunset until sunrise.
- **Banner**: the only box with its own panel. Its colour follows the weather and the sun, with a warm glow around sunrise and sunset. It shows the date (17) with the day under it, the time, and a bar that fills each minute. On the right are now, wind (compass, mph and the Beaufort name, as in `sensor.dashboard_wind_status`) and the next sunrise or sunset. Along the bottom are the next 6 hours.
- **What's on** (lake): an open section with a small tick before the title. Today is shown big: an event on now has the accent mixed into its fill and shows "Now · until …", and the next one has a countdown. Below that, "Coming up" lists later days in a smaller size.

Taps open Clock (time), Weawow (weather) and OneCalendar (What's on).

The colours are at the top of `generate.py` as (day, night) pairs. They're approximations, because
`themes/mistforest_theme.py` wasn't available. Paste the real `FAMILIES` / `tokens()` values in, then run `python3 generate.py`.
