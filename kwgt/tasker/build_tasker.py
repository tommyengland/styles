"""Builds KWGT_Glance.prj.xml: a Tasker project with the Glance task and the two profiles that run it.
Structure copied from real Tasker exports (HTTP Request 339, If 37 / End If 38, the KWGT
"Kustom Variable" plugin action, Display Unlocked event 1000, Time context). Run: python3 build_tasker.py"""
import os
from xml.sax.saxutils import escape

URL = "https://barrellfamily.duckdns.org/api/states/sensor.kwgt_glance"
TOKEN = "PASTE_YOUR_HOME_ASSISTANT_TOKEN_HERE"
TS = "1794550000000"
TASK, P_UNLOCK, P_TIME = 7101, 7102, 7103


def kwgt_var(sr, name, value):
    b = lambda k, v, t="java.lang.String": f"<{k}>{escape(v)}</{k}>\n\t\t\t\t\t<{k}-type>{t}</{k}-type>"
    return f"""		<Action sr="{sr}" ve="7">
			<code>1186637727</code>
			<Bundle sr="arg0">
				<Vals sr="val">
					{b("com.twofortyfouram.locale.intent.extra.BLURB", "Set: " + name)}
					{b("net.dinglisch.android.tasker.extras.VARIABLE_REPLACE_KEYS", "org.kustom.tasker.VAR_NAME org.kustom.tasker.VAR_VALUE")}
					{b("net.dinglisch.android.tasker.subbundled", "true", "java.lang.Boolean")}
					{b("org.kustom.tasker.VAR_NAME", name)}
					{b("org.kustom.tasker.VAR_VALUE", value)}
					{b("org.kustom.tasker.extra.INT_VERSION_CODE", "376422110", "java.lang.Integer")}
				</Vals>
			</Bundle>
			<Str sr="arg1" ve="3">org.kustom.widget</Str>
			<Str sr="arg2" ve="3">org.kustom.lib.editor.tasker.EditVarActivity</Str>
			<Int sr="arg3" val="0"/>
			<Int sr="arg4" val="1"/>
		</Action>"""


xml = f"""<TaskerData sr="" dvi="1" tv="6.3.13">
	<Profile sr="prof{P_UNLOCK}" ve="2">
		<cdate>{TS}</cdate>
		<edate>{TS}</edate>
		<flags>8</flags>
		<id>{P_UNLOCK}</id>
		<mid0>{TASK}</mid0>
		<nme>KWGT Glance on unlock</nme>
		<Event sr="con0" ve="2">
			<code>1000</code>
		</Event>
	</Profile>
	<Profile sr="prof{P_TIME}" ve="2">
		<cdate>{TS}</cdate>
		<edate>{TS}</edate>
		<flags>8</flags>
		<id>{P_TIME}</id>
		<mid0>{TASK}</mid0>
		<nme>KWGT Glance every 15 min</nme>
		<Time sr="con0">
			<fh>0</fh>
			<fm>0</fm>
			<rep>2</rep>
			<repval>15</repval>
			<th>23</th>
			<tm>59</tm>
		</Time>
	</Profile>
	<Project sr="proj0" ve="2">
		<cdate>{TS}</cdate>
		<name>KWGT Glance</name>
		<pids>{P_UNLOCK},{P_TIME}</pids>
		<tids>{TASK}</tids>
	</Project>
	<Task sr="task{TASK}">
		<cdate>{TS}</cdate>
		<edate>{TS}</edate>
		<id>{TASK}</id>
		<nme>KWGT Glance</nme>
		<pri>6</pri>
		<Action sr="act0" ve="7">
			<code>339</code>
			<se>false</se>
			<Bundle sr="arg0">
				<Vals sr="val"/>
			</Bundle>
			<Int sr="arg1" val="0"/>
			<Int sr="arg10" val="1"/>
			<Int sr="arg11" val="1"/>
			<Int sr="arg12" val="1"/>
			<Str sr="arg2" ve="3">{escape(URL)}</Str>
			<Str sr="arg3" ve="3">Authorization:Bearer {escape(TOKEN)}</Str>
			<Str sr="arg4" ve="3"/>
			<Str sr="arg5" ve="3"/>
			<Str sr="arg6" ve="3"/>
			<Str sr="arg7" ve="3"/>
			<Int sr="arg8" val="15"/>
			<Int sr="arg9" val="0"/>
		</Action>
		<Action sr="act1" ve="7">
			<code>37</code>
			<ConditionList sr="if">
				<Condition sr="c0" ve="3">
					<lhs>%http_response_code</lhs>
					<op>0</op>
					<rhs>200</rhs>
				</Condition>
			</ConditionList>
		</Action>
{kwgt_var("act2", "glance_bins", "%http_data.attributes.bins")}
{kwgt_var("act3", "glance_alerts", "%http_data.attributes.alerts")}
		<Action sr="act4" ve="7">
			<code>38</code>
		</Action>
	</Task>
</TaskerData>
"""
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "KWGT_Glance.prj.xml")
open(out, "w").write(xml)
print("wrote", out)
