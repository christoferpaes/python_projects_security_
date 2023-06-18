import plotly.graph_objects as go

class LinearCongruentialGenerator:
    def __init__(self, seed, a, c, m):
        self.seed = seed
        self.a = a
        self.c = c
        self.m = m

    def generate(self, count):
        numbers = []
        xn = self.seed
        for i in range(count):
            # Print step-by-step calculation
            print(f"Iteration {i+1}: X{i} = (a * X{i-1} + c) mod m")
            print(f"             = ({self.a} * {xn} + {self.c}) mod {self.m}")

            xn = (self.a * xn + self.c) % self.m
            numbers.append(xn)

            # Print the generated number
            print(f"   => X{i+1} = {xn}\n")

        return numbers


# Example usage
seed = 1
a = 1
c = 1
m = 2**31 - 1

lcg = LinearCongruentialGenerator(seed, a, c, m)
random_numbers = lcg.generate(10)

# Plot the random numbers
x = list(range(1, len(random_numbers) + 1))
y = random_numbers

fig = go.Figure(data=go.Scatter(x=x, y=y, mode='markers+lines'))
fig.update_layout(title='Linear Congruential Generator', xaxis_title='Iteration', yaxis_title='Random Number')
fig.show()
