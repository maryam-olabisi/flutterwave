from flask import Flask, jsonify, request, render_template, session, logging, flash, redirect, url_for
from wtforms import Form, StringField, PasswordField, validators, TextField, IntegerField
from flask_restful import Resource, Api
from flask_cors import CORS
import requests
import random
from process import *
from encrypt import *

app = Flask(__name__)
#CORS(app)
def start_app():
    app = Flask(__name__)
    CORS(app)
    return app


 
@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

class bvn_form(Form):
    bvnText = StringField('BVN',[validators.Length(11)],
                                render_kw={"placeholder": "Enter Your BVN"})
    lastName = StringField('Last Name',[validators.Length(min=1, message=(u'Too short For A Name'))],
                                render_kw={"placeholder": "Last Name"})
    phoneNumber = TextField('Phone Number', [validators.Length(min=11, max=11, message=(u'Input Your 11 Digits Phone Number'))],
                                render_kw={"placeholder": "Phone Number"})

class pay_form(Form):
    cardName = StringField('Name',[validators.Length(min=5, message=(u'Too short For A Name'))],
                                render_kw={"placeholder": "NAME ON CARD"})
    cardnumber = StringField('Card Number', [validators.Length(min=16, max=16, message=(u'Enter A Valid Card Number'))],
                                render_kw={"placeholder": "CARD NUMBER"})
    cvv = PasswordField('Pasword', [validators.Length(min=3, max=3, message=(u'Enter A Valid CVV'))],
                                render_kw={"placeholder": "cvv"})
    pin = PasswordField('Pasword', [validators.Length(min=4, max=4, message=(u'Enter A Valid Secret Pin'))],
                                render_kw={"placeholder": "PIN"})
    expiryMonth = IntegerField('Month', [validators.NumberRange(min=1, max=12, message=(u'Invalid Month'))],
                                render_kw={"placeholder": "MM"})
    expiryYear = IntegerField('Year', [validators.NumberRange(min=2019, max=2030, message=(u'Invalid Year'))],
                                render_kw={"placeholder": "YYYY"})                                

class otp_form(Form):
    otpText = StringField('OTP', [validators.Length(min=6, message=(u'Too Short For An OTP'))],
                                render_kw={"placeholder": "CARD NUMBER"})

@app.route('/verify', methods=['GET', 'POST'])
def bvn():
    form = bvn_form(request.form)

    if request.method == 'POST' and form.validate():
        #extract bvn & last name, and phone number from form
        bvn = form.bvnText.data
        lN = form.lastName.data
        pN = form.phoneNumber.data
        result = verify_bvn(bvn)
        #check status
        status = result["status"]
        if status == "error":
            #Error. Try Again
            error = "An Error Occurred. Confirm BVN And/Or Internet Connection."
            return render_template('verify.html', form=form, error=error)
        
        if status == "success":
            #bvn verified - check if name or phone number tallies
            lName = result["data"]["last_name"]
            fName = result["data"]["first_name"]
            pNumber = result["data"]["phone_number"]
            if (lName != lN) or (pNumber != pN):
                #either or both doesnt corelate
                error = "Error Occurred. Please Confirm Provided Information."
                return render_template('verify.html', form=form, error=error)
            else:
                #display name and continue
                success = "Welcome, " + lName + " " + fName + " You'll Soon Be Redirected."
                return render_template('verify.html', form=form, success=success) 
    return render_template('verify.html', form=form) #r.json()

@app.route('/payment', methods=['GET', 'POST'])
def pay():
    form = pay_form(request.form)

    if request.method == 'POST' and form.validate():
        #collect card details
        cNo = form.cardnumber.data
        cvv = form.cvv.data
        cExpiryMonth = form.expiryMonth.data
        cExpiryYear = form.expiryYear.data
        cPin = form.pin.data
        cName = form.cardName.data

        try:
            rave = PayTest()
            #amount and driveraccount universal
            response = rave.pay_via_card(cName, cNo, cExpiryMonth, cExpiryYear, cvv, cPin, amount, driverAccount)

            result = response["status"]
            responseCode = response["data"]["chargeResponseCode"]
            authModel = response["data"]["authModelUsed"]

            #if success
            if result == "success":
                if responseCode == "02":
                    #check authmodel
                    if authModel == "PIN":
                        message = response["data"]["chargeResponseMessage"]
                        trans_ref = response["data"]["flwRef"]
                        #go to otp page
                        return redirect(url_for('otp', message=message, trans_ref=trans_ref))
                    elif authModel == "VBVSECURECODE":
                        authurl = response["data"]["authurl"]
                        #authurl is mock - not a valid url
                        iframe = random.choice(authurl)
                        return render_template('transaction.html', iframe=iframe)
                        
                elif responseCode == "00":
                    #payment successful
                    return redirect(url_for(transactions))

            elif result == "error":
                error = "Error Occurred. Please Confirm Provided Information."
                return render_template('payment.html', form=form, error=error)
            
        except:
            error = "Error Occurred. Try Again"
            return render_template('payment.html', form=form, error=error)

    return render_template('payment.html', form=form)

@app.route('/otp', methods=['GET', 'POST'])
def otp(message, trans_ref):
    form = otp_form(request.form)
    if request.method == 'POST' and form.validate():
        otPass = form.otpText.data
        #validate otp
        response = validate_otp(otPass, trans_ref)
        result = response["status"]
        if result == "success":
            #verify currency and amount are good, then verify payment
            if (response["data"]["tx"]["currency"] == "NGN") and (float(response["data"]["tx"]["amount"]) <= float(response["data"]["tx"]["charged_amount"])):
                res = verify_pay()
                if res["status"] == "error":
                    error = "Error Occured. Payment Not Successful"
                    return render_template('error.html', error=error)
                elif res["status"] == "success":
                    return redirect(url_for(transactions))
            else:
                #amount not correlation &/or currency not the same - abort
                error = "Error Occured. Payment Not Successful"
                return render_template('error.html', error=error)
        else:
            #error occured
            error = "Incorrect OTP. Payment Not Successful"
            return render_template('error.html', error=error)


    return render_template('otp.html', form=form, message=message, trans_ref=trans_ref)


@app.route('/transactions', methods=['GET'])
def transactions():
    #render page after a successful transaction
    return render_template('transaction.html')

@app.route('/error', methods=['GET'])
def error():
    #render page when otp fails
    return render_template('error.html')



if __name__ == '__main__':
    app.secret_key = "run_t3st"
    app.run(host='0.0.0.0', debug=True, threaded=True)