import os
import requests
import json

from dotenv import load_dotenv
load_dotenv()
API_KEY =  os.getenv("ALCHEMY_API")

with open('config.json') as f:
    config_data = json.load(f)

chain = config_data["chain"]
toBlock = hex(config_data["params"]["toBlock"])
contractAddress = config_data["params"]["contractAddresses"]
tokenName = config_data["params"]["symbol"]

if chain == "ethereum" :
    url = "https://eth-mainnet.g.alchemy.com/v2/" + API_KEY

if chain == "polygon" :
    url = "https://polygon-mainnet.g.alchemy.com/v2/" + API_KEY

tokenStandard = "erc721"

payload = {
    "id": 1,
    "jsonrpc": "2.0",
    "method": "alchemy_getAssetTransfers",
    "params": [
        {
            "fromBlock": "0x0",
            "toBlock": toBlock,
            "contractAddresses": [contractAddress],
            "category": [tokenStandard],
            "withMetadata": False,
            "excludeZeroValue": True,
            "maxCount": "0x3e8"
        }
    ]
}

headers = {
    "accept": "application/json",
    "content-type": "application/json"
}

balance={}
mint={}
tokenIds={} # New dictionary for storing token Ids
nullAddress = "0x0000000000000000000000000000000000000000"

while (True):
    response = requests.post(url, json=payload, headers=headers)
    jsonFile = response.json()

    for i in range(len(jsonFile["result"]["transfers"])):
        toAddress = jsonFile["result"]["transfers"][i]["to"]
        fromAddress = jsonFile["result"]["transfers"][i]["from"]
        tokenId = int(jsonFile["result"]["transfers"][i]["tokenId"], 16)  # Get token ID

        # For balance calculation
        if toAddress not in balance:
            balance[toAddress] = 0
        if fromAddress not in balance:
            balance[fromAddress] = 0   
        balance[toAddress] += 1
        balance[fromAddress] -= 1

        # For mint calculation
        if fromAddress == nullAddress :
            if toAddress not in mint:
                mint[toAddress] = 0
            mint[toAddress] += 1
        
        # For token Ids
        if toAddress not in tokenIds:
            tokenIds[toAddress] = []
        if fromAddress not in tokenIds:
            tokenIds[fromAddress] = []
        tokenIds[toAddress].append(tokenId)
        tokenIds[fromAddress].remove(tokenId) if tokenId in tokenIds[fromAddress] else None

    if 'pageKey' in jsonFile["result"]:
        payload["params"][0]["pageKey"] = jsonFile["result"]["pageKey"]
        print("Data Num = " + str(len(jsonFile["result"]["transfers"])) + " pageKey = " + jsonFile["result"]["pageKey"])
    else:
        print("Data Num = " + str(len(jsonFile["result"]["transfers"])))
        break

del balance[nullAddress]
if nullAddress in tokenIds:
    del tokenIds[nullAddress]

for key in list(balance.keys()):
    if balance[key] == 0:
        del balance[key]
        if key in tokenIds:
            del tokenIds[key]

with open( "data/" + tokenName + "_" + str(config_data["params"]["toBlock"]) + '_balance.json', 'w') as f:
    json.dump(balance, f, ensure_ascii=False)
with open( "data/" + tokenName + "_" + str(config_data["params"]["toBlock"]) + '_mint.json', 'w') as f:
    json.dump(mint, f, ensure_ascii=False)
with open( "data/" + tokenName + "_" + str(config_data["params"]["toBlock"]) + '_tokenIds.json', 'w') as f:  # Save tokenIds dictionary
    json.dump(tokenIds, f, ensure_ascii=False)
