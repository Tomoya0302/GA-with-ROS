from socket import socket, AF_INET, SOCK_STREAM
from contextlib import closing # if python2
from moveit_msgs.msg import RobotState as RS
from sensor_msgs.msg import JointState
from niryo_robot_python_ros_wrapper import *
import rospy
import moveit_commander
import pickle
import numpy as np
HOST = 'localhost'
PORT = 8000
MAX_MESSAGE = 2048

class Robot:
    def __init__(self):
        self.joint_state = JointState()
        self.moveit_robot_state = RS()

    def socket_up(self):
        print(' connectiong ... ')
        # with socket(AF_INET, SOCK_STREAM) as sock: # python3
        with closing(socket(AF_INET, SOCK_STREAM)) as sock: # python2
            sock.connect((HOST, PORT))
            self.main(sock)

    # client to server
    def send_message(self, sock, msg):
        while True:
            sock.send(msg.encode('utf-8'))
            break

    def set_up(self):
        # Initializing ROS node
        rospy.init_node('niryo_ned_example_python_ros_wrapper')
        # Connecting to the ROS wrapper & calibrating if needed
        self.robot = NiryoRosWrapper()
        self.robot.calibrate_auto()
        # self.robot.set_learning_mode(True)
        self.robot.move_to_sleep_pose()
        # get info
        self.move_group = moveit_commander.MoveGroupCommander('arm')
        self.robot_group = moveit_commander.RobotCommander()
        print(' [Group] ')
        print(' [name] ', self.move_group.get_name())
        # set planner
        self.move_group.set_planner_id('RRTstarkConfigDefault')
        planner_id = self.move_group.get_planner_id()
        print(' [planner] ', planner_id)
        self.move_group.set_planning_time(0.25)
        # set speed
        self.move_group.set_max_acceleration_scaling_factor(0.4)
        self.move_group.set_max_velocity_scaling_factor(0.4)

    def main(self, sock):
        self.sock = sock
        self.set_up()
        while True:
            self.offset_position = [0.0, 0.50, -1.25, 0.0, 0.0, 0.0]
            data = sock.recv(MAX_MESSAGE)
            data = pickle.loads(data)
            if data[0] == 7777: # continue (simulation)
                print('Continue [simulation]')
                self.simulation = True
                self.sock.send(pickle.dumps([0]))
            elif data[0] == 8888: # continue (without simulation)
                print('Continue')
                self.simulation = False
                self.sock.send(pickle.dumps([0]))
            elif data[0] == 9999: # finish
                print('Finish')
                break
            # move_joint
            target = sock.recv(MAX_MESSAGE)
            target = pickle.loads(target)
            ot_1 = self.execute(target[:6], self.simulation)
            ot_2 = self.execute(target[6:12], self.simulation)
            self.sock.send(pickle.dumps([ot_1 + ot_2]))

    def execute(self, target, simulation):
        # plan
        self.init(self.offset_position)
        self.move_group.set_pose_target(target)
        trj = self.move_group.plan(joints=None)
        # get length of trajectory
        points = np.array(trj.joint_trajectory.points)
        # initial time
        try:
            s = str(points[0])
        except IndexError:
            return float('inf')
        pos = s.find('positions')
        vel = s.find('velocities')
        sec = s.find('secs')
        nsec = s.find('nsecs')
        jointlist = s[pos+12:vel-2]
        a = [x.strip() for x in jointlist.split(',')]
        a = [float(y) for y in a]

        init_time = s[sec+6:nsec-3] + '.' + s[nsec+7:]
        init_time = float(init_time.replace(' ', ''))
        # end time
        s = str(points[-1])
        pos = s.find('positions')
        vel = s.find('velocities')
        sec = s.find('secs')
        nsec = s.find('nsecs')
        jointlist = s[pos+12:vel-2]
        self.offset_position = [x.strip() for x in jointlist.split(',')]
        self.offset_position = [float(y) for y in self.offset_position]

        end_time = s[sec+6:nsec-3] + '.' + s[nsec+7:]
        end_time = float(end_time.replace(' ', ''))
        elapsed_time = end_time - init_time
        # execute
        if not simulation:
            self.move_group.execute(trj, wait=True)
        return elapsed_time

    def init(self, position):
        self.joint_state.name = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'joint_5', 'joint_6']
        self.joint_state.position = position
        self.moveit_robot_state.joint_state = self.joint_state
        self.move_group.set_start_state(self.moveit_robot_state)

if __name__ == '__main__':
    robot = Robot()
    robot.socket_up()
