
"""Various calculations specific to GPR data processing"""

def ns2mm(time, velocity):
    """Return the distance (mm) from signal travel time (ns) and velocity (m/ns).
        Attributes:
            time <float>: travel time (ns) of radio signal;
            velocity <float>: travel velocity (m/ns) of radio signal.
    """
    meters = velocity * time
    distance = meters * 1000
    return(distance)

def mm2ns(distance, velocity):
    """Return the time (ns) from distance (mm) and signal velcity (m/ns).
        Attributes:
            distance <float>: travel distance (ns) of radio signal;
            velocity <float>: travel velocity (m/ns) of radio signal.
    """
    d, v = distance / 1000, velocity
    time = d / v
    return(time)

def distance(step, traces, precision=7):
    """Calculate the x (distance) values of a GPR line.
        Attributes:
            step <float>: distance (m) between traces;
            traces <int>: number of traces in radargram;
            precision <int>: required output precision set to MALA default.
    """
    distances = [round(i * step, 7) for i in range(traces)]
    return(distances)

def time(frequency, samples, precision=6):
    """Calculate the y (time) values of a GPR line.
        Attributes:
            frequency <float>: frequency of traces;
            samples <int>: number of samples in each trace;
            precision <int>: required output precision set to MALA default.
    """
    interval = 1 / frequency * 1000
    times = [round(i * interval, precision) for i in range(1, samples + 1)]
    return(times)


