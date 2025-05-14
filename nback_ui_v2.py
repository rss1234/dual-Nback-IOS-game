from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Line
from kivy.animation import Animation
from kivy.core.window import Window
import random

from nback_logic import NBackGame

SPLASH_IMAGE_PATH = r"E:\pyproject\dual-Nback-IOS-game\icon\Rick-SunRaise.jpg"
ICON_PATH = r"E:\pyproject\dual-Nback-IOS-game\icon\64x64icon1.png"
# User did not provide an info icon, using text button for now.
# INFO_ICON_PATH = "/home/ubuntu/upload/info_icon.png" 

class SplashScreen(Screen):
    def on_enter(self, *args):
        self.layout = BoxLayout(orientation='vertical')
        try:
            self.splash_image = Image(source=SPLASH_IMAGE_PATH, allow_stretch=True, keep_ratio=False)
            self.layout.add_widget(self.splash_image)
        except Exception as e:
            print(f"Error loading splash image: {e}")
            self.layout.add_widget(Label(text="Error loading splash image."))
        self.add_widget(self.layout)
        Clock.schedule_once(self.start_fade_out, 1.5)

    def start_fade_out(self, dt):
        if hasattr(self, 'splash_image') and self.splash_image:
            anim = Animation(opacity=0, duration=0.5)
            anim.bind(on_complete=self.go_to_main_menu)
            anim.start(self.splash_image)
        else:
            self.go_to_main_menu(None, None) # Go directly if image failed

    def go_to_main_menu(self, animation, widget):
        self.manager.current = 'main_menu'

class MainMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_n_value = 2
        self.min_n = 1
        self.max_n = 7 

        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        title = Label(text="Dual N-Back Game", font_size='32sp', size_hint_y=0.2)
        layout.add_widget(title)

        n_value_layout = BoxLayout(orientation='horizontal', size_hint_y=0.2, spacing=10)
        n_label = Label(text="N-Value:", font_size='24sp')
        self.n_value_display = Label(text=str(self.selected_n_value), font_size='24sp')
        btn_decrease_n = Button(text="-", font_size='24sp', on_press=self.decrease_n)
        btn_increase_n = Button(text="+", font_size='24sp', on_press=self.increase_n)
        
        n_value_layout.add_widget(n_label)
        n_value_layout.add_widget(btn_decrease_n)
        n_value_layout.add_widget(self.n_value_display)
        n_value_layout.add_widget(btn_increase_n)
        layout.add_widget(n_value_layout)

        start_button = Button(text="Start Game", font_size='28sp', size_hint_y=0.3, on_press=self.start_game)
        layout.add_widget(BoxLayout(size_hint_y=0.1))
        layout.add_widget(start_button)
        layout.add_widget(BoxLayout(size_hint_y=0.2))
        self.add_widget(layout)

    def decrease_n(self, instance):
        if self.selected_n_value > self.min_n:
            self.selected_n_value -= 1
            self.n_value_display.text = str(self.selected_n_value)

    def increase_n(self, instance):
        if self.selected_n_value < self.max_n:
            self.selected_n_value += 1
            self.n_value_display.text = str(self.selected_n_value)

    def start_game(self, instance):
        game_screen = self.manager.get_screen('game_screen')
        game_screen.set_n_value(self.selected_n_value)
        self.manager.current = 'game_screen'

