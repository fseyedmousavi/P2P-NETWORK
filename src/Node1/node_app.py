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
file_name = ""

logging.getLogger().setLevel(logging.INFO)


@app.route('/<string:file_requested>/<string:nnu>', methods=['GET'])
def response(file_requested, nnu):
    if current_node['owned_files'].__contains__(file_requested):
        return jsonify({"string": '../Node' + str(current_node['node_number']) + '/ownedFiles/' + str(file_requested)})
    else:
        nodes: list = current_node['friend_nodes']
        x = [i for i in nodes if not (i['node_name'] == int(nnu))]
        return jsonify({"dict": find_closest(current_node['node_name'], nodes)})


def find_closest(current_number: int, friends: list):
    closest = friends[0]

    for f in friends:
        x = closest['node_name'] - current_number
        y = f['node_name'] - current_number
        if x > y:
            closest = f
    return closest


def request(next_node: dict):
    # reply is a string of file path (type: str)
    # if another node was returned (type: dict)
    request_str = "http://127.0.0.1:" + str(next_node['node_port']) + '/' + str(file_name) + '/' + str(current_node['node_number'])
    reply = requests.get(request_str)
    rep = reply.json()
    if rep.__contains__("dict"):
        nodes_visited.append(next_node)
        if nodes_visited.__contains__(rep["dict"]):
            request(find_closest(current_node['node_name'], current_node['friend_nodes']))
        else:
            logging.info("another path to node number " +
                         str(rep["dict"]['node_name']) + "was introduced")
            request(rep["dict"])
    elif rep.__contains__("string"):
        original = r'' + rep["string"]
        target = r'' + '../Node' + str(current_node['node_number']) + '/newFiles/' + file_name
        shutil.copyfile(original, target)
        logging.info("file was found and placed successfully")
        nodes_visited.clear()


string = input("make a request:")
if not (string.__contains__('request')):
    logging.info('INVALID INPUT')
else:
    file_name = string[8:]
    request(find_closest(current_node['node_number'], current_node['friend_nodes']))

if __name__ == "__main__":
    app.run(port=current_node['node_port'])
