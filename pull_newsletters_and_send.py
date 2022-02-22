import json
import os
import urllib.request

def emails_query(account_id):
    return [[ "Email/query", {
        "accountId": account_id,
        "filter": { "inMailbox": mailbox_id}, # TODO: is this something that is static or dynamic
        "sort": [{"property": "receivedAt", "isAscending": False}],
        "collapseThreads": True,
        }, "t0"],
        [ "Email/get", {
            "accountId": account_id,
            "#ids": {
                "resultOf": "t0",
                "name": "Email/query",
                "path": "/ids"
            }
        }]
    ]

def fetch_session_token():
    username = os.environ['FASTMAIL_USERNAME']
    password = os.environ['FASTMAIL_PASSWORD']
    auth_handler =  urllib.request.HTTPBasicAuthHandler()
    auth_handler.add_password(
            realm='jmap.fastmail.com',
            uri='https://jmap.fastmail.com',
            user=username,
            passwd=password
    )
    opener = urllib.request.build_opener(auth_handler)

    try:
        with opener.open('https://jmap.fastmail.com/.well-known/jmap') as response:
            return json.loads(response.read().decode('utf-8'))['primaryAccounts']['urn:ietf:params:jmap:mail']
    except urllib.error.HTTPError as e:
        print('Error fetching fastmail session', e)



def run():
    session_token = fetch_session_token()
    
if __name__ == '__main__':
    run()
