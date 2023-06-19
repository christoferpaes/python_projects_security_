import random
import os

class SystemRandom(random.Random):
    """Class representing a cryptographically secure random number generator."""

    def random(self):
        """Return the next random floating-point number in the range [0.0, 1.0)."""
        return os.urandom(4) / 0xffffffff

    def randint(self, a, b):
        """Return a random integer N such that a <= N <= b."""
        return a + int((b - a + 1) * self.random())

    def choice(self, seq):
        """Return a random element from the non-empty sequence seq."""
        if not seq:
            raise IndexError("Cannot choose from an empty sequence.")
        return seq[self.randint(0, len(seq) - 1)]

    def shuffle(self, seq):
        """Shuffle the sequence seq in place."""
        if len(seq) <= 1:
            return
        for i in range(len(seq) - 1, 0, -1):
            j = self.randint(0, i)
            seq[i], seq[j] = seq[j], seq[i]

# Example usage
sr = SystemRandom()

# Generate a random floating-point number
print(sr.random())

# Generate a random integer
print(sr.randint(1, 10))

# Choose a random element from a sequence
sequence = [1, 2, 3, 4, 5]
print(sr.choice(sequence))

# Shuffle a sequence
sequence = [1, 2, 3, 4, 5]
sr.shuffle(sequence)
print(sequence)
