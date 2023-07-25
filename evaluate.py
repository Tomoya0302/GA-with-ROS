import numpy as np
from socket import socket, AF_INET, SOCK_STREAM
import pickle
import dill

# Socket
HOST = 'localhost'
PORT = 8000
MAX_MESSAGE = 2048
NUM_THREAD = 1

EXPANSION = 0.1

class Robot():
    def __init__(self):
        self.rotation_list = np.loadtxt('rotation.csv', delimiter=',').reshape(24, 3, 3)
        self.host = HOST
        self.port = PORT
        self.num_thread = NUM_THREAD
        self.clients = []
        self.finish_flag = False

        with socket(AF_INET, SOCK_STREAM) as sock:
            sock.bind(('', self.port))
            sock.listen(NUM_THREAD)
            print('Waiting ...')
            try:
                con, addr = sock.accept()
            except KeyboardInterrupt:
                print('ERROR')
            print('[CONNECT] {}'.format(addr))
            self.clients.append((con, addr))

    def evaluate(self, pick, place, robot_position, robot_posture): # 引数 ([x,y,z], [x,y,z], [x,y,z], number)
        self.pick = np.dot(self.rotation_list[robot_posture], pick - robot_position)
        self.place = np.dot(self.rotation_list[robot_posture], place - robot_position)
        self.send_msg([7777]) # 7777 -> simulation, 8888 -> not simulation
        data = self.clients[0][0].recv(MAX_MESSAGE)
        # Convert Python 2 "ObjectType" to Python 3 object
        dill._dill._reverse_typemap["ObjectType"] = object
        data = pickle.loads(data, encoding='bytes')
        self.send_msg([self.pick[0]*EXPANSION, self.pick[1]*EXPANSION, self.pick[2]*EXPANSION, 0, 1.57, 0, 
                       self.place[0]*EXPANSION, self.place[1]*EXPANSION, self.place[2]*EXPANSION, 0, 1.57, 0])
        data = self.clients[0][0].recv(MAX_MESSAGE)
        # Convert Python 2 "ObjectType" to Python 3 object
        dill._dill._reverse_typemap["ObjectType"] = object
        ros_time = pickle.loads(data, encoding='bytes')
        return ros_time
    
    def close_connection(self):
        self.send_msg([9999])

    def send_msg(self, data):
        data = pickle.dumps(data, protocol=2) # if python2 -> protocol=2
        self.clients[0][0].sendto(data, self.clients[0][1])
