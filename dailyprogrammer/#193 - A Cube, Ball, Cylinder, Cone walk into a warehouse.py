def get_shapes(v):
    print("Cube: Side length = " + str(round(v ** (1 / 3), 3)) + " m.")
    print("Ball: Radius = " + str(round((v / ((4 / 3) * 3.1415)) ** (1 / 3), 3)) + " m.")
    print("Cylinder: Height = 3 m, Diameter = " + str(round((v / (3 * 3.1415)) ** (1 / 2) * 2, 3)) + " m.")


get_shapes(27)
