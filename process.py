import os, warnings, requests, json
publicKey = "FLWPUBK-7adb6177bd71dd43c2efa3f1229e3b7f-X"
secretKey = "FLWSECK-e6db11d1f8a6208de8cb2f94e293450e-X"


def verify_bvn(bvn):
    try:
        payload = {
            "seckey": "FLWSECK-e6db11d1f8a6208de8cb2f94e293450e-X "
        }

        #add BVN supplied from form to the url
        endpoint = "https://ravesandboxapi.flutterwave.com/v2/kyc/bvn/" + str(bvn)

        headers = {
            'content-type': 'application/json',
        }

        response = requests.get(endpoint, headers=headers, params=payload)
        #return JSON Data
        return (response.json())
    except:
        response = """
            {
                "status":"error"
            }
            """
        
        return json.loads(response)


def validate_otp(otp, transRef):
    try:
        payload = {
        "PBFPubKey": publicKey,
        "transaction_reference": transRef, 
        "otp": otp
        }
        endpoint = "https://api.ravepay.coflwv3-pug/getpaidx/api/validatecharge"
        headers = {
            'content-type': 'application/json',
        }
        response = requests.post(endpoint, headers=headers, params=payload)
        return (response.json())
    except:
        response = """
            {
                "status":"error"
            }
            """
        
        return json.loads(response)

def verify_pay():
    try:
        payload = {
            "txref":"MC-1520443531487",
            "SECKEY": secretKey
        }

        endpoint = "https://api.ravepay.co/flwv3-pug/getpaidx/api/v2/verify"

        headers = {
            'content-type': 'application/json',
        }

        response = requests.post(endpoint, headers=headers, params=payload)
        return (response.json())
    except:
        response = """
            {
                "status":"error"
            }
            """
        
        return json.loads(response)