import requests
import json


class API:
    def __init__(self, url):
        if url is None:
            self.url = "http://127.0.0.1/api/"
        else:
            self.url = url
        self.sessionkey = None
        self.user = None

    def post(self, endpoint, data=None):
        if data is None:
            data = {}
        if self.user is not None:
            data["user"] = self.user
        if self.sessionkey is not None:
            data["session_key"] = self.sessionkey

        resp = requests.post(self.url + endpoint, json=data)
        if resp.status_code == 200:
            return json.loads(resp.text)
        else:
            print(f"Error {resp.status_code}  {resp.text}")
        return None

    def login(self, user, password):
        resp = self.post("login", {"user": user, "password": password})
        if resp is None:
            self.user = None
            self.sessionkey = None
            print("Incorrect password")
            return None
        self.sessionkey = resp.get("result", {}).get("sessionkey", None)
        self.user = user
        return self.sessionkey

    def get_reported_transactions(self):
        if self.user is None or self.sessionkey is None:
            print("Session is not initialized")
            return None
        resp = self.post("get_reported_transactions")
        return resp.get("result", None)

    def get_wallets(self, owner):
        if self.user is None or self.sessionkey is None:
            print("Session is not initialized")
            return None
        resp = self.post("walletlist", {"owner": owner})
        return resp.get("result", None)

    def post_and_process_operation(self, operation):
        if self.user is None or self.sessionkey is None:
            print("Session is not initialized")
            return None
        resp = self.post("post_operation_and_process", {"operation": operation})
        return resp.get("result", None)

    def report_transaction_data(self, transaction_id, transaction_data):
        if self.user is None or self.sessionkey is None:
            print("Session is not initialized")
            return None
        resp = self.post("reporttransactiondata",
                         {"transaction_id": transaction_id, "transaction_data": transaction_data})
        return resp.get("result", None)
