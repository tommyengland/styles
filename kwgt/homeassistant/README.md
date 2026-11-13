# Home Assistant → phone widget (via Tasker)

The widget shows two things from Home Assistant:

- **Bins tomorrow:** a line under the time in the banner, like "Bins tomorrow: **Recycling + Garden**".
- **Alerts:** a row under the banner that appears only when something needs attention. It uses the kiosk's colours:
  ember for an open door or the alarm going off, and amber for the alarm arming, Met Office warnings and batteries at 20% or below.

Home Assistant works these out in one sensor, `sensor.kwgt_glance`. Tasker reads that sensor when the screen comes on and
every 15 minutes, then passes the values to KWGT.

## 1. Home Assistant

1. Copy `kwgt_glance.yaml` to `/config/packages/kwgt_glance.yaml`. Your config already loads that folder.
2. **Developer tools → YAML → Template entities** (reload). If the sensor doesn't appear, restart Home Assistant.
3. **Developer tools → States** → `sensor.kwgt_glance`. It should have `bins` and `alerts` attributes, which are empty when all's well.
4. Make a token for Tasker: click your profile (bottom left) → **Security** → **Long-lived access tokens** →
   **Create token**, and name it "Tasker". Copy it now, because Home Assistant shows it only once. Don't paste it anywhere but Tasker.

## 2. Tasker

### Quick way: import the project

1. Download `../tasker/KWGT_Glance.prj.xml` to the phone.
2. In Tasker, long-press the **home icon / project tabs** along the bottom → **Import Project** → pick the file.
   It adds a **KWGT Glance** project with the task and both profiles.
3. Open the **KWGT Glance** task → **HTTP Request** → **Headers**. Replace `PASTE_YOUR_HOME_ASSISTANT_TOKEN_HERE` with your token, keeping `Authorization:Bearer ` in front of it.
4. Tap ▶ to test. Tasker may ask you to allow KWGT as a plugin; say yes.

### By hand (if the import doesn't work)


**Task** "Glance" (Tasks tab → +):

1. **Net → HTTP Request**
   - Method: `GET`
   - URL: `https://barrellfamily.duckdns.org/api/states/sensor.kwgt_glance`
   - Headers: `Authorization:Bearer YOUR_TOKEN`
   - Timeout: `10`
   - Tick **Continue Task After Error**, so no signal doesn't stop the task.
2. **Task → If** `%http_response_code` *Maths: Equals* `200`
3. **Plugin → KWGT** (the action may be called *Kustom Variable* or *Send Variable*). Tap the pencil to set:
   - Variable name: `glance_bins`
   - Value: `%http_data.attributes.bins`
4. **Plugin → KWGT** again:
   - Variable name: `glance_alerts`
   - Value: `%http_data.attributes.alerts`
5. **Task → End If**

Tap ▶ to test it. The widget should update within a few seconds.

**Profiles** (Profiles tab → +). Link both to the Glance task:

- **Event → Display → Display Unlocked**, so the widget is fresh whenever you unlock your phone.
- **Time** → From `00:00` To `23:59`, Repeat **Every 15 minutes**, so it also updates while the phone sits unlocked.

## Notes

- If Tasker can't reach Home Assistant, the widget keeps showing the last values it got.
- An empty value from Home Assistant can reach KWGT as the literal text `%http_data…`. The widget treats that as empty.
- To change what counts as an alert, edit the `alerts` template. Each alert is one `[c=#colour]…[/c]` piece, joined with " · ".
