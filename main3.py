from __future__ import print_function
import time
import gate_api
import os
from gate_api.exceptions import ApiException, GateApiException
from twilio.rest import Client as TwilioClient
import ujson as json
from datetime import datetime
from multiprocessing import Process

def buyCoin(pair):
    cwd = os.getcwd()
    configfile = open(cwd + "/cfg.json", 'r')
    config = json.loads(configfile.read())
    configfile.close()
    # Defining the host is optional and defaults to https://api.gateio.ws/api/v4
    # See configuration.py for a list of all supported configuration parameters.
    configuration = gate_api.Configuration(
        host="https://api.gateio.ws/api/v4",
        key=config.gate_key,
        secret=config.gate_secret
    )
    api_client = gate_api.ApiClient(configuration)
    # Create an instance of the API class
    spot_api = gate_api.SpotApi(api_client)
    cwd = os.getcwd()
    file_currency = open(cwd + "/"+pair.id+".log", 'a')
    file_currency.write("START\n")
    file_currency.close()
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
            amount = 10 / float(api_response.price)

            file_currency = open(cwd + "/" + pair.id + ".log", 'a')
            file_currency.write("Price: %s - Amount: %s\n" % (str(api_response.price), str(amount)) )
            file_currency.close()
            order = gate_api.Order(
                currency_pair=pair_name,
                price=str(api_response.price),
                side='buy',
                amount=str(amount)
            )
            #created = spot_api.create_order(order)
            #print(created)

            file_currency = open(cwd + "/" + pair.id + ".log", 'a')
            file_currency.write("Order created")
            #file_currency.write(json.dumps(created))
            file_currency.close()
            continueWhile = False
        else:
            time.sleep(1)

if __name__ == "__main__":
    # Defining the host is optional and defaults to https://api.gateio.ws/api/v4
    # See configuration.py for a list of all supported configuration parameters.
    cwd = os.getcwd()
    configfile = open(cwd + "/cfg.json", 'r')
    config = json.loads(configfile.read())
    configfile.close()
    # Defining the host is optional and defaults to https://api.gateio.ws/api/v4
    # See configuration.py for a list of all supported configuration parameters.
    configuration = gate_api.Configuration(
        host="https://api.gateio.ws/api/v4",
        key=config.gate_key,
        secret=config.gate_secret
    )
    twilio_sid = config.twillo_key
    twilio_token = config.twillo_secret
    twilio_client = TwilioClient(twilio_sid, twilio_token)

    api_client = gate_api.ApiClient(configuration)
    # Create an instance of the API class
    spot_api = gate_api.SpotApi(api_client)
    all_pairs = spot_api.list_currency_pairs()
    workers = list()
    for pair in all_pairs:
        if pair.base == 'SHIB' and pair.quote == 'USDT':
            p = Process(target=buyCoin, args=(pair,))
            p.start()
            workers.append(p)