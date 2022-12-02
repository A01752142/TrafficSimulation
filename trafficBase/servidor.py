from flask import Flask, request, jsonify
from model import *
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer

app = Flask("Simulador de trafico")

@app.route('/init', methods=['POST', 'GET'])
def initModel():
    global currentStep, randomModel

    if request.method == 'POST':
        
        currentStep = 0

        print(request.form)
        randomModel = RandomModel(0)

        return jsonify({"message":"Parameters recieved, model initiated."})

@app.route('/getAgents', methods=['GET'])
def getTrafficLight():
    global randomModel

    if request.method == 'GET':
        agentPositions = [{"id": str(agent.unique_id), "x": x, "y":1, "z":z} for (a, x, z) in randomModel.grid.coord_iter() for agent in a if isinstance(agent, Car)]

        return jsonify({'positions':agentPositions})
        

@app.route('/getSemaforos', methods=['GET'])
def getObstacles():
    global randomModel

    if request.method == 'GET':
        semaforoPositions = [{"id": str(agent.unique_id), "x": x, "y":0, "z":z} for (a, x, z) in randomModel.grid.coord_iter() for agent in a if isinstance(agent, Traffic_Light) ]

        return jsonify({'positions':semaforoPositions})

@app.route('/update', methods=['GET'])
def updateModel():
    global currentStep, randomModel
    if request.method == 'GET':
        randomModel.step()
        currentStep += 1
        return jsonify({'message':f'Model updated to step {currentStep}.', 'currentStep':currentStep})

if __name__=='__main__':
    app.run(host="localhost", port=8585, debug=True)