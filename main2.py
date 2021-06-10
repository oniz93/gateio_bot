from __future__ import print_function
import time
import gate_api
import os
from gate_api.exceptions import ApiException, GateApiException
from twilio.rest import Client as TwilioClient
import ujson as json
from datetime import datetime
from websocket import create_connection

cwd = os.getcwd()
configfile = open(cwd + "/cfg.json", 'r')
config = json.loads(configfile.read())
configfile.close()
# Defining the host is optional and defaults to https://api.gateio.ws/api/v4
# See configuration.py for a list of all supported configuration parameters.
configuration = gate_api.Configuration(
    host = "https://api.gateio.ws/api/v4",
    key=config['gate_key'],
    secret=config['gate_secret']
)
#twilio_sid = config.twillo_key
#twilio_token = config.twillo_secret
#twilio_client = TwilioClient(twilio_sid, twilio_token)

api_client = gate_api.ApiClient(configuration)
# Create an instance of the API class
spot_api = gate_api.SpotApi(api_client)

try:
    # while True:
    #     # List all futures contracts
    #     cwd = os.getcwd()
    #     file_currency = open(cwd+"/coins.json", 'r')
    #     old_currency = json.loads(file_currency.read())
    #     file_currency.close()
    #     all_currency = spot_api.list_currencies()
    #     currency_list = list()
    #     for currency in all_currency:
    #         if currency.trade_disabled == False:
    #             currency_list.append(currency.currency)
    #     new_one = list(set(currency_list) - set(old_currency))
    #     if len(new_one) > 0:
    #         message = twilio_client.messages.create(
    #             to="+393206661546",
    #             from_="+13615241098",
    #             body="New Coin: "+' '.join([str(elem) for elem in new_one]))
    #         print(str(datetime.now())+" - New coin: "+' '.join([str(elem) for elem in new_one]))
    #
    #         file_currency = open(cwd + "/coins.json", 'w')
    #         file_currency.write(json.dumps(currency_list))
    #         file_currency.close()
    #     else:
    #         print(str(datetime.now())+" - No new coins")
    #     time.sleep(30)
    all_pairs = spot_api.list_currency_pairs()
    all_currency = spot_api.list_currencies()
    for currency in all_currency:
        if currency.currency == 'BTC':
            print(currency)
    for pair in all_pairs:
        if pair.base == 'BTC' and pair.quote == 'USDT':
            print(pair)
    api_response = spot_api.list_trades('BTC_USDT', limit = 1)
    print(api_response)

    ws = create_connection("wss://api.gateio.ws/ws/v4/")
    ws.send(json.dumps({
        "time": int(time.time()),
        "channel": "spot.trades",
        "event": "subscribe",  # "unsubscribe" for unsubscription
        "payload": ["BTC_USDT"]
    }))
    print(ws.recv())
except GateApiException as ex:
    print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
except ApiException as e:
    print("Exception when calling DeliveryApi->list_delivery_contracts: %s\n" % e)