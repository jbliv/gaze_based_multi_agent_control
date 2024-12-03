import numpy
import agent_controller
import gaze2agent


def gaze_location(image):
    location = image
    return location


def agent_from_gaze(gaze_location):
    desired_agent = gaze_location
    return desired_agent


def control_agent(agent):
    control = agent
    return control


if __name__ == "__main__":
    image = None
    # Initialization code, whether that be a calibration sequence or accessing a stored calibration sequence
    controller = agent_controller.DualWindowController()
    agent1 = controller.agents[0]
    agent2 = controller.agents[1]
    agent_selector = gaze2agent.agent_select(agent1, agent2, "position", 60)

    # Loop for standard operations, exit condition tbd
    running = True
    while running:
        agent_selector.getAgent()  # input is gaze location
