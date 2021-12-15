from requests.api import request
import yaml
from flask import Flask
import shutil
import requests
import logging


app = Flask(__name__)


file1 = open("Config.yml")
current_node = yaml.load(file1, Loader=yaml.FullLoader)

nodes_visited = []
friend_counter = 0
file_name = ""


def request(next_node: dict, friend_counter: int):
    # reply is a string of file path (type: str)
    # if another node was returned (type: dict)
    reply = requests.get("http://127.0.0.1:" + str(
        next_node['node_port']) + '/' + file_name + '/' + str(current_node['node_number']))
    if (type(reply) == dict):
        nodes_visited.append(next_node)
        if (nodes_visited.__contains__(reply)):
            request(current_node['friend_nodes']
                    [friend_counter], friend_counter+1)
        else:
            logging.info("another path to node number " +
                         reply['node_name'] + "was introduced")
            request(reply, friend_counter)
    elif (type(reply) == str):
        original = r'' + reply
        target = r'' + 'Node' + \
            current_node['node_number'] + '/newFiles/' + file_name
        shutil.copyfile(original, target)
        logging.info("file was found and placed successfully")
        nodes_visited.clear()


@app.route('/', methods=['GET'])
def response(file_requested, node_number):
    node_number_requested = int(node_number)
    if (current_node['owned_files'].__contains__(file_requested)):
        return 'Node' + current_node['node_number'] + '/ownedFiles/' + file_requested
    else:
        nodes: list = current_node['friend_nodes']
        for node in nodes:
            if not (node['node_name'] == node_number_requested):
                return node


string = input()
if not(string.__contains__('request')):
    print('INVALID INPUT')
else:
    file_name = string[8:]
    request(current_node['friend_nodes'][friend_counter], friend_counter + 1)

if __name__ == "__main__":
    app.run(port=current_node['node_port'])
