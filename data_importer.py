import os, sys, requests
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import fantasy_creds


data_folder = 'data'
data_urls = {'players.json':      "https://fantasy.afl.com.au/json/fantasy/players.json",
             'squads.json':       "https://fantasy.afl.com.au/json/fantasy/squads.json",
             'rounds.json':       "https://fantasy.afl.com.au/json/fantasy/rounds.json",
             'player_stats.json': "https://fantasy.afl.com.au/json/fantasy/players_game_stats/2026.json",
             'team.json':         "https://fantasy.afl.com.au/api/en/fantasy/team/show" # requires cookies
             }



driver = webdriver.Firefox()
driver.get("https://fantasy.afl.com.au/classic/team")

# log in
try:
    username = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "input27"))
    )
    username.send_keys(fantasy_creds.uname)
    username.send_keys(Keys.RETURN)
    password = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "input63"))
    )
    password.send_keys(fantasy_creds.pword)
    password.send_keys(Keys.RETURN)
except:
    print("log in failed")
    sys.exit(1)


def download_data(filename, url, attempts=5):
    cookies_dict = {cookie['name']: cookie['value'] for cookie in driver.get_cookies()}
    response = requests.get(url, cookies=cookies_dict)
    if response.status_code == 200:
        with open(os.path.join(data_folder, filename), 'wb') as file:
            file.write(response.content)
        print(f"{filename} downloaded successfully")
    elif attempts > 0:
        print(f"Failed to download {filename}... {attempts} attempt/s remaining...")
        sleep(0.5)
        download_data(filename, url, attempts-1)
    else:
        print(f"Failed to download {filename}")

for filename, url in data_urls.items():
    # update cookies dict
    cookies_dict = {cookie['name']: cookie['value'] for cookie in driver.get_cookies()}
    download_data(filename, url)


driver.quit()
