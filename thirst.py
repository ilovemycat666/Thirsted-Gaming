from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import csv
import operator

Tournament_Matches = 4
Tournament_Start = 14
# Remember: Tournament will end 59 minutes after the hour you select below
Tournament_End = 17 #59

ids = []
# Opens CSV and makes the ids list above
with open('beta.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        ids.append((row[0], row[1], row[2]))
# Calculates Points, Placement Points and Kills
def points(kills, place):
    if kills == '':
        kills = 0
    else:
        kills = int(kills)
    place = int(place)
    placementPts = 0
    if place == 1:
        placementPts += 10
    elif place <= 5:
        placementPts += 5
    elif place <= 10:
        placementPts += 3
    elif place <=25:
        placementPts += 2
    points = placementPts + kills
    return points, placementPts, kills

opts = Options()
opts.headless = True

# The Main job
def do_work():
    # Declare some variables
    topFour = []
    proTier = []
    amsTier = []
    tracker = {}
    #Main for loop, each iteration is one gamer tag
    for id in ids:
        tried = False
        try:
            driver = webdriver.Firefox(options=opts)
            tried = True
            driver.implicitly_wait(10)
            wait = WebDriverWait(driver, 20)
            print(id)

            if id[0] == '' or id[1] == '' or id[2] == '':
                print(f"{id} Missing Contestant Name or Tier. Review spreadsheet.")
                continue
            new = id[0].split('#')
            if len(new[1]) == 7:
                url = 'https://cod.tracker.gg/warzone/profile/atvi/' + new[0] + '%23' + new[1] + '/overview'
            elif len(new[1]) == 5 or len(new[1]) == 4:
                url = 'https://cod.tracker.gg/warzone/profile/battlenet/' + new[0] + '%23' + new[1] + '/overview'
            else:
                print(f"No Such Id: {id}")
                continue
            driver.get(url)

            # List of games per gamer tag
            matchStats = []
            wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'match-row__link')))
            # grabs the markers for the date of a set of games
            gamesPlayedToday = driver.find_elements_by_class_name('session-header__metadata')
            # uses index 0 to grab the most current one, then splits off irrelevant data
            gamesPlayedToday = gamesPlayedToday[0].text.split('\n')
            tournyGames = 0
            if gamesPlayedToday[0] == "Today":
                match = -1
                sauce = BeautifulSoup(driver.page_source, 'html.parser')
                match_details = sauce.find_all(class_ = 'match-row__details')
                times = [title.find('span')['title'].split(" ")[4:-4] for title in match_details]
                times = [item[:-3] for sublist in times for item in sublist]
                for t in times[:int(gamesPlayedToday[1])]:
                    match += 1
                    if int(t[:2]) >= Tournament_Start and int(t[:2]) <= Tournament_End:
                        tournyGames += 1
                        driver.get(url)

                        matches = driver.find_elements_by_class_name('match-row__link')
                        matches[match].click()

                        wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'player__stats')))
                        sauce = BeautifulSoup(driver.page_source, 'html.parser')
                        playerStats = sauce.find(class_ = 'player__stats')
                        teamStats = playerStats.parent.parent.parent.get_text()
                        teamDetails = teamStats[:10].split(' ')
                        teamDetails = teamDetails[1:3]

                        pts = points(teamDetails[1], teamDetails[0][:-2])


                        matchStats.append({ "Kills" : pts[2],
                                            "Points" : pts[0],
                                            "Placement" : pts[1],
                                            })
        except TimeoutException as exception:
            print(f"No Such Id: {id}")
            print(exception)
            continue
        finally:
            if tried:
                print("quit driver")
                driver.quit()

        # Orders the team matches by Points value
        matchStats.sort(key=operator.itemgetter('Points'), reverse=True)
        kills = 0
        placement = 0
        pts = 0
        place = 0
        for con in matchStats[:Tournament_Matches]:
            kills += con['Kills']
            placement += con['Placement']
            pts += con['Points']

        topFour.append({'Tier' : id[1],
                        'Code' : id[2],
                        "Games" : tournyGames,
                        'Placement' : placement,
                        'Kills' : kills,
                        'Points' : pts,
                        })

    # Big ID for loop ends here.

    # Orders the team scores by Points value
    topFour.sort(key=operator.itemgetter('Points'), reverse=True)
    for top in topFour:
        if top['Tier'] == 'pros':
            proTier.append(top)
        else:
            amsTier.append(top)

    # Order the two leaderboards
    if proTier:
        place = 0
        proHigh = proTier[0]['Points']
        for pro in proTier:
            place += 1
            pro['Place'] = place
            ptsBehind = proHigh - pro['Points']
            if ptsBehind == 0:
                pro['Behind'] = "-"
            else:
                pro['Behind'] = ptsBehind


    if amsTier:
        place = 0
        amsHigh = amsTier[0]['Points']
        for ams in amsTier:
            place += 1
            ams['Place'] = place
            ptsBehind = amsHigh - ams['Points']
            if ptsBehind == 0:
                ams['Behind'] = "-"
            else:
                ams['Behind'] = ptsBehind
    return proTier, amsTier
