import json
import os

file_name = "config.json"
ip_addr_title = "ip_addr"

def read_from_config():
    if not os.path.exists(file_name):
        return ""
    
    with open(file_name, 'r') as fp:
        config = json.load(fp)
        if ip_addr_title not in config.keys():
            return ""

        return config[ip_addr_title]


def save_to_config(ip_addr):
    with open(file_name, 'w') as fp:
        config = { ip_addr_title : ip_addr }
        json.dump(config, fp, indent=4)
