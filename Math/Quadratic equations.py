from sympy import *

init_printing(use_latex=True)

'''
equation = input("What's the equation: ")
equation.translate({"^": "**"})
equation.translate({"+": " + "})
equation.translate({"-": " - "})

x_coefficients = re.findall(r'[123456789]x', equation)
coefficients = re.findall(r'(?:^|[^\^])[123456789]', equation)

for c in x_coefficients:
    replace = c[0] + "*x"
    equation = re.sub(c, replace, equation)

x = symbols("x")

expr = sympify(equation)
derivative = diff(expr, x)
roots = solve(Eq(expr), x)

print(expr)
print(derivative)
print(roots)
'''

x = symbols('x')

print(Integral(sqrt(1 / x)), x)
