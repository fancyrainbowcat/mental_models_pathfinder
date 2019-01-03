from __future__ import print_function

import zipfile
import io
import pathlib
from flask import Flask, render_template, request, make_response, send_file
import json
import sys
import os
from apps.me import generate_graph_json, reduce_graph, save_graph_png, save_graph_json
from time import gmtime, strftime

app = Flask(__name__)

user_dict = dict()

class Log():
    def __init__(self, logfile):
        self.log = open(logfile, 'a')
        
    def write(self, s, uuid = ''):
        try:
            self.log = open(logfile, 'a')
        except IOError:
            print("log file already in use", file=sys.stderr)
        self.log.write(strftime("%Y_%m_%d_%H_%M_%S: "+uuid+': ', gmtime()));
        self.log.write(s+'\n');
        self.log.flush();

log = Log('./log.txt');

# Load list of files matching filters
debug = 2 # 0 - no debug console, 1 limited debug console, 2 full text log

def load_file_list(directory, filters):
    list = [f for f in sorted(os.listdir(directory)) if os.path.isfile(
        os.path.join(directory, f)) and any(filter in f for filter in filters)]
    return list


def get_uuid(data_input):
    uuid = data_input.pop(0).pop('uuid')
    return uuid, data_input


def save_to_uuid_dict(request):
    global user_dict

    # extract uuid to assign data to correct dictionary
    uuid, data = get_uuid(request.json)

    if(not uuid in user_dict):
        user_dict[uuid] = []

    user_dict[uuid] += data

    # print data input to console
    if(debug >= 2):
        log.write(json.dumps(user_dict), uuid)

    return uuid, data


def create_graphs(user_dict):
    # Export graphs
    team_id = [x['team_id'] for x in user_dict if 'team_id' in x][0]
    uuid = [x['uuid'] for x in user_dict if 'uuid' in x][-1]

    if(debug >= 2):
        log.write(json.dumps(user_dict))

    # Create reduced graph dummy
    G = generate_graph_json(user_dict)
    S = reduce_graph(G)

    save_graph_png(team_id+'_' + uuid+'weighted_graph_S.png', S)
    save_graph_png(team_id+'_' + uuid+'weighted_graph_G.png', G)

    # Export jsons
    save_graph_json(team_id+'_' + uuid+'weighted_graph_S.json', S)
    save_graph_json(team_id+'_' + uuid+'weighted_graph_G.json', G)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')


@app.route('/index', methods=['POST'])
def get_lickert():
    uuid, data = save_to_uuid_dict(request)

    # send HTTP response
    response = make_response(json.dumps(data))
    response.status_code = 200
    response.headers['Access-Control-Allow-Origin']

    return response


@app.route('/team', methods=['POST'])
def get_team_id():
    uuid, data = save_to_uuid_dict(request)

    response = make_response(json.dumps(data))
    response.status_code = 200
    response.headers['Access-Control-Allow-Origin']

    return response


@app.route('/submit', methods=['POST'])
def finished():
    uuid, data = save_to_uuid_dict(request)

    if(debug >= 1):
        print('REACHED SUBMIT :)', file=sys.stderr)
        log.write('REACHED SUBMIT', uuid)

    # if (data["result"] == "success"):
    # create_graphs(user_dict[uuid])

    team_id = [x['team_id'] for x in user_dict[uuid] if 'team_id' in x][-1]

    if not os.path.exists('./user_data/submissions'):
        os.makedirs('./user_data/submissions')

    if(debug >= 1):
        print('Save json file ' + team_id+'_' + uuid, file=sys.stderr)
        log.write('Save json file ' + team_id+'_' + uuid, uuid)
   
    with open('./user_data/submissions/' + team_id+'_' + uuid, 'w') as outfile:
        json.dump(([{'uuid': uuid}] + user_dict[uuid]), outfile)

    response = make_response(json.dumps(data))
    response.status_code = 200
    response.headers['Access-Control-Allow-Origin']

    return response


@app.route('/generate')
def generate():
    user_inputs = load_file_list('./user_data/submissions', [''])
    if('.DS_Store' in user_inputs):
        user_inputs.remove('.DS_Store')
    print('Generating graphs for ', file=sys.stderr)
    print(user_inputs, file=sys.stderr)

    for input in user_inputs:
        with open('./user_data/submissions/' + input, 'r') as infile:
            indata = json.load(infile)
            print(indata, file=sys.stderr)
            create_graphs(indata)

    response = make_response(json.dumps({"result": "result"}))
    response.status_code = 200
    response.headers['Access-Control-Allow-Origin']

    return response

@app.route('/get_log')
def get_log():
    log = open('./log.txt', 'r');

    if(debug >= 1):
        print('Download log', file=sys.stderr)

    return send_file(
        log,
        mimetype='application/text',
        as_attachment=True,
        attachment_filename='log.txt'
    )

@app.route('/get_data')
def download():
    base_path = './user_data/'
    data = io.BytesIO()
    with zipfile.ZipFile(data, mode='w') as z:
        for root, dirs, files in os.walk(base_path):
            for file in files:
                z.write(os.path.join(root, file))
    data.seek(0)

    filename = strftime('%Y_%m_%d_%H_%M_%S_', gmtime())+'user_data.zip'

    if(debug >= 1):
        print('Download '+filename, file=sys.stderr)
        log.write('Download '+filename)

    return send_file(
        data,
        mimetype='application/zip',
        as_attachment=True,
        attachment_filename=filename
    )

@app.route('/clear_data')
def clear():
    base_path = './user_data/'

    if(debug >= 1):
        print('ATTENTION!!! CLEARING ALL DATA!!!', file=sys.stderr)
        log.write('ATTENTION!!! CLEARING ALL DATA!!!')

    for root, dirs, files in os.walk(base_path):
            for file in files:
                try:
                    if os.path.isfile(os.path.join(root, file)):
                        os.unlink(os.path.join(root, file))
                except Exception as e:
                    print(e)
    return ('Cleared Data', 204)

if __name__ == "__main__":
    app.run()
