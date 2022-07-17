import os
import requests
import pdfkit
from requests.auth import HTTPBasicAuth

def emails_query(account_id, mailbox_id):
  return [[ "Email/query", {
    "accountId": account_id,
    "filter": { "inMailbox": mailbox_id},
    "sort": [{"property": "receivedAt", "isAscending": False}],
    "collapseThreads": True,
    "position": 0,
    "limit": 100
    }, "t0"],
    [ "Email/get", {
      "accountId": account_id,
      "#ids": {
        "resultOf": "t0",
        "name": "Email/query",
        "path": "/ids"
      },
      "properties": ["threadId"]
    }, "t1" ],
    [ "Thread/get", {
      "accountId": account_id,
      "#ids": { 
        "resultOf": "t1",
        "name": "Email/get",
        "path": "/list/*/threadId"
      }
    }, "t2"],
    [ "Email/get", {
        "accountId": account_id,
        "fetchHTMLBodyValues": True,
        "#ids": {
          "resultOf": "t2",
          "name": "Thread/get",
          "path": "/list/*/emailIds"
        },
        "properties": [ "subject", "bodyValues" ]
    }, "t3" ]]

def make_jmap_query(x):
  return { "using": ["urn:ietf:params:jmap:core", "urn:ietf:params:jmap:mail"], "methodCalls": x }

def fetch_inbox_id(account_id):
  mailbox_query = make_jmap_query([[ "Mailbox/get", {
    "accountId": account_id,
    "ids": None,
  }, "0" ]])
  data = requests.post(
    "https://jmap.fastmail.com/api/",
    auth=HTTPBasicAuth(os.environ["FASTMAIL_USERNAME"], os.environ["FASTMAIL_PASSWORD"]),
    json = mailbox_query
  ).json()

  for mailbox in data["methodResponses"][0][1]['list']:
    if mailbox["name"] == "Newsletters":
      return mailbox["id"]

def fetch_emails(account_id, mailbox_id):
  query = make_jmap_query(emails_query(account_id, mailbox_id))
  data = requests.post(
    "https://jmap.fastmail.com/api/",
    auth=HTTPBasicAuth(os.environ["FASTMAIL_USERNAME"], os.environ["FASTMAIL_PASSWORD"]),
    json = query
  ).json()
  return data["methodResponses"][3][1]["list"]

def create_pdfs(emails):
  for email in emails:
    pdfkit.from_string(list(email["bodyValues"].values())[0]["value"], f'/tmp/newsletters/{email["subject"]}.pdf')

def run():
  account_id = os.environ["FASTMAIL_ACCOUNT_ID"]
  mailbox_id = fetch_inbox_id(account_id)
  emails = fetch_emails(account_id, mailbox_id)

  create_pdfs(emails)

if __name__ == '__main__':
  run()
