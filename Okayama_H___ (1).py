
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
import random

# Assuming nback_logic.py is in the same directory
from nback_logic import NBackGame

class NBackGrid(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 3
        self.cells = []
        for i in range(9):
            cell = Button(text=str(i+1), background_normal='', background_color=(0.2, 0.2, 0.2, 1))
            cell.bind(on_press=self.cell_pressed) # For potential future use, not active in N-Back
            self.cells.append(cell)
            self.add_widget(cell)

    def highlight_cell(self, index):
        for i, cell in enumerate(self.cells):
            if i == index:
                cell.background_color = (0.1, 0.7, 0.1, 1) # Highlight color (e.g., green)
            else:
                cell.background_color = (0.2, 0.2, 0.2, 1) # Default color
    
    def cell_pressed(self, instance):
        # This function is not used for N-Back stimulus presentation
        # but could be used if the grid itself was an input mechanism.
        pass

class NBackApp(App):
    def build(self):
        self.title = 'Dual N-Back Game'
        self.game = NBackGame(n_value=2, sequence_length=20, num_positions=9, num_audio_stimuli=9)
        self.current_visual_stimulus = None
        self.current_audio_stimulus = None
        self.game_in_progress = False
        self.waiting_for_response = False

        # Main layout
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Top section for N-value and Score
        top_bar = BoxLayout(size_hint_y=None, height=50)
        self.n_value_label = Label(text=f"N = {self.game.n_value}")
        self.score_label = Label(text="Score: 0")
        top_bar.add_widget(self.n_value_label)
        top_bar.add_widget(self.score_label)
        self.layout.add_widget(top_bar)

        # Middle section for stimuli
        stimuli_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=0.6)
        
        # Visual stimulus (Grid)
        self.visual_grid = NBackGrid(size_hint_x=0.7)
        stimuli_layout.add_widget(self.visual_grid)
        
        # Audio stimulus (Label for now)
        self.audio_label = Label(text="Audio: -", font_size='30sp', size_hint_x=0.3)
        stimuli_layout.add_widget(self.audio_label)
        
        self.layout.add_widget(stimuli_layout)

        # Bottom section for controls
        controls_layout = BoxLayout(size_hint_y=None, height=100, spacing=10)
        self.visual_match_button = Button(text="Visual Match", on_press=self.on_visual_match, disabled=True)
        self.audio_match_button = Button(text="Audio Match", on_press=self.on_audio_match, disabled=True)
        controls_layout.add_widget(self.visual_match_button)
        controls_layout.add_widget(self.audio_match_button)
        self.layout.add_widget(controls_layout)

        self.start_next_button = Button(text="Start Game", on_press=self.start_or_next_trial, size_hint_y=None, height=50)
        self.layout.add_widget(self.start_next_button)
        
        self.feedback_label = Label(text="Welcome! Press 'Start Game'", size_hint_y=None, height=30)
        self.layout.add_widget(self.feedback_label)

        return self.layout

    def start_or_next_trial(self, instance):
        if not self.game_in_progress:
            self.game.generate_sequences()
            self.game_in_progress = True
            self.start_next_button.text = "Next Trial"
            self.score_label.text = "Score: 0"
            self.feedback_label.text = "Game Started!"
            # Disable match buttons until N trials have passed
            self.visual_match_button.disabled = True
            self.audio_match_button.disabled = True
            self.waiting_for_response = False # Reset waiting state
            self.proceed_to_next_stimulus()
        elif self.waiting_for_response:
            # If waiting for response, this button press means user chose not to press match
            # So, effectively a 'no match' response for both if they didn't click.
            # The game logic handles this by comparing recorded response (False by default if not pressed) with actual.
            # However, a more explicit 'no match' button or timeout would be better.
            # For now, we assume if they press Next Trial, they are done with current response period.
            if self.game.current_trial > self.game.n_value:
                 # If no explicit match button was pressed, we need to record 'False' for both
                 # This part needs refinement: how to handle 
