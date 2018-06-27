#!/usr/bin/python                                                               
# -*- coding: utf-8 -*-

import fire
import requests
import json


TRANSFER_EVENT_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
PRA_CONTRACT_ADDR = "0x9041fe5b3fdea0f5e4afdc17e75180738d877a01"
ENDPOINT_URL = 'https://mainnet.infura.io/metamask'

headers = {
    'Content-Type' : 'application/json'
}
data = {
    "jsonrpc":"2.0",
    "method":"eth_getLogs",
    "params":[{
        "fromBlock" : "0x0",
        "toBlock" : "latest",
        "address" : PRA_CONTRACT_ADDR,
        "topics": [
                TRANSFER_EVENT_TOPIC
        ]
    }],
    "id":1
}

class Tool(object):

    def fetch_log(self, snapshot_point='latest'):
        data['params'][0]['toBlock'] = snapshot_point
        log_data = requests.post(ENDPOINT_URL, headers=headers, json=data).text
        open('pra_log.json', 'w').write(log_data)

    def export_epra_snapshot(self):
        log_data = json.loads(open('pra_log.json', 'r').read())['result']
        addr_value_map = {
        }
        snapshot = open('epra_snapshot.txt', 'w')

        for log in log_data:
            fr = log['topics'][1]
            to = log['topics'][2]
            token_value = int(log['data'], 16)
            addr_value_map[fr] = addr_value_map.get(fr, 0) - token_value
            addr_value_map[to] = addr_value_map.get(to, 0) + token_value

        addr_values = []
        for key, value in addr_value_map.items():
            key = key.replace('0x000000000000000000000000', '0x')
            if value < 0:
                value = 100000000000000000000000000 + value
            addr_values.append((key, value))

        addr_values = sorted(addr_values, lambda a, b: int((b[1]-a[1])/1000000000000000000))

        for item in addr_values:
            value = item[1] / 1000000000000000000.0
            value = '%.7f' % (value)
            if value == '0.0000000':
                continue
            snapshot.write('%s %s\n' % (item[0], value))


if __name__ == '__main__':
    fire.Fire(Tool)
