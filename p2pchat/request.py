import yaml
from flask import Flask
import shutil

node_config = open("\\src\\Node1\\Config.yml")
config = yaml.load(node_config, Loader=yaml.FullLoader)


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST', 'DELETE', 'PUT'])
def response(file_name, node_requested):
    if not(file_name.__contains__('request')):
        print('INVALID INPUT')
    else:
        node_name = next(iter(config['friend_nodes']))['node_name']
        node_file_name = 'Node' + next(iter(config['friend_nodes']))['node_name'] + '\\Config.yml'
        file = open(node_file_name)
        next_config = yaml.load(file, Loader=yaml.FullLoader)
        if (file_name in next_config['owned_files']):
            print('\n' + file_name + ' found in node number ' + node_name)
            original = r''+node_file_name+'\\ownedFiles\\file_name'
            target = r''+ 'Node' + node_requested +'\\newFiles\\filename'
            shutil.copyfile(original, target)
        else : 
            print ('\n' + file_name + ' not found in node number ' + node_name)
            
    
    
    
    
    
    
    
if __name__ == "__main__":
    app.run(debug=True)

    
file = open("NodeFiles.yml")
nodes = yaml.load(file, Loader=yaml.FullLoader)

number_of_nodes = len(nodes['node_files'])

# r = requests.get('https://api.github.com/user', auth=('user', 'pass'))



file_requested = input()
response(file_requested)

config['friend_nodes']