import random

class NBackGame:
    def __init__(self, n_value=2, sequence_length=20, num_positions=9, num_audio_stimuli=9):
        self.n_value = n_value
        self.sequence_length = sequence_length
        self.num_positions = num_positions  # For visual stimuli (e.g., 3x3 grid)
        self.num_audio_stimuli = num_audio_stimuli # For audio stimuli (e.g., digits 1-9 or letters)

        self.visual_sequence = []
        self.audio_sequence = []
        
        self.current_trial = 0
        self.score = 0
        
        self.user_visual_responses = [] # True if user thinks current visual matches N-back
        self.user_audio_responses = []  # True if user thinks current audio matches N-back

    def _generate_stimulus(self, num_options):
        """Generates a single stimulus (either visual position or audio sound)."""
        return random.randint(0, num_options - 1)

    def generate_sequences(self):
        """Generates both visual and audio sequences for the game."""
        self.visual_sequence = [self._generate_stimulus(self.num_positions) for _ in range(self.sequence_length)]
        self.audio_sequence = [self._generate_stimulus(self.num_audio_stimuli) for _ in range(self.sequence_length)]
        self.current_trial = 0
        self.score = 0
        self.user_visual_responses = []
        self.user_audio_responses = []

    def next_trial(self):
        """Advances to the next trial and returns the current stimuli."""
        if self.current_trial < self.sequence_length:
            visual_stimulus = self.visual_sequence[self.current_trial]
            audio_stimulus = self.audio_sequence[self.current_trial]
            self.current_trial += 1
            return visual_stimulus, audio_stimulus
        else:
            return None, None # Game over

    def record_response(self, visual_match_response, audio_match_response):
        """Records the user's response for the current trial (after N trials have passed)."""
        if self.current_trial > self.n_value:
            self.user_visual_responses.append(visual_match_response)
            self.user_audio_responses.append(audio_match_response)
            self._check_response()

    def _check_response(self):
        """Checks the user's response against the actual N-back matches and updates score."""
        # Response is for trial (current_trial - 1) compared to (current_trial - 1 - n_value)
        trial_index_to_check = self.current_trial - 1
        n_back_trial_index = trial_index_to_check - self.n_value

        actual_visual_match = (self.visual_sequence[trial_index_to_check] == self.visual_sequence[n_back_trial_index])
        actual_audio_match = (self.audio_sequence[trial_index_to_check] == self.audio_sequence[n_back_trial_index])
        
        user_visual_said_match = self.user_visual_responses[-1]
        user_audio_said_match = self.user_audio_responses[-1]

        if user_visual_said_match == actual_visual_match:
            self.score += 1
        if user_audio_said_match == actual_audio_match:
            self.score += 1
            
    def get_current_stimuli(self):
        """Returns the stimuli for the current trial without advancing."""
        if 0 <= self.current_trial < self.sequence_length:
            return self.visual_sequence[self.current_trial], self.audio_sequence[self.current_trial]
        return None, None

    def is_game_over(self):
        """Checks if the game has ended."""
        return self.current_trial >= self.sequence_length

    def get_score(self):
        """Returns the current score."""
        # Max possible score is 2 points per checkable trial.
        # Checkable trials start after N trials, so sequence_length - N trials are checkable.
        return self.score

# Example Usage (for testing the logic):
if __name__ == "__main__":
    game = NBackGame(n_value=2, sequence_length=10, num_positions=9, num_audio_stimuli=8)
    game.generate_sequences()
    print(f"Visual Sequence: {game.visual_sequence}")
    print(f"Audio Sequence:  {game.audio_sequence}")

    while not game.is_game_over():
        current_visual, current_audio = game.next_trial()
        if current_visual is None: # Game ended
            break
        
        print(f"Trial {game.current_trial}: Visual={current_visual}, Audio={current_audio}")

        # Simulate user input after N trials
        if game.current_trial > game.n_value:
            # For this example, let's simulate some random responses
            # In a real game, this would come from user UI interaction
            user_thinks_visual_matches = random.choice([True, False])
            user_thinks_audio_matches = random.choice([True, False])
            
            print(f"  User response: Visual match? {user_thinks_visual_matches}, Audio match? {user_thinks_audio_matches}")
            game.record_response(user_thinks_visual_matches, user_thinks_audio_matches)
            print(f"  Current Score: {game.get_score()}")
        else:
            print("  (Observing first N trials)")

    print(f"Game Over! Final Score: {game.get_score()}")

