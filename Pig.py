import random
import argparse
import time

random.seed(0)

class Player:
    """Represent a player in the Pig game."""

    def __init__(self, name):
        self.name = name
        self.score = 0

    def add_points(self, points):
        """Add points to the player's total score."""
        self.score += points

    def reset_score(self):
        """Reset the player's score for a new game."""
        self.score = 0

    def decide(self, turn_total):
        """Return 'r' (roll) or 'h' (hold). Subclasses must implement."""
        raise NotImplementedError("Subclasses must implement decide().")

class HumanPlayer(Player):
    """A player who decides using keyboard input."""

    def decide(self, turn_total):
        while True:
            decision = input(
                "\nRoll or hold? (r/h): "
            ).lower().strip()

            if decision in ("r", "h"):
                return decision

            print("Invalid choice. Please enter 'r' or 'h'.")

class ComputerPlayer(Player):
    """A player that holds at the lesser of 25 and (100 - score)."""

    def decide(self, turn_total):
        if turn_total >= min(25, 100 - self.score):
            print(f"\n{self.name} (computer) chooses to hold.")
            return "h"

        print(f"\n{self.name} (computer) chooses to roll.")
        return "r"

class PlayerFactory:
    """Create a human or computer player."""

    @staticmethod
    def create_player(player_type, name):
        if player_type == "human":
            return HumanPlayer(name)
        elif player_type == "computer":
            return ComputerPlayer(name)
        raise ValueError(f"Unknown player type: {player_type}")

class Die:
    """Represent a six-sided die."""

    def roll(self):
        """Return a random number from 1 to 6."""
        return random.randint(1, 6)

class PigGame:
    """Manage the Pig game for human and computer players."""

    def __init__(self, player_types):
        self.num_players = len(player_types)
        self.players = []

        # Create the players using the factory.
        for number, player_type in enumerate(player_types, start=1):
            player = PlayerFactory.create_player(
                player_type, f"Player {number}"
            )
            self.players.append(player)

        self.die = Die()
        self.current_player_index = 0
        self.winning_score = 100

    def rules_text(self):
        """Describe how the game is won."""
        return "The first player to reach 100 points wins."

    def time_is_up(self):
        """Never true for a normal game; TimedGameProxy replaces this."""
        return False

    def switch_player(self):
        """Move to the next player."""
        self.current_player_index = (
            self.current_player_index + 1
        ) % self.num_players

    def reset_game(self):
        """Reset all scores and game state for a new game."""
        for player in self.players:
            player.reset_score()

        self.current_player_index = 0

    def play(self):
        """Play until one player reaches 100 points."""

        print("\nWelcome to the Pig Game!")
        print(f"Number of players: {self.num_players}")
        print(self.rules_text())
        print("Enter 'r' to roll or 'h' to hold.")

        while True:
            player = self.players[self.current_player_index]
            turn_total = 0

            print(f"\n--- {player.name}'s turn ---")

            while True:
                # Stop immediately if the timed proxy says time is up.
                if self.time_is_up():
                    return

                # Display the current scores before the decision.
                print(f"Current score for this turn so far: {turn_total} "
                      f"| Total game score: {player.score}")

                decision = player.decide(turn_total)

                if decision == "r":
                    roll = self.die.roll()
                    print(f"{player.name} rolled: {roll}")

                    if roll == 1:
                        print("You rolled a 1! Your turn total is lost.")
                        print(f"Your score remains {player.score}.")
                        break

                    turn_total += roll

                elif decision == "h":
                    player.add_points(turn_total)

                    print(f"{player.name} holds.")
                    print(f"Points earned this turn: {turn_total} | New total game score: {player.score}")

                    break

            # Check whether the current player has won.
            if player.score >= self.winning_score:
                print("\nGame over!")
                print(f"{player.name} wins!")
                print(f"Final score: {player.score}")

                # Display every player's final score.
                print("\nFinal scores:")
                for current_player in self.players:
                    print(
                        f"{current_player.name}: "
                        f"{current_player.score}"
                    )

                return

            self.switch_player()

class TimedGameProxy(PigGame):
    """Proxy for PigGame that ends the game after one minute."""

    TIME_LIMIT = 60  # seconds

    def __init__(self, player_types):
        super().__init__(player_types)
        self.start_time = None

    def rules_text(self):
        return (f"The first player to reach 100 points wins. If nobody "
                f"gets there in {self.TIME_LIMIT} seconds, the player "
                f"with the most points wins.")

    def time_is_up(self):
        return (self.start_time is not None
                and time.time() - self.start_time >= self.TIME_LIMIT)

    def play(self):
        """Play the game, stopping when someone wins or time runs out."""
        self.start_time = time.time()
        super().play()

        # If the game stopped without a winner, time ran out.
        best = max(player.score for player in self.players)
        if best < self.winning_score:
            leaders = [p for p in self.players if p.score == best]

            print("\nTime is up! One minute has elapsed.")
            print("\nGame over!")
            if len(leaders) == 1:
                print(f"{leaders[0].name} wins with the most points!")
            else:
                print("The game ends in a tie!")

            print("\nFinal scores:")
            for current_player in self.players:
                print(f"{current_player.name}: {current_player.score}")

def main():
    """Read command-line arguments and manage multiple games."""

    parser = argparse.ArgumentParser(
        description="Play the Pig dice game."
    )

    parser.add_argument(
        "--player1",
        choices=["human", "computer"],
        default="human",
        help="Type of player 1 (default: human)"
    )

    parser.add_argument(
        "--player2",
        choices=["human", "computer"],
        default="human",
        help="Type of player 2 (default: human)"
    )

    parser.add_argument(
        "--timed",
        action="store_true",
        help="Play a timed game (one minute limit)"
    )

    args = parser.parse_args()

    # Create the game with the requested player types.
    player_types = [args.player1, args.player2]

    if args.timed:
        game = TimedGameProxy(player_types)
    else:
        game = PigGame(player_types)

    while True:
        game.play()

        # Ask whether the players want to start another game.
        while True:
            answer = input(
                "\nWould you like to play another game? (y/n): "
            ).lower().strip()

            if answer == "y":
                game.reset_game()
                print("\nStarting a new game. All scores are reset.")
                break

            elif answer == "n":
                print("Thanks for playing Pig!")
                return

            else:
                print("Invalid choice. Please enter 'y' or 'n'.")

if __name__ == "__main__":
    main()
