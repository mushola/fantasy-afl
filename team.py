from pulp import *
import datetime
import pandas as pd

now = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()


############## MODEL OPTIONS ############

# use the following option variables to tweak selections

player_include = []  # must be id int, overrides status_exclude
player_exclude = []  # must be id int
status_exclude = [] # is overridden by player_include

curr_round = 9 # TODO determine current round from data import


############## MODEL VARIABLES ##########

PROB_STR = "best_fantasy_team"
BUDGET = 21719000
SQUAD_COUNT = 30
EMG_COUNT = 4
ROLES = ['field', 'bench']
POSITIONS = {"DEF": {'field': 6, 'bench': 2},
             "MID": {'field': 8, 'bench': 2},
             "RUC": {'field': 2, 'bench': 1},
             "FWD": {'field': 6, 'bench': 2},
             "UTL": {'field': 0, 'bench': 1}
}
ROLE_WEIGHT = {'field': 1, 'bench': 0.5}


############## IMPORT DATA ##############

players = pd.read_json('data\\players.json').set_index('id')
squads = pd.read_json('data\\squads.json').set_index('id')
with open('data\\team.json') as f:
    team = json.load(f)['success']['team']
    
current_team = set()
for pos, ps in team['lineup'].items():
    current_team.update(ps)
for pos, ps in team['bench'].items():
    current_team.update(ps)
current_team.add(team['utilityId'])


# combination matrices for improved readability (eg ODP)
SLOTS = [(pos, role, i) for pos in POSITIONS for role in ROLES for i in range(POSITIONS[pos][role])]
SLOT_IDS = list(range(len(SLOTS)))
PS = [(player, ids) for player in players.index for ids in SLOT_IDS]


############## PROBLEM ##################

prob = LpProblem(PROB_STR, LpMaximize)


############## DECISION VARIABLES #######

x = LpVariable.dicts('inSquad',
                     players.index,
                     0, 1, LpBinary)
ti = LpVariable.dicts('tradeIn',
                     players.index,
                     0, 1, LpBinary)
to = LpVariable.dicts('tradeOut',
                     players.index,
                     0, 1, LpBinary)
y = LpVariable.dicts('assign',
                     (players.index, SLOT_IDS),
                     0, 1, LpBinary)

############## OBJECTIVE FUNCTION #######

prob += lpSum(players.loc[p, 'averagePoints'] * (
    1 if SLOTS[s][1] == "field" else 0.75 if SLOTS[s][0] != "UTL" else 0
    ) * y[p][s] for p in players.index for s in SLOT_IDS
)

############## CONSTRAINTS ##############

# squad size
# prob += lpSum(in_squad[p] for p in players.index) == 30

# trades
prob += lpSum(ti[p] for p in players.index if p not in current_team) <= 2
prob += lpSum(to[p] for p in current_team) <= 2
prob += lpSum(ti[p] for p in players.index) == lpSum(to[p] for p in players.index)

# link trades to squad
for p in players.index:
    if p in current_team:
        # can only trade out if currently owned
        prob += to[p] <= 1
        prob += ti[p] == 0
        prob += x[p] == 1 - to[p]

    else:
        # can only trade in if not owned
        prob += to[p] == 0
        prob += x[p] == ti[p]

# budget constraint
prob += (
    lpSum(players.loc[p, 'price'] * ti[p] for p in players.index)
    <=
    lpSum(players.loc[p, 'price'] * to[p] for p in players.index)
    + team['budget']
)

# fill each slot
for s in SLOT_IDS:
    prob += lpSum(y[p][s] for p in players.index) == 1

# players only used once
for p in players.index:
    prob += lpSum(y[p][s] for s in SLOT_IDS) <= 1

# only assign players in squad
for p in players.index:
    for s in SLOT_IDS:
        prob += y[p][s] <= x[p]

# position constraints
for p in players.index:
    player_pos = players.loc[p, 'position']
    for s in SLOT_IDS:
        pos, role, _ = SLOTS[s]
        if pos != "UTL" and pos not in player_pos:
            prob += y[p][s] == 0


############## SOLVE ####################

prob.writeLP(PROB_STR)
prob.solve()

############## PRINT RESULTS ############


total_cost = 0
player_count = 0
pos_count = {(pos, role): 0 for pos in POSITIONS for role in ROLES}
new_team = {slot: 0 for slot in SLOTS}
trades = {'in': [], 'out': []}

for p in players.index:
    if ti[p].varValue == 1:
        trades['in'].append(p)
    if to[p].varValue == 1:
        trades['out'].append(p)
    for s in SLOT_IDS:
        if y[p][s].varValue == 1:
            new_team[SLOTS[s]] = p
            pos, role, _ = SLOTS[s]
            total_cost += players.loc[p,'price']
            player_count += 1
            pos_count[(pos, role)] += 1

    
for slot, p in new_team.items():
    pos, role, _ = slot
    print(f"{players.loc[p,'firstName'][0]} {players.loc[p,'lastName']}".ljust(15),
            pos, role,
            squads.loc[players.loc[p,'squadId'], 'abbreviation'].rjust(4),
            str(players.loc[p,'averagePoints']).rjust(6),
            str(players.loc[p,'price']).rjust(8),
            ti[p].varValue
        )
print(f"player count: {player_count}")
print()
print("trade out:")
for p in trades['out']:
    print(f"{players.loc[p,'firstName'][0]} {players.loc[p,'lastName']}".ljust(15),
            squads.loc[players.loc[p,'squadId'], 'abbreviation'].rjust(4),
            str(players.loc[p,'averagePoints']).rjust(6),
            str(players.loc[p,'price']).rjust(8),
            players.loc[p,'position']
    )
print()
print("trade in:")
for p in trades['in']:
    print(f"{players.loc[p,'firstName'][0]} {players.loc[p,'lastName']}".ljust(15),
            squads.loc[players.loc[p,'squadId'], 'abbreviation'].rjust(4),
            str(players.loc[p,'averagePoints']).rjust(6),
            str(players.loc[p,'price']).rjust(8),
            players.loc[p,'position']
    )
    

print()
print(f"total cost: {total_cost}")
print()
print("Status:", LpStatus[prob.status])
print("Objective:", "{:.2f}".format(pulp.value(prob.objective)))
print()