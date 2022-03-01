import json
import time
import contract as c
from datetime import datetime,timedelta
import time

garden_contract_addr = "0x685BFDd3C2937744c13d7De0821c83191E3027FF"
wallet_public_addr = "0x361472B5784e83fBF779b015f75ea0722741f304"
min_plant_amount = 1.00
loop_sleep_seconds = 5
margin_of_error = 0.005
seeds_per_day_per_plant = 86400
start_polling_threshold_in_seconds = 60*2

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

def buildTimer(t):
    mins, secs = divmod(int(t), 60)
    hours, mins = divmod(int(mins), 60)
    timer = '{:02d} hours, {:02d} minutes, {:02d} seconds'.format(hours, mins, secs)
    return timer

def getNextPlantingDate(t):
    mins, secs = divmod(int(t), 60)
    hours, mins = divmod(int(mins), 60)
    nextPlantAt = datetime.today() + timedelta(hours=hours,minutes=mins,seconds=secs)
    timestampStr = nextPlantAt.strftime("[%d-%b-%Y (%H:%M:%S)]")
    return timestampStr

def countdown(t):
    while t:
        print(f"Next poll in: {buildTimer(t)}", end="\r")
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

    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("[%d-%b-%Y (%H:%M:%S)]")

    sleep = loop_sleep_seconds
    
    print("********** STATS *******")
    print(f"{timestampStr} Planted plants: {plantedPlants:.3f}")
    print(f"{timestampStr} Available plants: {availablePlants:.3f}")
    print(f"{timestampStr} Margin of error: {margin_of_error:.3f}")
    print(f"{timestampStr} Minimum plants to plant: {min_plant_amount:.3f}")
    print(f"{timestampStr} Plants needed before planting: {plantsNeededForPlanting:.3f}")
    print(f"{timestampStr} Until next planting: {buildTimer(secondsUntilPlanting)}")
    print(f"{timestampStr} Next planting at: {getNextPlantingDate(secondsUntilPlanting)}")
    print(f"{timestampStr} Start polling each {(loop_sleep_seconds / 60)} minute {(start_polling_threshold_in_seconds / 60):.0f} minutes before next planting")
    print("************************")

    if secondsUntilPlanting > start_polling_threshold_in_seconds:
        sleep = secondsUntilPlanting - start_polling_threshold_in_seconds
            
    if availablePlants >= min_plant_amount and availablePlants < (min_plant_amount + margin_of_error):
        plant()
        print("********** PLANTED *******")
        print(f"Added {availablePlants:.2f} plants to the garden!")
        print("**************************")

    countdown(int(sleep))
    
