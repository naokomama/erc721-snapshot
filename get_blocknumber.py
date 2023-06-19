import os
import time
import datetime
import json
from web3 import Web3
from web3.middleware import geth_poa_middleware


#API_KEYにinfulaのAPIを入力してください。
#「.env」ファイルを使う場合は、「.env_sample」を「.env」にリネームしてください。

from dotenv import load_dotenv
load_dotenv()
API_KEY =  os.getenv("INFURA_API")



with open('config.json') as f:
    config_data = json.load(f)


chain = config_data["chain"]
if chain == "ethereum":
    infura_url = "https://mainnet.infura.io/v3/" + API_KEY
    chainId = 1
elif chain == "polygon":
    infura_url = "https://polygon-mainnet.infura.io/v3/" + API_KEY
    chainId = 137


#PCのローカルタイムゾーンを入力
targetYear = config_data["time"]["year"]
targetMonth = config_data["time"]["month"]
targetDay = config_data["time"]["day"]
targetHour = config_data["time"]["hour"]
targetMinute = config_data["time"]["minute"]

targetTime =  datetime.datetime(targetYear, targetMonth, targetDay, targetHour, targetMinute)
targetTimeUnix = int(time.mktime(targetTime.timetuple()))
print("targetTime is " + str(targetTimeUnix))

web3 = Web3(Web3.HTTPProvider(infura_url))
web3.middleware_onion.inject(geth_poa_middleware, layer=0)


blockNum = web3.eth.block_number-10
blockInfo = web3.eth.get_block(blockNum)
blockTime = blockInfo.timestamp


blockNum1 = web3.eth.block_number
answer = 0


#ニュートン法でターゲットタイムに最も近いブロックを探索

while True:

    blockNum2 = blockNum1 - 10

    blockTime1 = web3.eth.get_block(blockNum1).timestamp
    blockTime2 = web3.eth.get_block(blockNum2).timestamp

    blockGradient = (blockTime1 - blockTime2 ) / (blockNum1 - blockNum2)
    #print("blockGradient " + str(blockGradient))

    nextBlock = int(blockNum1) + int( (int((targetTimeUnix)) - int(blockTime1)) / int(blockGradient) )
    nextTime =  web3.eth.get_block(nextBlock).timestamp

    print("--- Next Block " + str(nextBlock) + " --- Next Time " + str(datetime.datetime.fromtimestamp(nextTime)) )

    if abs(nextTime - blockTime1) < 20:
        answer1 = nextBlock - 1
        answer2 = nextBlock 
        answer3 = nextBlock + 1
        timeAnswer1 = web3.eth.get_block(answer1).timestamp
        timeAnswer2 = web3.eth.get_block(answer2).timestamp
        timeAnswer3 = web3.eth.get_block(answer3).timestamp

        if targetTimeUnix < timeAnswer1:
            answer = answer1
            timeAnswer = timeAnswer1
        elif targetTimeUnix < timeAnswer2:
            answer = answer2
            timeAnswer = timeAnswer2
        else:
            answer = answer3
            timeAnswer = timeAnswer3

        break

    blockNum1 = nextBlock

print("Answer is " + str(answer) + " : Time is " + str(datetime.datetime.fromtimestamp(timeAnswer)) )
