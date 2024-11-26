import numpy as np
from agent_controller_2 import AgentState
from filterpy.kalman import KalmanFilter

class agent_select:
    def __init__(self, agent1: AgentState, agent2: AgentState, selection_method="position", hz=60):
        self.agent1 = agent1
        self.agent2 = agent2
        if selection_method == "position":
            self.__method = self.position
            self.gaze_location = np.array([0,0])
            self.gaze_velocity = None
        elif selection_method == "velocity":
            self.__method = self.velocity
            self.__velo_cutoff = 0.5
            self.__angle_difference = 0.785
            self.gaze_velocity = np.array([0,0])
        elif selection_method == "classifier":
            self.__method = self.classifier
    
    def position(self) -> AgentState:
        # Simple comparison for closest agent to gaze position
        dist1 = np.linalg.norm(self.gaze_location - self.agent1.getPosition())
        dist2 = np.linalg.norm(self.gaze_location - self.agent2.getPosition())
        if dist1 < dist2:
            return self.agent1
        return self.agent2
    
    def velocity(self) -> AgentState:
        # Calculate vectors from gaze position to agents
        agent1_vec = self.agent1.getPosition() - self.gaze_location
        agent2_vec = self.agent2.getPosition() - self.gaze_location
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
            return self.agent1
        elif np.abs(a1_angle_rad) > np.abs(a2_angle_rad) and np.abs(a1_angle_rad - a2_angle_rad) < self.__angle_difference:
            return self.agent2
        return self.position()
    
    def classifier(self):
        return
    
    def getAgent(self, gaze_location: tuple):
        if not self.gaze_velocity:
            # Kalman filter to be implemented
            pass
        self.gaze_location = np.array([gaze_location[0], gaze_location[1]])

        return self.__method()
            