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
        elif selection_method == "velocity":
            self.__method = self.velocity
            self.__velo_cutoff = 0.5
            self.gaze_velocity = np.array([0,0])
        elif selection_method == "classifier":
            self.__method = self.classifier
    
    def position(self):
        # Simple comparison for closest agent to gaze position
        dist1 = np.linalg.norm(self.gaze_location - self.agent1.getPosition())
        dist2 = np.linalg.norm(self.gaze_location - self.agent2.getPosition())
        if dist1 < dist2:
            return self.agent1
        return self.agent2
    
    def velocity(self):
        # Calculate vectors from gaze position to agents
        agent1_vec = self.agent1.getPosition() - self.gaze_location
        agent2_vec = self.agent2.getPosition() - self.gaze_location
        # Calculate angle between gaze velocity and gaze -> agent

        if gaze_velo


        return
    
    def classifier(self):
        return
            