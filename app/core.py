import random


class NBackGame:
    def __init__(self, n_value=2, sequence_length=20, num_positions=9, num_audio_stimuli=9):
        if not 1 <= n_value <= 9:  # Max N commonly up to 9, though 1-5 is typical for training
            raise ValueError("N-value must be between 1 and 9.")
        self.n_value = n_value
        self.sequence_length = sequence_length + n_value  # Ensure enough trials for N-back checks
        self.num_positions = num_positions  # For visual stimuli (e.g., 3x3 grid)
        self.num_audio_stimuli = num_audio_stimuli  # For audio stimuli (e.g., digits 1-9 or letters)

        self.visual_sequence = []
        self.audio_sequence = []

        self.current_trial_index = 0  # Index in the sequence
        self.score = 0

        self.user_visual_responses_history = []  # Stores user's visual match button presses for each trial
        self.user_audio_responses_history = []  # Stores user's audio match button presses for each trial

    def _generate_stimulus(self, num_options):
        """Generates a single stimulus (either visual position or audio sound)."""
        return random.randint(0, num_options - 1)

    def generate_sequences(self):
        """Generates both visual and audio sequences for the game."""
        self.visual_sequence = [self._generate_stimulus(self.num_positions) for _ in range(self.sequence_length)]
        self.audio_sequence = [self._generate_stimulus(self.num_audio_stimuli) for _ in range(self.sequence_length)]
        self.current_trial_index = 0
        self.score = 0
        self.user_visual_responses_history = []
        self.user_audio_responses_history = []

    def next_stimuli(self):
        """Advances to the next trial and returns the current stimuli."""
        if self.current_trial_index < self.sequence_length:
            visual_stimulus = self.visual_sequence[self.current_trial_index]
            audio_stimulus = self.audio_sequence[self.current_trial_index]
            self.current_trial_index += 1
            return visual_stimulus, audio_stimulus
        else:
            return None, None  # Game over

    def record_response_and_score(self, visual_match_pressed, audio_match_pressed):
        """Records the user's response for the *previous* stimulus presentation and scores it."""
        # This is called *before* presenting the next stimulus, or at the end of a response window.
        # The response is for the (current_trial_index - 1) stimulus compared to (current_trial_index - 1 - n_value)

        # Store raw button presses for the stimulus that was just shown
        # (current_trial_index has already advanced for the *next* stimulus to be shown)
        # So, the response is for trial_idx = self.current_trial_index - 1

        # We only score if enough trials have passed to make an N-back comparison
        if self.current_trial_index > self.n_value:
            # The stimulus just presented was at index: presented_stim_idx = self.current_trial_index - 1
            # The N-back stimulus to compare against was at index: n_back_stim_idx = presented_stim_idx - self.n_value
            presented_stim_idx = self.current_trial_index - 1
            n_back_stim_idx = presented_stim_idx - self.n_value

            actual_visual_match = (self.visual_sequence[presented_stim_idx] == self.visual_sequence[n_back_stim_idx])
            actual_audio_match = (self.audio_sequence[presented_stim_idx] == self.audio_sequence[n_back_stim_idx])

            if visual_match_pressed == actual_visual_match:
                self.score += 1
            if audio_match_pressed == actual_audio_match:
                self.score += 1

        # History for potential later analysis, not directly used by current scoring logic
        self.user_visual_responses_history.append(visual_match_pressed)
        self.user_audio_responses_history.append(audio_match_pressed)

    def get_current_trial_number(self):
        """Returns the 1-based current trial number being presented."""
        return self.current_trial_index

    def is_game_over(self):
        """Checks if the game has ended (all stimuli presented)."""
        # Game is over if current_trial_index reaches sequence_length
        return self.current_trial_index >= self.sequence_length

    def get_score(self):
        """Returns the current score."""
        return self.score

    def get_max_possible_score(self):
        """Calculates the maximum possible score for the current game settings."""
        # Scoring happens for trials from n_value up to sequence_length - 1
        # Number of scorable trials = sequence_length - n_value
        # Each scorable trial has two components (visual and audio)
        return (self.sequence_length - self.n_value) * 2


# Example Usage (for testing the logic):
if __name__ == "__main__":
    test_n_value = 2
    game = NBackGame(n_value=test_n_value, sequence_length=10, num_positions=9, num_audio_stimuli=8)
    game.generate_sequences()
    print(f"N-Value: {game.n_value}")
    print(f"Sequence Length (total stimuli): {game.sequence_length}")
    print(f"Visual Sequence: {game.visual_sequence}")
    print(f"Audio Sequence:  {game.audio_sequence}")
    print(f"Max possible score: {game.get_max_possible_score()}")

    while not game.is_game_over():
        # In a real game, user responses for the *previous* trial would be collected here
        # For this test, we'll simulate responses *after* getting new stimuli, then call record

        # Simulate user responses for the stimulus that was *just* shown (or would have been if this was UI)
        # This part is tricky in a pure logic test. In UI, response happens *after* stimulus is shown and *before* next.
        if game.get_current_trial_number() > 0:  # If at least one stimulus has been shown
            # Let's assume these are responses for the (game.current_trial_index -1) stimulus
            user_thinks_visual_matches = random.choice([True, False])
            user_thinks_audio_matches = random.choice([True, False])
            print(
                f"  Trial {game.get_current_trial_number()} (stimulus just shown) - User response: Visual? {user_thinks_visual_matches}, Audio? {user_thinks_audio_matches}")
            game.record_response_and_score(user_thinks_visual_matches, user_thinks_audio_matches)
            print(f"  Current Score: {game.get_score()}")

        current_visual, current_audio = game.next_stimuli()
        if current_visual is None:  # Game ended
            print("Next stimuli is None, game should be over.")
            break

        print(f"Presenting Trial {game.get_current_trial_number()}: Visual={current_visual}, Audio={current_audio}")

        if game.get_current_trial_number() <= game.n_value:
            print("  (Observing first N trials - no scoring yet for these specific stimuli)")

    # After the loop, one last scoring might be needed if the last stimulus was scorable
    # This depends on how the UI loop calls record_response_and_score
    # For this test, the last response was recorded inside the loop for the second to last stimulus.
    # If sequence_length is 10, and n=2, trials 3-10 are scorable (8 trials * 2 = 16 points)
    # current_trial_index goes from 0 to 9. next_stimuli() is called 10 times.
    # record_response_and_score is called when current_trial_index is 1 through 9 (for previous stimulus)

    print(f"Game Over! Final Score: {game.get_score()} / {game.get_max_possible_score()}")

