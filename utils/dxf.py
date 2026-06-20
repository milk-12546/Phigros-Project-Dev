def d2f(value, d = 1048576):
    return round(value * d)

def f2d(value, r = 15, d = 1048576):
    return round(value / d, r)