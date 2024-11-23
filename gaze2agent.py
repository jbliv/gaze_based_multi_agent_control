import numpy as np
from agent_controller_2 import AgentState
from filterpy.kalman import KalmanFilter
from filterpy.

class agent_select:
    def __init__(self, agent1: AgentState, agent2: AgentState, selection_method="position", hz=60):
        self.agent1 = agent1
        self.agent2 = agent2
        if selection_method == "position":
            self.__method = self.position
            self.gaze_location = np.array([0,0])
        elif selection_method == "velocity":
            self.__method = self.velocity
        elif selection_method == "classifier":
            self.__method = self.classifier
    
    def position(self):
        dist1 = np.linalg.norm(self.gaze_location - self.agent1.getPosition)
        dist2 = np.linalg.norm(self.gaze_location - self.agent2.getPosition)
        if dist1 < dist2:
            return self.agent1
        return self.agent2
    
    def velocity(self):
        return
    
    def classifier(self):
        return
            