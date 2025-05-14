from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.core.audio import SoundLoader # For audio feedback, if needed
import random

# Assuming nback_logic.py is in the same directory
from nback_logic import NBackGame

class NBackGrid(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 3
        self.cells = []
        for i in range(9):
            # Cells are Labels, background is drawn on canvas
            cell_label = Label(text="") # No text needed for visual stimulus, just position
            with cell_label.canvas.before:
                Color(0.2, 0.2, 0.2, 1) # Default background color
                self.rect = Rectangle(size=cell_label.size, pos=cell_label.pos)
            cell_label.bind(size=self._update_rect, pos=self._update_rect)
            cell_label._highlighted = False # Custom property to track highlight state
            self.cells.append(cell_label)
            self.add_widget(cell_label)

    def _update_rect(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            if instance._highlighted:
                Color(0.1, 0.7, 0.1, 1) # Highlight color
            else:
                Color(0.2, 0.2, 0.2, 1) # Default color
            Rectangle(size=instance.size, pos=instance.pos)

    def highlight_cell(self, index):
        for i, cell_label in enumerate(self.cells):
            if i == index:
                cell_label._highlighted = True
            else:
                cell_label._highlighted = False
            # Trigger a redraw by updating a bound property (e.g., size, or manually call _update_rect)
            self._update_rect(cell_label, None) # Force redraw
    
    def clear_highlight(self):
        for cell_label in self.cells:
            cell_label._highlighted = False
            self._update_rect(cell_label, None) # Force redraw

class NBackApp(App):
    def build(self):
        self.title = 'Dual N-Back Game'
        self.game = NBackGame(n_value=2, sequence_length=20, num_positions=9, num_audio_stimuli=9) # Audio stimuli 0-8
        self.game_in_progress = False
        self.stimulus_duration = 1.5  # seconds to show stimulus
        self.inter_stimulus_interval = 0.5 # seconds between stimuli (response window)
        self.user_responded_visual = False
        self.user_responded_audio = False

        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        top_bar = BoxLayout(size_hint_y=None, height=50)
        self.n_value_label = Label(text=f"N = {self.game.n_value}")
        self.score_label = Label(text="Score: 0")
        top_bar.add_widget(self.n_value_label)
        top_bar.add_widget(self.score_label)
        self.layout.add_widget(top_bar)

        stimuli_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=0.6)
        self.visual_grid = NBackGrid(size_hint_x=0.7)
        stimuli_layout.add_widget(self.visual_grid)
        self.audio_label = Label(text="Audio: -", font_size='40sp', size_hint_x=0.3)
        stimuli_layout.add_widget(self.audio_label)
        self.layout.add_widget(stimuli_layout)

        controls_layout = GridLayout(cols=2, size_hint_y=None, height=100, spacing=10)
        self.visual_match_button = Button(text="Visual Match", on_press=self.on_visual_match, disabled=True)
        self.audio_match_button = Button(text="Audio Match", on_press=self.on_audio_match, disabled=True)
        controls_layout.add_widget(self.visual_match_button)
        controls_layout.add_widget(self.audio_match_button)
        self.layout.add_widget(controls_layout)

        self.start_button = Button(text="Start Game", on_press=self.start_game, size_hint_y=None, height=50)
        self.layout.add_widget(self.start_button)
        
        self.feedback_label = Label(text="Welcome! Press 'Start Game'", size_hint_y=None, height=30)
        self.layout.add_widget(self.feedback_label)

        return self.layout

    def start_game(self, instance):
        if not self.game_in_progress:
            self.game.generate_sequences()
            self.game_in_progress = True
            self.start_button.disabled = True
            self.score_label.text = "Score: 0"
            self.feedback_label.text = "Game Started! Get Ready..."
            self.visual_match_button.disabled = True
            self.audio_match_button.disabled = True
            Clock.schedule_once(self.present_stimulus, 1)

    def present_stimulus(self, dt):
        if self.game.is_game_over():
            self.end_game()
            return

        if self.game.current_trial > self.game.n_value:
            self.game.record_response(self.user_responded_visual, self.user_responded_audio)
            self.score_label.text = f"Score: {self.game.get_score()}"
        
        self.user_responded_visual = False
        self.user_responded_audio = False
        self.visual_match_button.background_color = [1,1,1,1] # Reset button color (Kivy expects list/tuple)
        self.audio_match_button.background_color = [1,1,1,1] # Reset button color

        visual_stim, audio_stim = self.game.next_trial()

        if visual_stim is not None:
            self.visual_grid.highlight_cell(visual_stim)
            self.audio_label.text = f"Audio: {audio_stim + 1}"
            self.feedback_label.text = f"Trial: {self.game.current_trial}/{self.game.sequence_length}"

            if self.game.current_trial > self.game.n_value:
                self.visual_match_button.disabled = False
                self.audio_match_button.disabled = False
            else:
                self.visual_match_button.disabled = True
                self.audio_match_button.disabled = True
            
            Clock.schedule_once(self.clear_stimulus, self.stimulus_duration)
        else:
            self.end_game()

    def clear_stimulus(self, dt):
        self.visual_grid.clear_highlight()
        self.audio_label.text = "Audio: -"
        if self.game.current_trial > self.game.n_value:
            self.feedback_label.text = "Respond now!"
        else:
            self.feedback_label.text = "Observe..."
        
        Clock.schedule_once(self.present_stimulus, self.inter_stimulus_interval)

    def on_visual_match(self, instance):
        if not self.visual_match_button.disabled:
            self.user_responded_visual = True
            self.visual_match_button.background_color = [0.5, 1, 0.5, 1] # Indicate press

    def on_audio_match(self, instance):
        if not self.audio_match_button.disabled:
            self.user_responded_audio = True
            self.audio_match_button.background_color = [0.5, 1, 0.5, 1] # Indicate press

    def end_game(self):
        self.game_in_progress = False
        self.start_button.disabled = False
        self.start_button.text = "Start New Game"
        self.visual_match_button.disabled = True
        self.audio_match_button.disabled = True
        self.visual_grid.clear_highlight()
        self.audio_label.text = "Audio: -"
        self.feedback_label.text = f"Game Over! Final Score: {self.game.get_score()}"
        self.score_label.text = f"Final Score: {self.game.get_score()}"

if __name__ == '__main__':
    NBackApp().run()

