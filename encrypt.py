import os, hashlib, warnings, requests, json
import base64
from Crypto.Cipher import DES3
import datetime

driverAccount = "RS_344DD49DB5D471EF565C897ECD67CD95"
amount = "1000"
current_date = str(datetime.datetime.today().year) + str(datetime.datetime.today().month) + str(datetime.datetime.today().day) + str(datetime.datetime.today().hour) + str(datetime.datetime.today().minute) + str(datetime.datetime.today().second)

class PayTest(object):

    """this is the getKey function that generates an encryption Key for you by passing your Secret Key as a parameter."""

    def __init__(self):
        pass

    def getKey(self,secret_key):
        hashedseckey = hashlib.md5(secret_key.encode("utf-8")).hexdigest()
        hashedseckeylast12 = hashedseckey[-12:]
        seckeyadjusted = secret_key.replace('FLWSECK-', '')
        seckeyadjustedfirst12 = seckeyadjusted[:12]
        return seckeyadjustedfirst12 + hashedseckeylast12

    """This is the encryption function that encrypts your payload by passing the text and your encryption Key."""

    def encryptData(self, key, plainText):
        blockSize = 8
        padDiff = blockSize - (len(plainText) % blockSize)
        cipher = DES3.new(key, DES3.MODE_ECB)
        plainText = "{}{}".format(plainText, "".join(chr(padDiff) * padDiff))
        # cipher.encrypt - the C function that powers this doesn't accept plain string, rather it accepts byte strings, hence the need for the conversion below
        test = plainText.encode('utf-8')
        encrypted = base64.b64encode(cipher.encrypt(test)).decode("utf-8")
        return encrypted


    def pay_via_card(self, name, no, exM, exY, cvv, pin, amount, driverAcc):
        data = {
                "PBFPubKey": "FLWPUBK-4e581ebf8372cd691203b27227e2e3b8-X",
                "cardno": no,
                "cvv": cvv,
                "expirymonth": exM,
                "expiryyear": exY,
                "currency": "NGN",
                "country": "NG",
                "amount": amount,
                "email": "user@gmail.com",
                "phonenumber": "0902620185",
                "lastname": name,
                "pin": pin,
                "suggested_auth": "PIN",
                "subaccounts": [
                  {
                    "id": "RS_D87A9EE339AE28BFA2AE86041C6DE70E",
                    "transaction_split_ratio": "1"
                  },
                  {
                    "id": driverAcc,
                    "transaction_split_ratio": "9"
                  }
                ],
                "IP": "355426087298442",
                "txRef": "MC-",
                "meta": [
                  {
                    "metaname": "flightID",
                    "metavalue": "123949494DC"
                  }
                ],
                "IP": "355426087298442",
                "txRef": "MC-" + current_date,
                "redirect_url": "https://rave-webhook.herokuapp.com/receivepayment",
                "device_fingerprint": "69e6b7f0b72037aa8428b70fbe03986c"
            }               

        sec_key = 'FLWSECK-bb971402072265fb156e90a3578fe5e6-X'

        # hash the secret key with the get hashed key function
        hashed_sec_key = self.getKey(sec_key)

        # encrypt the hashed secret key and payment parameters with the encrypt function

        encrypt_3DES_key = self.encryptData(hashed_sec_key, json.dumps(data))

        # payment payload
        payload = {
            "PBFPubKey": "FLWPUBK-e634d14d9ded04eaf05d5b63a0a06d2f-X",
            "client": encrypt_3DES_key,
            "alg": "3DES-24"
        }

        # card charge endpoint
        endpoint = "https://ravesandboxapi.flutterwave.com/flwv3-pug/getpaidx/api/charge"

        # set the content type to application/json
        headers = {
            'content-type': 'application/json',
        }

        response = requests.post(endpoint, headers=headers, data=json.dumps(payload))
        return (response.json()) 






