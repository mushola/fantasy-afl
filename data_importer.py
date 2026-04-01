import os, sys, requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fantasy_creds import *

data_urls = ["https://fantasy.afl.com.au/json/fantasy/players.json",
             "https://fantasy.afl.com.au/json/fantasy/squads.json",
             "https://fantasy.afl.com.au/json/fantasy/rounds.json",
             "https://fantasy.afl.com.au/json/fantasy/players_game_stats/2026.json"
             ]


def download_data(url, data_folder):
    filename = url.split("/")[-1]
    save_path = os.path.join(data_folder, filename)
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f'{filename} downloaded successfully')
    else:
        print(f'Failed to download {filename}')


driver = webdriver.Firefox()
driver.get("https://fantasy.afl.com.au/classic/team")


try:
    username = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "input27"))
    )
    username.send_keys(uname)
    username.send_keys(Keys.RETURN)
    password = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "input63"))
    )
    password.send_keys(pword)
    password.send_keys(Keys.RETURN)
except:
    print("log in failed")
    sys.exit(1)

for url in data_urls:
    download_data(url, "data")
    
driver.quit()
