import boto3
import botocore.exceptions
import hmac
import hashlib
import base64
import json
USER_POOL_ID = 'us-east-1_4d7E1DqhQ'
CLIENT_ID = '6dgiceasj3t7jof3ahuu7pl5sm'
CLIENT_SECRET = '1sno2sh62dvdf2o6jm3je5vc1i5i9e0lih4str1n1rvlmcdbb2og'
def get_secret_hash(username):
    msg = username + CLIENT_ID
    dig = hmac.new(str(CLIENT_SECRET).encode('utf-8'), 
        msg = str(msg).encode('utf-8'), digestmod=hashlib.sha256).digest()
    d2 = base64.b64encode(dig).decode()
    return d2

def disable_user(event, context):
    username = event['username']
    client = boto3.client('cognito-idp')
    try:
        return client.admin_disable_user(
            UserPoolId=USER_POOL_ID,
            Username=username
            )
    except Exception as e:
        return {"error": False, 
                "success": True, 
                "message": str(e), 
               "data": None}

def enable_user(event, context):
    username = event['username']
    client = boto3.client('cognito-idp')
    try:
        return client.admin_enable_user(
            UserPoolId=USER_POOL_ID,
            Username=username
            )
    except Exception as e:
        return {"error": False, 
                "success": True, 
                "message": str(e), 
               "data": None}

if __name__ == '__main__':
    e = {'name':'Soundar1', 
         'email':'spandian.contractor@pax8.com', 
         'username':'spandian1', 
         'password':'P@ss3242'}
    c = None
    print(disable_user(e, c))
    # print(enable_user(e, c))