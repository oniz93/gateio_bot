from __future__ import print_function
import time
import gate_api
import os
from gate_api.exceptions import ApiException, GateApiException
from twilio.rest import Client as TwilioClient
import ujson as json
from datetime import datetime

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
except GateApiException as ex:
    print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
except ApiException as e:
    print("Exception when calling DeliveryApi->list_delivery_contracts: %s\n" % e)