from engine.agent_selection import AgentSelect
from engine.agent_state import AgentState
from engine.gaze_detection import GazeOTS

from typing import Dict, Optional, Tuple, Callable
from turtle import RawTurtle, TurtleScreen
import tkinter as tk
import numpy as np
import threading


class SingleWindowController:
    def __init__(self) -> None:
        self.test_gaze = GazeOTS()

        self.root = tk.Tk()
        self.root.title("Dual Turtle Control")

        # Get screen dimensions
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # Configure root window for fullscreen
        self.root.attributes("-fullscreen", True)

        # Create main frame
        self.frame = tk.Frame(self.root)
        self.frame.pack(expand=True, fill="both")

        # Create canvas first
        self.canvas = tk.Canvas(
            self.frame, width=self.screen_width, height=self.screen_height, bg="white"
        )
        self.canvas.pack(expand=True, fill="both")

        # Create instructions frame and place it on top of the canvas
        self.instructions_frame = tk.Frame(
            self.frame, bg="lightgray", bd=2, relief="solid"
        )
        self.instructions_frame.place(
            in_=self.canvas, relx=0.7, rely=0.02, relwidth=0.28, relheight=0.25
        )

        # Add instructions text with larger font
        self.instructions = tk.Text(
            self.instructions_frame,
            wrap=tk.WORD,
            font=("Arial", 24),
            bg="lightgray",
            relief="flat",
            padx=10,
            pady=0,
        )
        self.instructions.pack(expand=True, fill="both")

        instructions_text = """
Arrow keys: Move/rotate selected turtle
+/-: Adjust speed
d: Print canvas info
p/v: eye position/velocity
Escape: Exit fullscreen"""

        self.instructions.insert(tk.END, instructions_text)
        self.instructions.config(state="disabled")

        # Initialize turtle screen
        self.screen = TurtleScreen(self.canvas)

        # Store canvas dimensions
        self.canvas_width = self.screen_width
        self.canvas_height = self.screen_height

        # Set coordinate system with (0,0) at top-left
        self.screen.setworldcoordinates(0, self.screen_height, self.screen_width, 0)

        self.agents: Dict[int, AgentState] = {}
        self.selected_window: Optional[int] = None
        self.movement_speed = 20
        self.rotation_speed = 15

        self.position_callback: Optional[
            Callable[[Dict[int, Tuple[float, float]]], None]
        ] = None

        # Add escape key binding for exiting fullscreen
        self.root.bind("<Escape>", lambda e: self.on_escape())

        self._initialize_agents()
        self._setup_controls()
        self.agent_selector = AgentSelect(
            self.agents[0], self.agents[1], "position", 60
        )

        self.running = True
        self.background_thread = threading.Thread(
            target=self._background_agent, daemon=True
        )
        self.background_thread.start()

        self.running = True
        self._update_movement()

    def set_position_callback(
        self, callback: Callable[[Dict[int, Tuple[float, float]]], None]
    ) -> None:
        """Set a callback function to receive position updates."""
        self.position_callback = callback

    def _initialize_agents(self) -> None:
        # Position turtles relative to screen size
        left_pos = (self.screen_width * 0.25, self.screen_height * 0.5)
        right_pos = (self.screen_width * 0.75, self.screen_height * 0.5)

        # Create and configure first turtle
        turtle1 = RawTurtle(self.screen)
        turtle1.penup()
        turtle1.shape("turtle")
        turtle1.color("red")
        turtle1.shapesize(3, 3)  # Make turtle 3 times larger
        turtle1.setpos(*left_pos)

        self.agents[0] = AgentState(
            turtle=turtle1, position=left_pos, heading=0, speed=self.movement_speed
        )

        # Create and configure second turtle
        turtle2 = RawTurtle(self.screen)
        turtle2.penup()
        turtle2.shape("turtle")
        turtle2.color("green")
        turtle2.shapesize(3, 3)  # Make turtle 3 times larger
        turtle2.setpos(*right_pos)

        self.agents[1] = AgentState(
            turtle=turtle2, position=right_pos, heading=0, speed=self.movement_speed
        )

    def _setup_controls(self) -> None:
        self.root.bind("1", lambda event: self.select_window(0))
        self.root.bind("2", lambda event: self.select_window(1))

        self.root.bind("<Up>", lambda event: self._start_forward())
        self.root.bind("<Down>", lambda event: self._start_backward())
        self.root.bind("<Left>", lambda event: self._start_left())
        self.root.bind("<Right>", lambda event: self._start_right())

        self.root.bind("<KeyRelease-Up>", lambda event: self._stop_forward())
        self.root.bind("<KeyRelease-Down>", lambda event: self._stop_backward())
        self.root.bind("<KeyRelease-Left>", lambda event: self._stop_left())
        self.root.bind("<KeyRelease-Right>", lambda event: self._stop_right())

        self.root.bind("<equal>", lambda event: self._increase_speed())
        self.root.bind("<minus>", lambda event: self._decrease_speed())
        self.root.bind("<plus>", lambda event: self._increase_speed())
        self.root.bind("<KP_Add>", lambda event: self._increase_speed())
        self.root.bind("<KP_Subtract>", lambda event: self._decrease_speed())

        self.root.bind("p", lambda event: self.agent_selector.setMode("position"))
        self.root.bind("v", lambda event: self.agent_selector.setMode("velocity"))

        self.root.bind("d", lambda event: self.print_canvas_info())

    def get_all_positions(self) -> Dict[int, Tuple[float, float]]:
        """Return current positions of all turtles."""
        return {
            agent_id: agent.turtle.position() for agent_id, agent in self.agents.items()
        }

    def _get_bounds(self) -> Tuple[float, float, float, float]:
        padding = 20

        return (
            padding,
            self.screen_width - padding,
            padding,
            self.screen_height - padding,
        )

    def _clamp_position(self, pos: Tuple[float, float]) -> Tuple[float, float]:
        x, y = pos
        min_x, max_x, min_y, max_y = self._get_bounds()

        x = max(min_x, min(max_x, x))
        y = max(min_y, min(max_y, y))

        return (x, y)

    def _calculate_new_position(
        self, agent: AgentState, forward: bool = True
    ) -> Tuple[float, float]:
        heading_rad = np.radians(agent.turtle.heading())

        direction = 1 if forward else -1
        dx = direction * agent.speed * np.cos(heading_rad)
        dy = direction * agent.speed * np.sin(heading_rad)

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
                        agent, forward=agent.moving_forward
                    )

                    agent.turtle.setposition(new_pos)
                    agent.position = new_pos

                if agent.turning_left:
                    agent.turtle.left(-self.rotation_speed)
                    agent.heading = agent.turtle.heading()
                if agent.turning_right:
                    agent.turtle.right(-self.rotation_speed)
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
            if self.selected_window != window_id:
                prev_agent.selected = False
                prev_agent.moving_forward = False
                prev_agent.moving_backward = False
                prev_agent.turning_left = False
                prev_agent.turning_right = False
                prev_agent.turtle.color(prev_agent.turtle.color()[0])

        self.selected_window = window_id
        selected_agent = self.agents[window_id]
        selected_agent.selected = True

        original_color = selected_agent.turtle.color()[0]
        selected_agent.turtle.color(original_color, "white")

        return True

    def print_canvas_info(self):
        print(f"\nScreen dimensions: {self.screen_width}x{self.screen_height}")
        bounds = self._get_bounds()
        print(f"Coordinate bounds: {bounds}")
        for agent_id, agent in self.agents.items():
            print(f"Turtle {agent_id} position: {agent.turtle.position()}")

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

    def _background_agent(self) -> None:
        while self.running:
            self.select_window(
                self.agent_selector.getAgent(self.test_gaze.gaze_location) - 1
            )

    def on_escape(self):
        self.running = False  # Signal the background thread to stop
        self.root.destroy()  # Close the tkinter window

    def run(self):
        self.root.mainloop()


def main():
    controller = SingleWindowController()
    controller.run()


if __name__ == "__main__":
    main()
