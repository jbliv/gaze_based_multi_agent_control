from engine.agent_state import AgentState

import numpy as np
import time
from filterpy.kalman import KalmanFilter
from filterpy.common import Q_discrete_white_noise



class AgentSelect:
    def __init__(self, agent1: AgentState, agent2: AgentState, selection_method="position", hz=60):
        self.agent1 = agent1
        self.agent2 = agent2
        self.last_time = None
        self.selection_method = selection_method
        if selection_method == "position":
            self.__method = self.position
            self.gaze_location = np.array([0,0])
            self.gaze_velocity = None
        elif selection_method == "velocity":
            self.__method = self.velocity
            self.__velo_cutoff = 50
            self.__angle_difference = 0.785
            self.gaze_velocity = np.array([0,0])

            # Kalman filter init coed
            self.kf = KalmanFilter(dim_x=4, dim_z=2)

            # Initial state [x, vx, y, vy]
            self.kf.x = np.array([0., 0., 0., 0.])

            # State transition matrix
            dt = 1.0  # initial time step
            
            self.kf.F = np.array([[1., dt, 0., 0.],
                            [0., 1., 0., 0.],
                            [0., 0., 1., dt],
                            [0., 0., 0., 1.]])

            # Measurement function
            self.kf.H = np.array([[1., 0., 0., 0.],
                            [0., 0., 1., 0.]])

            # Measurement noise covariance
            self.kf.R = np.eye(2) * 10

            # Process noise covariance with initial dt
            self.kf.Q = Q_discrete_white_noise(dim=4, dt=dt, var=0.1)

            # Error covariance matrix
            self.kf.P *= 1000
    
    def position(self) -> int:
        # Simple comparison for closest agent to gaze position
        dist1 = np.linalg.norm(self.gaze_location - self.agent1.position)
        dist2 = np.linalg.norm(self.gaze_location - self.agent2.position)
        self.current_time = time.time()
        if dist1 < dist2:
            # print("Agent 1")
            return 1
        # print("Agent 2")
        return 2
    
    def velocity(self) -> AgentState:
        # Calculate vectors from gaze position to agents
        agent1_vec = self.agent1.position - self.gaze_location
        agent2_vec = self.agent2.position - self.gaze_location
        # Calculate angle between gaze velocity and gaze -> agent
        if np.linalg.norm(self.gaze_velocity) < self.__velo_cutoff:
            return self.position()
        
        # Normalize the vectors
        unit_a1 = agent1_vec / np.linalg.norm(agent1_vec)
        unit_a2 = agent2_vec / np.linalg.norm(agent2_vec)
        unit_gv = self.gaze_velocity / np.linalg.norm(self.gaze_velocity)
        
        # Calculate the dot product
        a1_dot_product = np.dot(unit_a1, unit_gv)
        a2_dot_product = np.dot(unit_a2, unit_gv)
        
        # Calculate the angle in radians
        a1_angle_rad = np.arccos(a1_dot_product)
        a2_angle_rad = np.arccos(a2_dot_product)
        if np.abs(a1_angle_rad) < np.abs(a2_angle_rad) and np.abs(a1_angle_rad - a2_angle_rad) < self.__angle_difference:
            return 1
        elif np.abs(a1_angle_rad) > np.abs(a2_angle_rad) and np.abs(a1_angle_rad - a2_angle_rad) < self.__angle_difference:
            return 2
        return self.position()
    
    def getAgent(self, gaze_location: tuple):
        if self.selection_method == "velocity":
            # Kalman filter to be implemented
            current_time = time.time()
            if self.last_time is not None:
                dt = current_time - self.last_time
                self.kf.F = np.array([[1., dt, 0., 0.],
                              [0., 1., 0., 0.],
                              [0., 0., 1., dt],
                              [0., 0., 0., 1.]])
                self.kf.Q = Q_discrete_white_noise(dim=4, dt=dt, var=0.1)
                self.kf.predict()

            measurement = np.array([gaze_location[0], gaze_location[1]])
            self.kf.update(measurement)

            self.last_time = current_time
            vx, vy = self.kf.x[1], self.kf.x[3]
            self.gaze_velocity = np.array([vx, vy])
            print(self.gaze_velocity)
        self.gaze_location = np.array([gaze_location[0], gaze_location[1]])

        return self.__method()
            