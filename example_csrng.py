import random
import os
import plotly.graph_objects as go

class SystemRandom(random.Random):
    """Class representing a cryptographically secure random number generator."""

    def random(self, num_values):
        """Return a list of random floating-point numbers in the range [0.0, 1.0)."""
        random_bytes = os.urandom(4 * num_values)
        random_integers = [int.from_bytes(random_bytes[i:i+4], byteorder='big') for i in range(0, len(random_bytes), 4)]
        return [value / 0xffffffff for value in random_integers]

# Example usage
sr = SystemRandom()

num_values = 1000
random_values = sr.random(num_values)

# Plotting the random values
fig = go.Figure(data=go.Scatter(y=random_values, mode='markers'))
fig.update_layout(title="CSPRNG")

fig.show()
