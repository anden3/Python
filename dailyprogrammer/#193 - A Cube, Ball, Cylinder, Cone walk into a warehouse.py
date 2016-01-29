from cmath import pi


def get_shapes(v):
    print("Cube: Side length = " + str(round(v ** (1 / 3), 3)) + " m.")
    print("Ball: Radius = " + str(round((v / ((4 / 3) * pi)) ** (1 / 3), 3)) + " m.")
    print("Cylinder: Height = 3 m, Diameter = " + str(round((v / (3 * pi)) ** (1 / 2) * 2, 3)) + " m.")
    print("Cone: Height = 3 m, Radius = " + str(round((3 * (v / (pi * 3))) ** 0.5, 3)) + " m.")


get_shapes(2197)
