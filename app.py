from __future__ import print_function

from flask import Flask, render_template, request, make_response
import json
import sys
from apps.me import generate_graph_json, reduce_graph, save_graph_png, save_graph_json
app = Flask(__name__)

user_dict = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/index', methods = ['POST'])
def get_lickert():
    global user_dict
    data = request.json
    user_dict += data
    print(json.dumps(user_dict), file = sys.stderr)
    response = make_response(json.dumps(data))
    response.status_code = 200
    response.headers['Access-Control-Allow-Origin']

    return response

@app.route('/team', methods = ['POST'])
def get_team_id():
    global user_dict
    data = request.json
    user_dict += data
    print(json.dumps(data), file = sys.stderr)
    response = make_response(json.dumps(data))
    response.status_code = 200
    response.headers['Access-Control-Allow-Origin']

    return response

@app.route('/submit', methods = ['POST'])
def finished():
    data = request.json
    print(json.dumps(data), file = sys.stderr)

    if (data["result"] == "success"):

        # # Create reduced graph dummy
        G = generate_graph_json(user_dict)
        S = reduce_graph(G)

        # Export graphs
        team_id = [x['team_id'] for x in user_dict if 'team_id' in x]
        uuid = [x['uuid'] for x in user_dict if 'uuid' in x]

        save_graph_png(team_id[0]+'_'+ uuid[-1]+'weighted_graph_S.png', S)
        save_graph_png(team_id[0]+'_'+ uuid[-1]+'weighted_graph_G.png', G)

        # Export jsons
        save_graph_json(team_id[0]+'_'+ uuid[-1]+'weighted_graph_S.json', S)
        save_graph_json(team_id[0]+'_'+ uuid[-1]+'weighted_graph_G.json', G)
    response = make_response(json.dumps(data))
    response.status_code = 200
    response.headers['Access-Control-Allow-Origin']

    with open('./try/'+ team_id[0]+'_'+ uuid[-1], 'w') as outfile:
        json.dump(data, outfile)

    return response



if __name__ == "__main__":
    app.run()