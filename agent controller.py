import tkinter as tk
from turtle import RawTurtle, TurtleScreen
from typing import Dict, Optional, Tuple
import math
from dataclasses import dataclass

@dataclass
class AgentState:
    turtle: RawTurtle
    position: tuple[float, float]
    heading: float
    speed: float
    selected: bool = False
    moving_forward: bool = False
    moving_backward: bool = False
    turning_left: bool = False
    turning_right: bool = False

class SingleWindowController:
    def __init__(self, width: int = 800, height: int = 600):
        self.root = tk.Tk()
        self.root.title("Dual Turtle Control")
        self.root.resizable(False, False)  # Disable resizing
        
        self.frame = tk.Frame(self.root)
        self.frame.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Create canvas with fixed size
        self.canvas = tk.Canvas(self.frame, width=width, height=height, bg='white')
        self.canvas.pack(expand=True, fill='both')
        self.screen = TurtleScreen(self.canvas)
        
        # Store canvas dimensions
        self.canvas_width = width
        self.canvas_height = height
        
        # Set coordinate system
        self.screen.setworldcoordinates(
            -width/2, -height/2,
            width/2, height/2
        )
        
        self.agents: Dict[int, AgentState] = {}
        self.selected_window: Optional[int] = None
        self.movement_speed = 10  # Default speed
        self.rotation_speed = 15
        
        # Add callback storage
        self.position_callback = None
        
        self._initialize_agents()
        self._setup_controls()
        
        self.running = True
        self._update_movement()

    def print_canvas_info(self):
        print(f"\nCanvas dimensions: {self.canvas_width}x{self.canvas_height}")
        bounds = self._get_bounds()
        print(f"Coordinate bounds: {bounds}")
        for agent_id, agent in self.agents.items():
            print(f"Turtle {agent_id} position: {agent.turtle.position()}")

    def _initialize_agents(self) -> None:
        turtle1 = RawTurtle(self.screen)
        turtle1.penup()
        turtle1.shape('turtle')
        turtle1.color('red')
        turtle1.setpos(-100, 0)
        
        self.agents[0] = AgentState(
            turtle=turtle1,
            position=(-100, 0),
            heading=0,
            speed=self.movement_speed
        )
        
        turtle2 = RawTurtle(self.screen)
        turtle2.penup()
        turtle2.shape('turtle')
        turtle2.color('green')
        turtle2.setpos(100, 0)
        
        self.agents[1] = AgentState(
            turtle=turtle2,
            position=(100, 0),
            heading=0,
            speed=self.movement_speed
        )

    def _setup_controls(self) -> None:
        self.root.bind('1', lambda event: self.select_window(0))
        self.root.bind('2', lambda event: self.select_window(1))
        
        self.root.bind('<Up>', lambda event: self._start_forward())
        self.root.bind('<Down>', lambda event: self._start_backward())
        self.root.bind('<Left>', lambda event: self._start_left())
        self.root.bind('<Right>', lambda event: self._start_right())
        
        self.root.bind('<KeyRelease-Up>', lambda event: self._stop_forward())
        self.root.bind('<KeyRelease-Down>', lambda event: self._stop_backward())
        self.root.bind('<KeyRelease-Left>', lambda event: self._stop_left())
        self.root.bind('<KeyRelease-Right>', lambda event: self._stop_right())
        
        self.root.bind('<equal>', lambda event: self._increase_speed())
        self.root.bind('<minus>', lambda event: self._decrease_speed())
        self.root.bind('<plus>', lambda event: self._increase_speed())
        self.root.bind('<KP_Add>', lambda event: self._increase_speed())
        self.root.bind('<KP_Subtract>', lambda event: self._decrease_speed())
        
        # Debug info binding
        self.root.bind('d', lambda event: self.print_canvas_info())

    def get_all_positions(self) -> Dict[int, Tuple[float, float]]:
        """Return current positions of all turtles."""
        return {
            agent_id: agent.position 
            for agent_id, agent in self.agents.items()
        }

    def _get_bounds(self) -> tuple[float, float, float, float]:
        padding = 20
        
        return (
            -self.canvas_width/2 + padding,   # left boundary
            self.canvas_width/2 - padding,    # right boundary
            -self.canvas_height/2 + padding,  # bottom boundary
            self.canvas_height/2 - padding    # top boundary
        )

    def _clamp_position(self, pos: tuple[float, float]) -> tuple[float, float]:
        x, y = pos
        min_x, max_x, min_y, max_y = self._get_bounds()
        
        x = max(min_x, min(max_x, x))
        y = max(min_y, min(max_y, y))
        
        return (x, y)

    def _calculate_new_position(self, agent: AgentState, forward: bool = True) -> tuple[float, float]:
        heading_rad = math.radians(agent.turtle.heading())
        
        direction = 1 if forward else -1
        dx = direction * agent.speed * math.cos(heading_rad)
        dy = direction * agent.speed * math.sin(heading_rad)
        
        current_x, current_y = agent.turtle.position()
        new_x = current_x + dx
        new_y = current_y + dy
        
        return self._clamp_position((new_x, new_y))

    def _update_movement(self):
        try:
            if self.selected_window is not None:
                agent = self.agents[self.selected_window]
                
                if agent.moving_forward or agent.moving_backward:
                    new_pos = self._calculate_new_position(
                        agent, 
                        forward=agent.moving_forward
                    )
                    
                    agent.turtle.setposition(new_pos)
                    agent.position = new_pos
                
                if agent.turning_left:
                    agent.turtle.left(self.rotation_speed)
                    agent.heading = agent.turtle.heading()
                if agent.turning_right:
                    agent.turtle.right(self.rotation_speed)
                    agent.heading = agent.turtle.heading()
            
            # Call position callback if set
            if self.position_callback:
                positions = self.get_all_positions()
                self.position_callback(positions)
            
            if self.running:
                self.root.after(16, self._update_movement)
        except Exception as e:
            print(f"Error in update movement: {e}")
            if self.running:
                self.root.after(16, self._update_movement)

    def select_window(self, window_id: int) -> bool:
        if window_id not in self.agents:
            return False
            
        if self.selected_window is not None:
            prev_agent = self.agents[self.selected_window]
            prev_agent.selected = False
            prev_agent.turtle.color(prev_agent.turtle.color()[0])
            
        self.selected_window = window_id
        selected_agent = self.agents[window_id]
        selected_agent.selected = True
        
        original_color = selected_agent.turtle.color()[0]
        selected_agent.turtle.color(original_color, 'white')
        
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
            agent.speed = min(agent.speed + 1, 20)
            print(f"\nTurtle {self.selected_window + 1} Speed: {agent.speed}")
            
    def _decrease_speed(self) -> None:
        if self.selected_window is not None:
            agent = self.agents[self.selected_window]
            agent.speed = max(agent.speed - 1, 1)
            print(f"\nTurtle {self.selected_window + 1} Speed: {agent.speed}")

    def run(self):
        print("Controls:")
        print("1: Select Red Turtle")
        print("2: Select Blue Turtle")
        print("Arrow keys: Move/rotate selected turtle")
        print("+/-: Adjust speed")
        print("d: Print canvas info")
        
        self.root.mainloop()

def main():
    # Set your desired window size here
    controller = SingleWindowController(width=1000, height=800)
    controller.run()

if __name__ == "__main__":
    main()