import threading

from requests.api import request
import yaml
from flask import Flask, jsonify
import shutil
import requests
import logging

app = Flask(__name__)

file1 = open("Config.yml")
current_node = yaml.load(file1, Loader=yaml.FullLoader)

nodes_not_visited: list = None

logging.getLogger().setLevel(logging.INFO)


@app.route('/<string:file_requested>/<string:node_number>', methods=['GET'])
def response(file_requested, node_number):
    if len(get_current_node_friends()) == 0:
        return jsonify({"error": "no friend"})
    if current_node['owned_files'].__contains__(file_requested):
        logging.info(file_requested + " sent to node " + str(node_number))
        return jsonify({"string": '../Node' + str(current_node['node_number']) + '/ownedFiles/' + str(file_requested)})
    else:
        nodes: list = nodes_not_visited
        x = [i for i in nodes if not (i['node_number'] == int(node_number))]
        for j in x:
            fj = open("../Node" + str(j['node_number']) + "/Config.yml")
            cj = yaml.load(fj, Loader=yaml.FullLoader)
            if cj['owned_files'].__contains__(file_requested):
                logging.info("node " + str(cj['node_number']) + " sent to node " + str(node_number) + " as node which has the file")
                return jsonify({"dict": cj})
        y = find_closest(current_node['node_number'], x)
        logging.info("node " + str(y['node_number']) + " sent to node " + str(node_number) + " as the closest friend")
        return jsonify({"dict": y})


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
    url = "http://127.0.0.1:" + str(next_node['node_port'])
    logging.info("node " + str(current_node['node_number'])
                 + " requesting to node " + str(next_node['node_number']))
    request_str = url + '/' + str(file_name) + '/' + str(current_node['node_number'])
    sw = True
    reply = None
    try:
        reply = requests.get(request_str)
    except:
        sw = False
        logging.error(url + " is not accessible!")
        nodes_not_visited.remove(next_node)
        if len(nodes_not_visited) != 0:
            request(file_name, find_closest(current_node['node_number'], nodes_not_visited))
    if sw:
        rep = reply.json()
        if rep.__contains__("dict"):
            nodes_not_visited.remove(next_node)
            if not nodes_not_visited.__contains__(rep["dict"]):
                z = find_closest(current_node['node_number'], nodes_not_visited)
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
            initialize_nodes_not_visited()
        elif rep.__contains__("error"):
            logging.warning(str(next_node['node_number']) + " has no friends!")

def get_current_node_friends():
    return list(current_node['friend_nodes'])

def initialize_nodes_not_visited():
    global nodes_not_visited
    nodes_not_visited = get_current_node_friends()

def input_function():
    while True:
        string = input()
        if not (string.__contains__('request')):
            logging.info('INVALID INPUT')
        else:
            # file_name was used, don't remove!
            file_name = string[8:]
            if len(file_name) != 0:
                initialize_nodes_not_visited()
                request(file_name, find_closest(current_node['node_number'], nodes_not_visited))
                logging.info("request process done!")
            else:
                logging.error("no input")


initialize_nodes_not_visited()
thread = threading.Thread(target=input_function)
thread.start()

if __name__ == "__main__":
    app.run(port=current_node['node_port'])
