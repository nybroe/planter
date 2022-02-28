import json
import time
import contract as c
from datetime import datetime
import time

garden_contract_addr = "0x685BFDd3C2937744c13d7De0821c83191E3027FF"
wallet_public_addr = "0x361472B5784e83fBF779b015f75ea0722741f304"
min_plant_amount = 3.00
loop_sleep_seconds = 5 # 60*60 # One hour
margin_of_error = 0.01
seeds_per_day_per_plant = 86400

# load private key
wallet_private_key = open('key.txt', "r").readline()

# load abi
f = open('garden_abi.json')
garden_abi = json.load(f)

# create contract
garden_contract = c.connect_to_contract(garden_contract_addr, garden_abi)

def seeds_for_1_plant():
    seedsFor1Plant = garden_contract.functions.SEEDS_TO_GROW_1PLANT().call()
    return seedsFor1Plant

def available_seeds():
    return garden_contract.functions.getUserSeeds(wallet_public_addr).call()

def planted_plants():
    return garden_contract.functions.hatcheryPlants(wallet_public_addr).call()

def plant():
    txn = garden_contract.functions.plantSeeds(wallet_public_addr).buildTransaction(c.get_tx_options(wallet_public_addr, 500000))
    return c.send_txn(txn, wallet_private_key)

def countdown(t):
    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(timer, end="\r")
        time.sleep(1)
        t -= 1

    
# create infinate loop that checks contract every set sleep time
while True:
    seedsFor1Plant = seeds_for_1_plant()
    available = available_seeds()
    plantedPlants = planted_plants()
    availablePlants = available / seedsFor1Plant

    plantsNeededForPlanting = (min_plant_amount + margin_of_error) - availablePlants
    seedsNeededForPlanting = plantsNeededForPlanting * seedsFor1Plant
    
    seedsPerDay = plantedPlants * seeds_per_day_per_plant
    daysUntilPlanting = seedsNeededForPlanting / seedsPerDay
    hoursUntilPlanting = daysUntilPlanting * 24 
    secondsUntilPlanting = hoursUntilPlanting * 60 * 60

    mins, secs = divmod(int(secondsUntilPlanting), 60)
    timer = '{:02d}:{:02d}'.format(mins, secs)

    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("[%d-%b-%Y (%H:%M:%S)]")
    
    print("********** STATS *******")
    print(f"{timestampStr} Seeds for 1 plant: {seedsFor1Plant:.2f}")
    print(f"{timestampStr} Seeds per day: {seedsPerDay:.2f}")
    print(f"{timestampStr} Planted plants: {plantedPlants:.2f}")
    print(f"{timestampStr} Available seeds: {available:.2f}")
    print(f"{timestampStr} Available plants: {availablePlants:.2f}")
    print(f"{timestampStr} Margin of error: {margin_of_error:.2f}")
    print(f"{timestampStr} Plants needed before planting: {plantsNeededForPlanting:.2f}")
    print(f"{timestampStr} Seeds needed before planting: {seedsNeededForPlanting:.2f}")
    print(f"{timestampStr} Seconds until next planting: {secondsUntilPlanting:.2f}")
    print(f"{timestampStr} Until next planting:")
    print(timer)
    print("************************")
    
    if availablePlants >= min_plant_amount and availablePlants < (min_plant_amount + margin_of_error):
        # plant()
        print(f"{timestampStr} Planted! {availablePlants:.2f} added to garden.")

    countdown(loop_sleep_seconds)
    
