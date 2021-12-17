import threading
import time

from requests.api import request
import yaml
from flask import Flask, jsonify
import shutil
import requests
import logging


app = Flask(__name__)

file1 = open("Config.yml")
current_node = yaml.load(file1, Loader=yaml.FullLoader)

nodes_visited = []

logging.getLogger().setLevel(logging.INFO)


@app.route('/<string:file_requested>/<string:node_number>', methods=['GET'])
def response(file_requested, node_number):
    if len(current_node['friend_nodes']) == 0:
        return jsonify({"error": "no friend"})
    if current_node['owned_files'].__contains__(file_requested):
        return jsonify({"string": '../Node' + str(current_node['node_number']) + '/ownedFiles/' + str(file_requested)})
    else:
        nodes: list = current_node['friend_nodes']
        x = [i for i in nodes if not (i['node_number'] == int(node_number))]
        for j in x:
            fj = open("../Node" + str(j['node_number']) + "/Config.yml")
            cj = yaml.load(fj, Loader=yaml.FullLoader)
            if cj['owned_files'].__contains__(file_requested):
                return jsonify({"dict": cj})
        return jsonify({"dict": find_closest(current_node['node_number'], x)})

def find_closest(current_number: int, friends: list):
    if len(friends) == 0:
        return None
    closest = friends[0]

    for f in friends:
        if closest['node_number'] > current_number:
            x = closest['node_number'] - current_number
        else:
            x = current_number - closest['node_number']
        if f['node_number'] > current_number:
            y = f['node_number'] - current_number
        else:
            y = current_number - f['node_number']
        if x > y:
            closest = f
    return closest


def request(file_name: str, next_node: dict):
    logging.info("node " + str(current_node['node_number'])
                 + " requesting to node " + str(next_node['node_number']))
    request_str = "http://127.0.0.1:" + str(next_node['node_port']) + '/' + str(file_name) + '/' + str(current_node['node_number'])
    reply = requests.get(request_str)
    rep = reply.json()
    if rep.__contains__("dict"):
        nodes_visited.append(next_node)
        if nodes_visited.__contains__(rep["dict"]):
            y = [i for i in current_node['friend_nodes'] if not (i in nodes_visited)]
            z = find_closest(current_node['node_number'], y)
            if z is not None:
                request(file_name, z)
            else:
                logging.warning("file not found!")
        else:
            logging.info("another path to node number " +
                         str(rep["dict"]['node_number']) + " was introduced")
            request(file_name, rep["dict"])
    elif rep.__contains__("string"):
        original = r'' + rep["string"]
        target = r'' + '../Node' + str(current_node['node_number']) + '/newFiles/' + file_name
        shutil.copyfile(original, target)
        logging.info("file was found and placed successfully")
        nodes_visited.clear()
    elif rep.__contains__("error"):
        logging.warning(str(next_node['node_number']) + " has no friends!")

def input_function():
    while True:
        string = input()
        if not (string.__contains__('request')):
            logging.info('INVALID INPUT')
        else:
            # file_name was used, don't remove!
            file_name = string[8:]
            if len(file_name) != 0:
                request(file_name, find_closest(current_node['node_number'], current_node['friend_nodes']) )
            else:
                logging.error("no input")


thread = threading.Thread(target=input_function)
thread.start()

if __name__ == "__main__":
    app.run(port=current_node['node_port'])
