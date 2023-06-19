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


#############################################
######   Balance and mint
#############################################

if chain == "ethereum" :
    url = "https://eth-mainnet.g.alchemy.com/v2/" + API_KEY

if chain == "polygon" :
    url = "https://polygon-mainnet.g.alchemy.com/v2/" + API_KEY

#contractAddress = inputData[num][1]
#tokenName = inputData[num][2]
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
nullAddress = "0x0000000000000000000000000000000000000000"

while (True):
    # APIからのデータ取得
    response = requests.post(url, json=payload, headers=headers)
    jsonFile = response.json()

    for i in range( len(jsonFile["result"]["transfers"]) ):
        # 残高
        if jsonFile["result"]["transfers"][i]["to"] not in balance:
            balance[jsonFile["result"]["transfers"][i]["to"]] = 0
                
        if jsonFile["result"]["transfers"][i]["from"] not in balance:
            balance[jsonFile["result"]["transfers"][i]["from"]] = 0   

        balance[ jsonFile["result"]["transfers"][i]["to"] ] += 1
        balance[ jsonFile["result"]["transfers"][i]["from"] ] -= 1

        # 新しいトークンの発行
        if jsonFile["result"]["transfers"][i]["from"] == nullAddress :
            if jsonFile["result"]["transfers"][i]["to"] not in mint:
                mint[jsonFile["result"]["transfers"][i]["to"]] = 0
                    
            mint[ jsonFile["result"]["transfers"][i]["to"] ] += 1

    # 次ページがある場合、データ取得に使用するパラメータを更新
    if 'pageKey' in jsonFile["result"]:
        payload["params"][0]["pageKey"] = jsonFile["result"]["pageKey"]
        print("Data Num = " + str(len(jsonFile["result"]["transfers"])) + " pageKey = " + jsonFile["result"]["pageKey"])
    else:
        # ページングが終了したときループを抜ける
        print("Data Num = " + str(len(jsonFile["result"]["transfers"])) )
        break


del balance[nullAddress]
for key in list(balance.keys()):
    if balance[key] == 0:
        del balance[key]


with open( "data/" + tokenName + "_" + str(config_data["params"]["toBlock"]) + '_balance.json', 'w') as f:
    json.dump(balance, f, ensure_ascii=False)
with open( "data/" + tokenName + "_" + str(config_data["params"]["toBlock"]) + '_mint.json', 'w') as f:
    json.dump(mint, f, ensure_ascii=False)

