# KWGT home widget: Misty Forest

`misty-forest.kustomclip` is a phone version of the Home Kiosk dashboard (`main.dash`, Misty Forest v2).
Copy the whole file, including the `##KUSTOMCLIP##` line, then long-press inside a preset in the KWGT editor and choose **Paste**.

- **One calm surface**: `#EEF2F2` by day and `#18212A` by night. It switches at the same times as `page_theme: mistforest`: night runs from 30 minutes after sunset until sunrise.
- **Banner**: the only box with its own panel. Its colour follows the weather and the sun, with a warm glow around sunrise and sunset. It shows the date (17) with the day under it, the time, and a bar that fills each minute. On the right are now, wind (compass, mph and the Beaufort name, as in `sensor.dashboard_wind_status`) and the next sunrise or sunset. Along the bottom are the next 6 hours.
- **What's on** (lake): one list of your upcoming events, 5 at a time, each labelled Today, Tomorrow or its date. An event on now has the accent mixed into its fill and shows "Now · until …", and the next one today has a countdown. A widget can't scroll, so when there are more than 5 events, the header shows "1–5 of 12" with **▲ ▼** to page through them (up to 20). The page is held in the `calpage` global.

Taps open your default clock app (time), your kiosk's Weather page (weather) and your default calendar app (What's on). To use a different app, select the item in KWGT, go to its **Touch** tab and pick **Launch app**.

The colours are at the top of `generate.py` as (day, night) pairs. They're approximations, because
`themes/mistforest_theme.py` wasn't available. Paste the real `FAMILIES` / `tokens()` values in, then run `python3 generate.py`.
