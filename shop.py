import requests
import json
from jinja2 import Template
from thirsty import *
import time
import datetime
import schedule



# key = "a00c785f84b202653daca7bbc6907980"
# password = "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"
# shop_url = "tournament-results.myshopify.com/admin/api/"
key = "cda1593aaa2e1739929498138f55bbed"
password = "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"
shop_url = "thirsted-gaming.myshopify.com/admin/api/"
api_version = '2021-04'

def get_time():
    now = datetime.datetime.now() + datetime.timedelta(hours=5)
    now = str(now)
    now = now.split('.')
    now = now[0]
    now = now.split(' ')
    return now


def update_page():
    tiers = do_work()
    proTier = tiers[0]
    amsTier = tiers[1]
    now = get_time()
    payload = {
        "page": {
        "id": 80691495070,
        "title" : "Results",
        "body_html": f"{template.render(proTier=proTier, amsTier=amsTier, now=now)}"
        }
    }
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    # r = requests.put(f"https://{key}:{password}@{shop_url}{api_version}/pages/80691495070.json", headers=headers, json=payload)
    r = requests.put(f"https://{key}:{password}@{shop_url}{api_version}/pages/67886022819.json", headers=headers, json=payload)


template = Template('''
<style>
table, th, td{
  margin-left:auto;
  margin-right:auto;
  width:100%;
}
button {
  float:right;
  color:black;
}
</style>
<button id="button" onclick="myFunction()">Beginner</button>
<p>Last Updated:</p>
<button onClick="document.location.reload(true)">Reload Page</button>
<b>Date:</b> {{ now[0] }}<br>
<b>Time:</b> {{ now[1] }}<br>
<!--<small>Next Update in Approximately 5min</small>-->

<script>
function myFunction() {
  var pro = document.getElementById("pros");
  var ams = document.getElementById("ams");
  var butt = document.getElementById("button");


  if (pro.style.display === "none") {
    pro.style.display = "inline";
    butt.innerHTML = "Beginner";
    ams.style.display = "none";
  } else {
    pro.style.display = "none";
    butt.innerHTML = "Amateur";
    ams.style.display = "inline";
  }
}
</script>


<table id="pros" style="display:inline;">
<caption><h1>Amateur</h1></caption>
  <tr>
    <th>Team</th>
    <th>Place</th>
    <th>Games Played</th>
    <th>Placement Points</th>
    <th>Kills</th>
    <th>Total Points</th>
    <th>Points Behind Leader</th>
  </tr>
  {% for pro in proTier %}
  <tr>
    <td>{{ pro['Code'] }}</td>
    <td>{{ pro['Place'] }}</td>
    <td>{{ pro['Games'] }}</td>
    <td>{{ pro['Placement'] }}</td>
    <td>{{ pro['Kills'] }}</td>
    <td>{{ pro['Points'] }}</td>
    <td>{{ pro['Behind'] }}</td>
  </tr>
  {% endfor %}
</table>

<table id="ams" style="display:none;">
<caption><h1>Beginner</h1></caption>
  <tr>
    <th>Team</th>
    <th>Place</th>
    <th>Games Played</th>
    <th>Placement Points</th>
    <th>Kills</th>
    <th>Total Points</th>
    <th>Points Behind Leader</th>
  </tr>
  {% for ams in amsTier %}
  <tr>
    <td>{{ ams['Code'] }}</td>
    <td>{{ ams['Place'] }}</td>
    <td>{{ ams['Games'] }}</td>
    <td>{{ ams['Placement'] }}</td>
    <td>{{ ams['Kills'] }}</td>
    <td>{{ ams['Points'] }}</td>
    <td>{{ ams['Behind'] }}</td>
  </tr>
  {% endfor %}
</table>
''')



def job():
    try:
        while True:
            update_page()
            print('updated page')
            time.sleep(10)
            now = get_time()
    except KeyboardInterrupt:
        print("Process Ended Successfully")

# job()
schedule.every().thursday.at("18:44").do(job)

while True:
	schedule.run_pending()
	time.sleep(59) # wait one minute!
