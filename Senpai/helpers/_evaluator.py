

class Evaluator:
    GREEN = "🟩"
    YELLOW = "🟨"
    RED = "🟥"

    def evaluate_guess(self, guess: str, answer: str) -> str:
        guess = guess.lower()
        answer = answer.lower()

        if len(guess) != len(answer):
            raise ValueError("Guess and answer must be the same length")

        length = len(answer)
        result = [self.RED] * length
        answer_letters = list(answer)

        for i in range(length):
            if guess[i] == answer_letters[i]:
                result[i] = self.GREEN
                answer_letters[i] = None

        for i in range(length):
            if result[i] == self.GREEN:
                continue
            if guess[i] in answer_letters:
                result[i] = self.YELLOW
                answer_letters[answer_letters.index(guess[i])] = None

        return "".join(result)

    def is_winning_pattern(self, pattern: str, length: int) -> bool:
        return pattern == self.GREEN * length

evaluator = Evaluator()
