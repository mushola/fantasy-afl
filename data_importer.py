import time


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


#https://fantasy.afl.com.au/json/fantasy/players.json
#https://fantasy.afl.com.au/json/fantasy/squads.json
#https://fantasy.afl.com.au/json/fantasy/rounds.json
#https://fantasy.afl.com.au/json/fantasy/players_game_stats/2026.json




browser = webdriver.Firefox()
browser.maximize_window()
browser.get("https://fantasy.afl.com.au/classic/team")
time.sleep(10)
#username = browser.find_element(By.ID, "input27")
username = browser.find_element(By.NAME, "identifier")
username.text = "test"
