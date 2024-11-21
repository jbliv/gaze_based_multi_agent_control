import turtle
from typing import Dict, List, Optional
import logging
from dataclasses import dataclass
import time
import threading

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentState:
    # Store state information for each agent
    turtle: turtle.Turtle
    position: tuple[float, float]
    heading: float
    speed: float
    selected: bool = False
    # Movement flags for continuous motion
    moving_forward: bool = False
    moving_backward: bool = False
    turning_left: bool = False
    turning_right: bool = False

class AgentController:
    def __init__(self, num_agents: int = 3, screen_width: int = 800, screen_height: int = 600):
        # Initialize the agent control system
        self.screen = turtle.Screen()
        self.screen.setup(screen_width, screen_height)
        self.screen.title("Multi-Agent Control System")
        
        # Initialize agents
        self.agents: Dict[int, AgentState] = {}
        self.selected_agent: Optional[int] = None
        self.movement_speed = 5
        self.rotation_speed = 15
        
        # Create agents
        self._initialize_agents(num_agents)
        
        # Set up key bindings
        self._setup_controls()
        
        # Start continuous movement thread
        self.running = True
        self.movement_thread = threading.Thread(target=self._continuous_movement_loop)
        self.movement_thread.daemon = True
        self.movement_thread.start()
        
    def _initialize_agents(self, num_agents: int) -> None:
        # Create and initialize turtle agents
        colors = ['red', 'blue', 'green', 'yellow', 'purple']
        
        for i in range(num_agents):
            agent = turtle.Turtle()
            agent.penup()
            agent.shape('turtle')
            agent.color(colors[i % len(colors)])
            # Position agents in different locations
            x = -200 + (i * 200)
            y = 0
            agent.setposition(x, y)
            
            self.agents[i] = AgentState(
                turtle=agent,
                position=(x, y),
                heading=0,
                speed=self.movement_speed
            )
            
    def _setup_controls(self) -> None:
        # Set up keyboard controls with press and release events
        # Number keys for agent selection
        for i in range(min(10, len(self.agents))):
            self.screen.onkey(lambda i=i: self.select_agent(i), str(i+1))
            
        # Movement key press events
        self.screen.onkeypress(self._start_forward, 'Up')
        self.screen.onkeypress(self._start_backward, 'Down')
        self.screen.onkeypress(self._start_left, 'Left')
        self.screen.onkeypress(self._start_right, 'Right')
        
        # Movement key release events
        self.screen.onkeyrelease(self._stop_forward, 'Up')
        self.screen.onkeyrelease(self._stop_backward, 'Down')
        self.screen.onkeyrelease(self._stop_left, 'Left')
        self.screen.onkeyrelease(self._stop_right, 'Right')
        
        # Speed controls
        self.screen.onkey(self._increase_speed, 'plus')
        self.screen.onkey(self._decrease_speed, 'minus')
        
        self.screen.listen()

    def _continuous_movement_loop(self):
        # Continuously update agent positions based on movement flags
        while self.running:
            if self.selected_agent is not None:
                agent = self.agents[self.selected_agent]
                
                if agent.moving_forward:
                    agent.turtle.forward(agent.speed)
                if agent.moving_backward:
                    agent.turtle.backward(agent.speed)
                if agent.turning_left:
                    agent.turtle.left(self.rotation_speed)
                if agent.turning_right:
                    agent.turtle.right(self.rotation_speed)
                    
                if any([agent.moving_forward, agent.moving_backward, 
                       agent.turning_left, agent.turning_right]):
                    agent.position = agent.turtle.position()
                    agent.heading = agent.turtle.heading()
                    
            time.sleep(0.016)  # Approx. 60 FPS
            
    def _start_forward(self):
        # Start moving selected agent forward
        if self.selected_agent is not None:
            self.agents[self.selected_agent].moving_forward = True
            
    def _start_backward(self):
        # Start moving selected agent backward
        if self.selected_agent is not None:
            self.agents[self.selected_agent].moving_backward = True
            
    def _start_left(self):
        # Start turning selected agent left
        if self.selected_agent is not None:
            self.agents[self.selected_agent].turning_left = True
            
    def _start_right(self):
        # Start turning selected agent right
        if self.selected_agent is not None:
            self.agents[self.selected_agent].turning_right = True
            
    def _stop_forward(self):
        # Stop moving selected agent forward
        if self.selected_agent is not None:
            self.agents[self.selected_agent].moving_forward = False
            
    def _stop_backward(self):
        # Stop moving selected agent backward
        if self.selected_agent is not None:
            self.agents[self.selected_agent].moving_backward = False
            
    def _stop_left(self):
        # Stop turning selected agent left
        if self.selected_agent is not None:
            self.agents[self.selected_agent].turning_left = False
            
    def _stop_right(self):
        # Stop turning selected agent right
        if self.selected_agent is not None:
            self.agents[self.selected_agent].turning_right = False
            
    def select_agent(self, agent_id: int) -> bool:
        # Select an agent for control
        if agent_id not in self.agents:
            logger.warning(f"Invalid agent ID: {agent_id}")
            return False
            
        # Deselect previously selected agent
        if self.selected_agent is not None:
            prev_agent = self.agents[self.selected_agent]
            prev_agent.selected = False
            prev_agent.turtle.color(prev_agent.turtle.color()[0])  # Reset to original color
            
        # Select new agent
        self.selected_agent = agent_id
        selected_agent = self.agents[agent_id]
        selected_agent.selected = True
        # Add visual feedback for selected agent
        original_color = selected_agent.turtle.color()[0]
        selected_agent.turtle.color(original_color, 'white')  # Change fill color to indicate selection
        
        logger.info(f"Selected agent {agent_id}")
        return True
            
    def _increase_speed(self) -> None:
        # Increase selected agent's speed
        if self.selected_agent is not None:
            agent = self.agents[self.selected_agent]
            agent.speed = min(agent.speed + 2, 20)
            logger.info(f"Speed increased to {agent.speed}")
            
    def _decrease_speed(self) -> None:
        # Decrease selected agent's speed
        if self.selected_agent is not None:
            agent = self.agents[self.selected_agent]
            agent.speed = max(agent.speed - 2, 1)
            logger.info(f"Speed decreased to {agent.speed}")
            
    def get_agent_positions(self) -> Dict[int, tuple[float, float]]:
        # Get current positions of all agents
        return {id: agent.position for id, agent in self.agents.items()}
        
    def cleanup(self) -> None:
        # Clean up turtle graphics and stop movement thread
        self.running = False
        self.movement_thread.join(timeout=1.0)
        self.screen.bye()

def main():
    # Demo function to test the controller
    controller = AgentController(num_agents=3)
    
    print("Controls:")
    print("1-3: Select agents")
    print("Arrow keys: Move/rotate selected agent")
    print("+/-: Adjust speed")
    
    # Keep the window open
    turtle.done()

if __name__ == "__main__":
    main()