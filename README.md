# Fantasy AFL Team Selector

A team selector for the AFL fantasy competition. Uses the PuLP linear programming library to model team selection - suggesting trades and positioning plays within your team. Uses Selenium to download player, season and team data directly from the fantasy website.

---

### Setting up

After cloning the repo, install required libs with:
```bash
pip install -r requirements.txt
```
or
```bash
py -m pip install -r requirements.txt
```

In the root of the directory, create a file called fantasy_creds.py with your afl fantasy website credentials in it, like so:
```python
uname = "<username>"
pword = "<password>"
```

### Updating data

The file data_importer.py should be run to pull the latest team and player data from the website. It is suggested to run this once teams are announced, but definitely before the trade lock out begins once the round starts (otherwise you won't be able to make any trades!).

Sometimes the team.json data might fail. If so, try running the script again.

### Running the model

The main LP model solver script is in the team.py file. Using your currently owned players, the model suggest up to two trades to make and, assuming these are made, suggests the optimal player positions. The objective function of the model considers player status, player positions, field vs bench roles, the utility position, and uses this in conjunction with a player's average score per game to determine the optimal team make up. Future updates will include additional scoring options/metrics.

There are option variables that can be tweaked towards the top of this file before running. Options currently available are:
player_trade_include - use to force a trade in or out of specified player/s. (Max of 2 in or out)
player_trade_exclude - use to ignore both owned and potential players from trade consideration.
role_weight - weights used by model for roles
status_weight - weights used by model for statuses

Optimal team and trades will be solved for by the LP solver, and printed to console.
