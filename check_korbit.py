#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import json
import time

import requests


def fetch_auth(payload):
    url = "https://api.korbit.co.kr/v1/oauth2/access_token"
    r = requests.post(url, data=payload)

    if r.status_code == requests.codes.ok:
        return json.loads(r.text)
    else:
        r.raise_for_status()


def authorize_pw(username, password, client_id, client_secret):
    payload = {
        "username": username, 
        "password": password, 
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "password"
        }
    return fetch_auth(payload)


def refresh_auth(refresh_token, client_id, client_secret):
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
        }
    return fetch_auth(payload)


def fetch_btc_value(access_token):
    headers = {"Authorization": access_token}
    api_url = "https://api.korbit.co.kr/v1/ticker/detailed"
    r = requests.get(api_url, headers=headers)
    if r.status_code == requests.codes.ok:
        resp = json.loads(r.text)
        return float(resp['last'])
    else:
        r.raise_for_status()


if __name__ == '__main__':
    if len(sys.argv) != 6:
        print(f"usage: python {__file__} id pw api_key api_secret threshold")
        exit(1)

    username = sys.argv[1]
    password = sys.argv[2]
    client_id = sys.argv[3]
    client_secret = sys.argv[4]
    threshold = float(sys.argv[5])

    auth = authorize_pw(username, password, client_id, client_secret)

    expires_at = time.time() + int(auth['expires_in'])

    period = 5

    while True:
        seconds_left = expires_at - time.time()
        if seconds_left < period:
            refresh_token = auth['refresh_token']
            auth = refresh_auth(refresh_token, client_id, client_secret)
            expires_at = time.time() + int(auth['expires_in'])

        last_val = fetch_btc_value(auth['access_token'])
        if last_val < threshold:
            print(f"BTC below {threshold}: {last_val}")
        else:
            pass

        time.sleep(period)