class NBackGrid(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 3
        self.spacing = 5
        self.padding = 5 # Padding around the grid itself
        self.cells = []
        for i in range(9):
            cell_label = Label(text="") 
            with cell_label.canvas.before:
                Color(0.2, 0.2, 0.2, 1)
                self.cell_bg_rect = Rectangle(size=cell_label.size, pos=cell_label.pos)
                Color(0.5, 0.5, 0.5, 1) 
                self.cell_border = Line(rectangle=(cell_label.x, cell_label.y, cell_label.width, cell_label.height), width=1.2)
            cell_label.bind(size=self._update_cell_graphics, pos=self._update_cell_graphics)
            cell_label._highlighted = False
            self.cells.append(cell_label)
            self.add_widget(cell_label)

    def _update_cell_graphics(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            if instance._highlighted:
                Color(0.1, 0.7, 0.1, 1)
            else:
                Color(0.2, 0.2, 0.2, 1)
            Rectangle(size=instance.size, pos=instance.pos)
            Color(0.5, 0.5, 0.5, 1) 
            Line(rectangle=(instance.x +1, instance.y+1, instance.width-2, instance.height-2), width=1.2) # Adjusted for spacing

    def highlight_cell(self, index):
        for i, cell_label in enumerate(self.cells):
            cell_label._highlighted = (i == index)
            self._update_cell_graphics(cell_label, None)
    
    def clear_highlight(self):
        for cell_label in self.cells:
            cell_label._highlighted = False
            self._update_cell_graphics(cell_label, None)

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game = None
        self.game_in_progress = False
        self.stimulus_duration = 1.5
        self.inter_stimulus_interval = 0.5
        self.user_responded_visual = False
        self.user_responded_audio = False
        self.current_n_value = 2
        self.info_popup_instance = None

        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        top_bar = BoxLayout(size_hint_y=None, height=64, spacing=10)
        try:
            self.game_icon = Image(source=ICON_PATH, size_hint_x=None, width=64, height=64)
        except Exception as e:
            print(f"Error loading game icon: {e}")
            self.game_icon = Label(text="Icon", size_hint_x=None, width=64)
        self.n_value_label = Label(text=f"N = {self.current_n_value}", size_hint_x=0.2, font_size='18sp')
        self.score_label = Label(text="Score: 0", size_hint_x=0.5, font_size='18sp')
        
        self.info_button = Button(text="?", size_hint_x=None, width=64, font_size='24sp')
        self.info_button.bind(on_press=self.show_info_popup_on_press)
        self.info_button.bind(on_release=self.dismiss_info_popup_on_release)
        
        top_bar.add_widget(self.game_icon)
        top_bar.add_widget(self.n_value_label)
        top_bar.add_widget(self.score_label)
        top_bar.add_widget(self.info_button)
        self.layout.add_widget(top_bar)

        stimuli_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=0.6)
        self.visual_grid = NBackGrid(size_hint_x=0.7)
        stimuli_layout.add_widget(self.visual_grid)
        self.audio_label = Label(text="Audio: -", font_size='40sp', size_hint_x=0.3)
        stimuli_layout.add_widget(self.audio_label)
        self.layout.add_widget(stimuli_layout)

        controls_layout = GridLayout(cols=2, size_hint_y=None, height=100, spacing=10)
        self.visual_match_button = Button(text="Visual Match", on_press=self.on_visual_match, disabled=True, font_size='18sp')
        self.audio_match_button = Button(text="Audio Match", on_press=self.on_audio_match, disabled=True, font_size='18sp')
        controls_layout.add_widget(self.visual_match_button)
        controls_layout.add_widget(self.audio_match_button)
        self.layout.add_widget(controls_layout)

        self.back_to_menu_button = Button(text="Back to Menu", on_press=self.go_to_main_menu, size_hint_y=None, height=50, font_size='18sp')
        self.layout.add_widget(self.back_to_menu_button)
        
        self.feedback_label = Label(text="Select N and Start from Main Menu", size_hint_y=None, height=30, font_size='16sp')
        self.layout.add_widget(self.feedback_label)
        self.add_widget(self.layout)

    def set_n_value(self, n_val):
        self.current_n_value = n_val
        self.n_value_label.text = f"N = {self.current_n_value}"
        self.game = NBackGame(n_value=self.current_n_value, sequence_length=20, num_positions=9, num_audio_stimuli=9)

    def on_enter(self, *args):
        if self.game:
            self.start_game_sequence()
        else:
            self.feedback_label.text = "Error: Game not initialized. Go to Menu."

    def start_game_sequence(self, *args):
        if not self.game_in_progress and self.game:
            self.game.generate_sequences()
            self.game_in_progress = True
            self.back_to_menu_button.disabled = True 
            self.score_label.text = "Score: 0"
            self.feedback_label.text = "Game Started! Get Ready..."
            self.visual_match_button.disabled = True
            self.audio_match_button.disabled = True
            Clock.schedule_once(self.present_stimulus, 1) 

    def present_stimulus(self, dt):
        if not self.game_in_progress: return
        if self.game.is_game_over():
            self.end_game()
            return

        if self.game.get_current_trial_number() > self.game.n_value: 
            self.game.record_response_and_score(self.user_responded_visual, self.user_responded_audio)
            self.score_label.text = f"Score: {self.game.get_score()}"
        
        self.user_responded_visual = False
        self.user_responded_audio = False
        self.visual_match_button.background_color = [1,1,1,1]
        self.audio_match_button.background_color = [1,1,1,1]

        visual_stim, audio_stim = self.game.next_stimuli() 

        if visual_stim is not None:
            self.visual_grid.highlight_cell(visual_stim)
            self.audio_label.text = f"Audio: {audio_stim + 1}"
            self.feedback_label.text = f"Trial: {self.game.get_current_trial_number()}/{self.game.sequence_length - self.game.n_value} (scorable)"

            if self.game.get_current_trial_number() > self.game.n_value:
                self.visual_match_button.disabled = False
                self.audio_match_button.disabled = False
            else:
                self.visual_match_button.disabled = True
                self.audio_match_button.disabled = True
            Clock.schedule_once(self.clear_stimulus, self.stimulus_duration)
        else:
            self.end_game()

    def clear_stimulus(self, dt):
        if not self.game_in_progress: return
        self.visual_grid.clear_highlight()
        self.audio_label.text = "Audio: -"
        if self.game.get_current_trial_number() > self.game.n_value:
            self.feedback_label.text = "Respond now!"
        else:
            self.feedback_label.text = "Observe..."
        Clock.schedule_once(self.present_stimulus, self.inter_stimulus_interval)

    def on_visual_match(self, instance):
        if not self.visual_match_button.disabled:
            self.user_responded_visual = True
            self.visual_match_button.background_color = [0.5, 1, 0.5, 1]

    def on_audio_match(self, instance):
        if not self.audio_match_button.disabled:
            self.user_responded_audio = True
            self.audio_match_button.background_color = [0.5, 1, 0.5, 1]

    def end_game(self):
        self.game_in_progress = False
        self.back_to_menu_button.disabled = False
        self.visual_match_button.disabled = True
        self.audio_match_button.disabled = True
        self.visual_grid.clear_highlight()
        self.audio_label.text = "Audio: -"
        
        final_score = self.game.get_score() if self.game else 0
        max_score = self.game.get_max_possible_score() if self.game else 0
        score_text = f"Game Over!\nFinal Score: {final_score} / {max_score}"

        popup_content = BoxLayout(orientation='vertical', padding=20, spacing=10)
        popup_content.add_widget(Label(text=score_text, font_size='24sp', halign='center'))
        close_button = Button(text="OK", size_hint_y=None, height=50, font_size='18sp')
        popup_content.add_widget(close_button)
        
        self.score_popup = Popup(title="Game Finished", content=popup_content,
                            size_hint=(0.6, None), height=Window.height*0.4, auto_dismiss=False)
        close_button.bind(on_press=self.dismiss_score_popup)
        self.score_popup.open()

    def dismiss_score_popup(self, instance):
        self.score_popup.dismiss()
        self.go_to_main_menu(None)

    def go_to_main_menu(self, instance):
        self.game_in_progress = False 
        if hasattr(self, 'score_popup') and self.score_popup.content and self.score_popup.content.parent:
            self.score_popup.dismiss()
        if self.info_popup_instance and self.info_popup_instance.content and self.info_popup_instance.content.parent:
            self.info_popup_instance.dismiss()
            self.info_popup_instance = None
        self.manager.current = 'main_menu'

    def show_info_popup_on_press(self, instance):
        if self.info_popup_instance and self.info_popup_instance.content.parent:
            return
        info_text = (f"Dual N-Back Game v2.0\n\n"
                     f"Instructions:\n"
                     f"- Visual: Click 'Visual Match' if the square's position is the same as N trials ago.\n"
                     f"- Audio: Click 'Audio Match' if the displayed number is the same as N trials ago.\n"
                     f"- N is currently set to: {self.current_n_value}\n\n"
                     f"Developer: Manus AI Agent")
        
        popup_main_content = BoxLayout(orientation='vertical', padding=10, spacing=5)
        info_label = Label(text=info_text, halign='left', valign='top', color=(1,1,1,1), font_size='14sp')
        info_label.bind(size=lambda *x: setattr(info_label, 'text_size', (info_label.width, None)))
        popup_main_content.add_widget(info_label)

        wrapper = BoxLayout(opacity=0.9) 
        with wrapper.canvas.before:
            Color(0.15, 0.15, 0.15, 0.9)
            self.info_popup_bg_rect = Rectangle(size=wrapper.size, pos=wrapper.pos)
        wrapper.bind(size=self._update_info_popup_bg, pos=self._update_info_popup_bg)
        wrapper.add_widget(popup_main_content)
        
        self.info_popup_instance = Popup(title='Game Info & Credits', content=wrapper, 
                                         size_hint=(None, None), size=(Window.width * 0.8, Window.height * 0.6),
                                         auto_dismiss=False, title_color=(1,1,1,1), separator_color=(0.3,0.3,0.3,1))
        self.info_popup_instance.open()

    def _update_info_popup_bg(self, instance, value):
        if hasattr(self, 'info_popup_bg_rect'):
            self.info_popup_bg_rect.pos = instance.pos
            self.info_popup_bg_rect.size = instance.size

    def dismiss_info_popup_on_release(self, instance):
        if self.info_popup_instance:
            self.info_popup_instance.dismiss()
            self.info_popup_instance = None

class NBackApp(App):
    def build(self):
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        self.title = 'Dual N-Back Game v2'
        sm = ScreenManager(transition=FadeTransition(duration=0.25))
        sm.add_widget(SplashScreen(name='splash_screen'))
        sm.add_widget(MainMenuScreen(name='main_menu'))
        sm.add_widget(GameScreen(name='game_screen'))
        return sm

if __name__ == '__main__':
    NBackApp().run()

