from __future__ import print_function

from flask import Flask, render_template, request, make_response
import json
import sys
import os
from apps.me import generate_graph_json, reduce_graph, save_graph_png, save_graph_json
app = Flask(__name__)

user_dict = dict()

# Load list of files matching filters


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
    print(json.dumps(user_dict), file=sys.stderr)

    return uuid, data


def create_graphs(user_dict):
    print(json.dumps(user_dict), file=sys.stderr)
    # Create reduced graph dummy
    G = generate_graph_json(user_dict)
    S = reduce_graph(G)

    # Export graphs
    team_id = [x['team_id'] for x in user_dict if 'team_id' in x][0]
    uuid = [x['uuid'] for x in user_dict if 'uuid' in x][-1]

    save_graph_png(team_id+'_' + uuid+'weighted_graph_S.png', S)
    save_graph_png(team_id+'_' + uuid+'weighted_graph_G.png', G)

    # Export jsons
    save_graph_json(team_id+'_' + uuid+'weighted_graph_S.json', S)
    save_graph_json(team_id+'_' + uuid+'weighted_graph_G.json', G)


@app.route('/')
def index():
    return render_template('index.html')


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
    print('REACHED SUBMIT :)', file=sys.stderr)
    uuid, data = save_to_uuid_dict(request)
    print('REACHED SUBMIT :)2', file=sys.stderr)

    # if (data["result"] == "success"):
    # create_graphs(user_dict[uuid])

    team_id = [x['team_id'] for x in user_dict[uuid] if 'team_id' in x][-1]

    if not os.path.exists('./try'):
        os.makedirs('./try')
    print('Save json file ' + team_id+'_' + uuid, file=sys.stderr)
    with open('./try/' + team_id+'_' + uuid, 'w') as outfile:
        json.dump(([{'uuid': uuid}] + user_dict[uuid]), outfile)

    response = make_response(json.dumps(data))
    response.status_code = 200
    response.headers['Access-Control-Allow-Origin']

    return response


@app.route('/generate')
def generate():
    user_inputs = load_file_list('./try', [''])
    if('.DS_Store' in user_inputs):
        user_inputs.remove('.DS_Store')
    print('Generating graphs for ', file=sys.stderr)
    print(user_inputs, file=sys.stderr)

    for input in user_inputs:
        with open('./try/' + input, 'r') as infile:
            indata = json.load(infile)
            print(indata, file=sys.stderr)
            create_graphs(indata)

    response = make_response(json.dumps({"result": "result"}))
    response.status_code = 200
    response.headers['Access-Control-Allow-Origin']

    return response


if __name__ == "__main__":
    app.run()
