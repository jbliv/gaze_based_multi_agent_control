import tkinter as tk
from turtle import RawTurtle, TurtleScreen
from typing import Dict, Optional
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
    turtle: RawTurtle
    canvas: tk.Canvas
    position: tuple[float, float]
    heading: float
    speed: float
    selected: bool = False
    # Movement flags for continuous motion
    moving_forward: bool = False
    moving_backward: bool = False
    turning_left: bool = False
    turning_right: bool = False

class DualWindowController:
    def __init__(self, canvas_width: int = 400, canvas_height: int = 400):
        # Create single root window
        self.root = tk.Tk()
        self.root.title("Dual Turtle Control")
        
        # Create frame to hold canvases side by side
        frame = tk.Frame(self.root)
        frame.pack(expand=True, fill='both')
        
        # Create two canvases
        self.canvas1 = tk.Canvas(frame, width=canvas_width, height=canvas_height, bg='white')
        self.canvas1.pack(side='left', padx=5)
        self.screen1 = TurtleScreen(self.canvas1)
        
        self.canvas2 = tk.Canvas(frame, width=canvas_width, height=canvas_height, bg='white')
        self.canvas2.pack(side='left', padx=5)
        self.screen2 = TurtleScreen(self.canvas2)
        
        # Initialize agents
        self.agents: Dict[int, AgentState] = {}
        self.selected_window: Optional[int] = None
        self.movement_speed = 5
        self.rotation_speed = 15
        
        # Create agents
        self._initialize_agents()
        
        # Set up key bindings
        self._setup_controls()
        
        # Start movement updates
        self.running = True
        self._update_movement()

    def _initialize_agents(self) -> None:
        # Create one turtle in each canvas
        turtle1 = RawTurtle(self.screen1)
        turtle1.penup()
        turtle1.shape('turtle')
        turtle1.color('red')
        
        self.agents[0] = AgentState(
            turtle=turtle1,
            canvas=self.canvas1,
            position=(0, 0),
            heading=0,
            speed=self.movement_speed
        )
        
        turtle2 = RawTurtle(self.screen2)
        turtle2.penup()
        turtle2.shape('turtle')
        turtle2.color('blue')
        
        self.agents[1] = AgentState(
            turtle=turtle2,
            canvas=self.canvas2,
            position=(0, 0),
            heading=0,
            speed=self.movement_speed
        )

    def _setup_controls(self) -> None:
        # Set up keyboard controls
        self.root.bind('1', lambda event: self.select_window(0))
        self.root.bind('2', lambda event: self.select_window(1))
        
        # Center turtle control
        self.root.bind('b', lambda event: self._center_turtle())
        
        # Movement key press events
        self.root.bind('<Up>', lambda event: self._start_forward())
        self.root.bind('<Down>', lambda event: self._start_backward())
        self.root.bind('<Left>', lambda event: self._start_left())
        self.root.bind('<Right>', lambda event: self._start_right())
        
        # Movement key release events
        self.root.bind('<KeyRelease-Up>', lambda event: self._stop_forward())
        self.root.bind('<KeyRelease-Down>', lambda event: self._stop_backward())
        self.root.bind('<KeyRelease-Left>', lambda event: self._stop_left())
        self.root.bind('<KeyRelease-Right>', lambda event: self._stop_right())
        
        # Speed controls - fixed key bindings
        self.root.bind('<equal>', lambda event: self._increase_speed())  # + key (usually Shift+=)
        self.root.bind('<minus>', lambda event: self._decrease_speed())  # - key
        self.root.bind('<plus>', lambda event: self._increase_speed())   # + key on numpad
        self.root.bind('<KP_Add>', lambda event: self._increase_speed()) # + on numpad (some systems)
        self.root.bind('<KP_Subtract>', lambda event: self._decrease_speed()) # - on numpad

    def _update_movement(self):
        # Update agent positions based on movement flags
        if self.selected_window is not None:
            agent = self.agents[self.selected_window]
            
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
        
        # Schedule next update if still running
        if self.running:
            self.root.after(16, self._update_movement)  # Approx. 60 FPS

    def select_window(self, window_id: int) -> bool:
        # Select a window for control
        if window_id not in self.agents:
            logger.warning(f"Invalid window ID: {window_id}")
            return False
            
        # Deselect previously selected window
        if self.selected_window is not None:
            prev_agent = self.agents[self.selected_window]
            prev_agent.selected = False
            prev_agent.turtle.color(prev_agent.turtle.color()[0])
            prev_agent.canvas.configure(bg='white')
            
        # Select new window
        self.selected_window = window_id
        selected_agent = self.agents[window_id]
        selected_agent.selected = True
        
        # Visual feedback
        original_color = selected_agent.turtle.color()[0]
        selected_agent.turtle.color(original_color, 'white')
        selected_agent.canvas.configure(bg='lightgray')
        
        logger.info(f"Selected window {window_id + 1}")
        return True

    def _start_forward(self):
        if self.selected_window is not None:
            self.agents[self.selected_window].moving_forward = True
            
    def _start_backward(self):
        if self.selected_window is not None:
            self.agents[self.selected_window].moving_backward = True
            
    def _start_left(self):
        if self.selected_window is not None:
            self.agents[self.selected_window].turning_left = True
            
    def _start_right(self):
        if self.selected_window is not None:
            self.agents[self.selected_window].turning_right = True
            
    def _stop_forward(self):
        if self.selected_window is not None:
            self.agents[self.selected_window].moving_forward = False
            
    def _stop_backward(self):
        if self.selected_window is not None:
            self.agents[self.selected_window].moving_backward = False
            
    def _stop_left(self):
        if self.selected_window is not None:
            self.agents[self.selected_window].turning_left = False
            
    def _stop_right(self):
        if self.selected_window is not None:
            self.agents[self.selected_window].turning_right = False
            
    def _increase_speed(self) -> None:
        if self.selected_window is not None:
            agent = self.agents[self.selected_window]
            agent.speed = min(agent.speed + 1, 20)  # Increases by 2, max of 20
            # Print speed more visibly
            print(f"\nWindow {self.selected_window + 1} Speed: {agent.speed}")
            logger.info(f"Speed increased to {agent.speed}")
            
    def _decrease_speed(self) -> None:
        if self.selected_window is not None:
            agent = self.agents[self.selected_window]
            agent.speed = max(agent.speed - 1, 1)  # Decreases by 2, min of 1
            # Print speed more visibly
            print(f"\nWindow {self.selected_window + 1} Speed: {agent.speed}")
            logger.info(f"Speed decreased to {agent.speed}")

    def _center_turtle(self) -> None:
        # Center the selected turtle
        if self.selected_window is not None:
            agent = self.agents[self.selected_window]
            agent.turtle.penup()
            agent.turtle.home()  # Move to (0,0) and set heading to 0
            agent.position = (0, 0)
            agent.heading = 0
            print(f"\nCentered turtle in Window {self.selected_window + 1}")

    def get_agent_positions(self) -> Dict[int, tuple[float, float]]:
        return {id: agent.position for id, agent in self.agents.items()}
        
    def run(self):
        # Display controls
        print("Controls:")
        print("1: Select Left Canvas")
        print("2: Select Right Canvas")
        print("Arrow keys: Move/rotate selected turtle")
        print("+/-: Adjust speed")
        print("b: Center selected turtle")
        
        # Start the Tkinter main loop
        self.root.mainloop()

    def cleanup(self) -> None:
        self.running = False
        self.root.quit()

def main():
    controller = DualWindowController()
    controller.run()

if __name__ == "__main__":
    main()
