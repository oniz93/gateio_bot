from __future__ import print_function
import time
import gate_api
import os
from gate_api.exceptions import ApiException, GateApiException
from twilio.rest import Client as TwilioClient
import ujson as json
from datetime import datetime
from multiprocessing import Process

def checkCoins():
    # Defining the host is optional and defaults to https://api.gateio.ws/api/v4
    # See configuration.py for a list of all supported configuration parameters.
    configuration = gate_api.Configuration(
        host = "https://api.gateio.ws/api/v4",
        key="a1f72ac6ad4b715d9f14c772f79b52f7",
        secret="a709696ed22ac6e6f0b270e7ad0ee9c4a74cf653bee6306c182ad742baef1d84"
    )
    twilio_sid = "AC67c5c65a9355709c6b9c01b1a0f409e8"
    twilio_token = "de4105eec7e2fa5486ed915b3c1096a0"
    twilio_client = TwilioClient(twilio_sid, twilio_token)

    api_client = gate_api.ApiClient(configuration)
    # Create an instance of the API class
    spot_api = gate_api.SpotApi(api_client)

    try:
        workers = list()
        while True:
            cwd = os.getcwd()
            file_currency = open(cwd+"/coins.json", 'r')
            old_currency = json.loads(file_currency.read())
            file_currency.close()
            # List all futures contracts
            all_currency = spot_api.list_currencies()
            currency_list = list()
            for currency in all_currency:
                if currency.trade_disabled == False:
                    currency_list.append(currency.currency)
            new_one = list(set(currency_list) - set(old_currency))
            if len(new_one) > 0:
                message = twilio_client.messages.create(
                    to="+393206661546",
                    from_="+13615241098",
                    body="New Coin: "+' '.join([str(elem) for elem in new_one]))
                print(str(datetime.now())+" - New coin: "+' '.join([str(elem) for elem in new_one]))

                file_currency = open(cwd + "/coins.json", 'w')
                file_currency.write(json.dumps(currency_list))
                file_currency.close()

                all_pairs = spot_api.list_currency_pairs()

                for pair in all_pairs:
                    for coin in new_one:

                        if pair.base == coin and pair.quote == 'USDT':
                            p = Process(target=buyCoin, args=(pair,))
                            p.start()
                            workers.append(p)

                #    if pair.quote == 'USDT':
                #        print(pair)
            else:
                print(str(datetime.now())+" - No new coins")
            time.sleep(30)

    except KeyboardInterrupt:
        print("control-c")
        for p in workers:
            p.terminate()
            p.join()
    except GateApiException as ex:
        print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
    except ApiException as e:
        print("Exception when calling DeliveryApi->list_delivery_contracts: %s\n" % e)

def buyCoin(coin):
    coin = str(coin.base)

    cwd = os.getcwd()
    configfile = open(cwd + "/cfg.json", 'r')
    config = json.loads(configfile.read())
    configfile.close()
    configuration = gate_api.Configuration(
        host="https://api.gateio.ws/api/v4",
        key="a1f72ac6ad4b715d9f14c772f79b52f7",
        secret="a709696ed22ac6e6f0b270e7ad0ee9c4a74cf653bee6306c182ad742baef1d84"
    )
    api_client = gate_api.ApiClient(configuration)
    # Create an instance of the API class
    spot_api = gate_api.SpotApi(api_client)
    file_currency = open(cwd + "/"+coin+"_USDT.log", 'a')
    file_currency.write("START\n")
    file_currency.close()
    endtime = time.time() + (6 * 60 * 60)
    while endtime > time.time():
        found = False
        all_pairs = spot_api.list_currency_pairs()
        for pair in all_pairs:
            if pair.base == coin and pair.quote == 'USDT':
                found = True
                continueWhile = True
                while continueWhile:
                    if pair.buy_start == 0 or pair.buy_start < time.time():
                        file_currency = open(cwd + "/"+pair.id+".log", 'a')
                        file_currency.write("BUY\n")
                        file_currency.close()

                        pair_name = pair.id

                        api_response = spot_api.list_trades(pair_name, limit=1)
                        if len(api_response) == 0:
                            continue

                        file_currency = open(cwd + "/" + pair.id + ".log", 'a')
                        file_currency.write("TRADE FOUND\n")
                        file_currency.close()
                        api_response = api_response[0]
                        amount = config.amount / float(api_response.price)

                        file_currency = open(cwd + "/" + pair.id + ".log", 'a')
                        file_currency.write("Price: %s - Amount: %s\n" % (str(api_response.price), str(amount)) )
                        file_currency.close()
                        order = gate_api.Order(
                            currency_pair=pair_name,
                            price=str(api_response.price),
                            side='buy',
                            amount=str(amount)
                        )
                        created = spot_api.create_order(order)

                        file_currency = open(cwd + "/" + pair.id + ".log", 'a')
                        file_currency.write("Order created")
                        file_currency.write(json.dumps(created))
                        file_currency.close()
                        continueWhile = False
                    else:
                        time.sleep(1)
        if found == True:
            break
        time.sleep(60)




if __name__ == "__main__":
    checkCoins()