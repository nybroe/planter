import json
import time
import contract as c
from datetime import datetime
import time

garden_contract_addr = "0x685BFDd3C2937744c13d7De0821c83191E3027FF"
wallet_public_addr = "0x361472B5784e83fBF779b015f75ea0722741f304"
min_plant_amount = 10
loop_sleep_seconds = 5 # 60*60 # One hour

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

def plant():
    txn = garden_contract.functions.roll().buildTransaction(c.get_tx_options(wallet_public_addr, 500000))
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
    available_plants = available / seedsFor1Plant

    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("[%d-%b-%Y (%H:%M:%S)]")
    
    if available_plants > min_plant_amount and available >= seedsFor1Plant:
        # plant()
       
        print(f"{timestampStr} Planted! {available_plants:.3f} added to garden.")
        #print(f"{timestampStr} Total value of your deposit is now ${total_value:,.2f}")
    else:
        if available_plants < min_plant_amount:
            print(f"{timestampStr} Only {available:.3f} seeds is available for the minimum required amount: {(min_plant_amount * seedsFor1Plant):.3f}. Sleeps..")
        else:
            print(f"{timestampStr} Planting not ready {available:.3f} seeds available. Need {((min_plant_amount * seedsFor1Plant) - available):.3f} more")

    countdown(loop_sleep_seconds)
    
