import boto3
import datetime
from dateutil.tz import tzlocal
import botocore.exceptions
import hmac
import hashlib
import base64
import json
USER_POOL_ID = 'us-east-1_4fsvP2qjv'
CLIENT_ID = '5ntn9p5je3ths4s1p59pbnc1f3'
CLIENT_SECRET ='kpkd8q7fmu5d9h93ar6ggt6c3qten3v3sl9v4qgmedbamokmoe1'
def get_secret_hash(username):
  msg = username + CLIENT_ID 
  dig = hmac.new(str(CLIENT_SECRET).encode('utf-8'),
  msg = str(msg).encode('utf-8'), digestmod=hashlib.sha256).digest()
  d2 = base64.b64encode(dig).decode()
  return d2
def initiate_auth(client, username, password):
    secret_hash = get_secret_hash(username)
    try:
      resp = client.admin_initiate_auth(
                 UserPoolId=USER_POOL_ID,
                 ClientId=CLIENT_ID,
                 AuthFlow='ADMIN_NO_SRP_AUTH',
                 AuthParameters={
                     'USERNAME': username,
                     'SECRET_HASH': secret_hash,
                     'PASSWORD': password,
                  },
                ClientMetadata={
                  'username': username,
                  'password': password,
              })
    except client.exceptions.NotAuthorizedException:
        return None, "The username or password is incorrect"
    except client.exceptions.UserNotConfirmedException:
        return None, "User is not confirmed"
    except Exception as e:
        return None, e.__str__()
    return resp, None
def lambda_handler(event, context):
    session = assumed_role_session('arn:aws:iam::386726749336:role/OrganizationAccountDevAccessRole')
    client = session.client('cognito-idp')
    for field in ["username", "password"]:
        if event.get(field) is None:
            return  {"error": True, 
                "success": False, 
                "message": f"{field} is required", 
                "data": None}
    resp, msg = initiate_auth(client, event.get('username'), event.get('password'))
    if msg != None:
        return {'message': msg, 
              "error": True, "success": False, "data": None}
    if resp.get("AuthenticationResult"):
        return {"message": "success", 
                "error": False, 
                "success": True, 
                "data": {
                    "id_token": resp["AuthenticationResult"]["IdToken"],
                    "refresh_token": resp["AuthenticationResult"]["RefreshToken"],
                    "access_token": resp["AuthenticationResult"]["AccessToken"],
                    "expires_in": resp["AuthenticationResult"]["ExpiresIn"],
                    "token_type": resp["AuthenticationResult"]["TokenType"]
                }}
    else: #this code block is relevant only when MFA is enabled
        return {"error": True, 
           "success": False, 
           "data": None, "message": None}

assume_role_cache: dict = {}
def assumed_role_session(role_arn: str, base_session: botocore.session.Session = None):
    base_session = base_session or boto3.session.Session()._session
    fetcher = botocore.credentials.AssumeRoleCredentialFetcher(
        client_creator = base_session.create_client,
        source_credentials = base_session.get_credentials(),
        role_arn = role_arn,
        extra_args = {
        #    'RoleSessionName': None # set this if you want something non-default
        }
    )
    creds = botocore.credentials.DeferredRefreshableCredentials(
        method = 'assume-role',
        refresh_using = fetcher.fetch_credentials,
        time_fetcher = lambda: datetime.datetime.now(tzlocal())
    )
    botocore_session = botocore.session.Session()
    botocore_session._credentials = creds
    return boto3.Session(botocore_session = botocore_session)

if __name__ == '__main__':
    e = {'username':'spandian1', 
         'password':'P@ss3242'}
    c = None
    print(lambda_handler(e, c))