import math
import time

# This library has some useful equations and conversions for planet characteristics

import math

def solve_kepler(M, e, tol=1e-10, max_iter=100):
    """
    Solve Kepler's equation:
    M = E - e*sin(E)

    Returns eccentric anomaly E
    """
    E = M if e < 0.8 else math.pi

    for _ in range(max_iter):
        f = E - e * math.sin(E) - M
        f_prime = 1 - e * math.cos(E)

        delta = f / f_prime
        E -= delta

        if abs(delta) < tol:
            break

    return E

def time_to_jd():
    """
    Convert Unix timestamp to Julian Date.
    
    Parameters:
    t : float
        Seconds since Unix epoch (Jan 1, 1970). If None, uses current time.
    
    Returns:
    jd : float
        Julian Date
    """

    t = time.time()
    
    # Number of days since Unix epoch
    days_since_epoch = t / 86400.0  # 86400 seconds in a day

    # Julian Date of Unix epoch = 2440587.5
    jd = 2440587.5 + days_since_epoch

    return jd

def orbitalCalc(
    jd,
    jd_epoch,
    a,
    e,
    i,
    Omega,
    omega,
    M0,
    period
):
    """
    Compute x,y,z position in ecliptic coordinates.

    Inputs:
    jd        : current Julian date
    jd_epoch  : epoch of orbital elements
    a         : semi-major axis
    e         : eccentricity
    i         : inclination (radians)
    Omega     : longitude of ascending node (radians)
    omega     : argument of periapsis (radians)
    M0        : mean anomaly at epoch (radians)
    period    : orbital period (days)
    """

    i = math.radians(i)
    Omega = math.radians(Omega)
    omega = math.radians(omega)
    M0 = math.radians(M0)

    # Time since epoch
    t = jd - jd_epoch

    # Mean motion
    n = 2 * math.pi / period

    # Mean anomaly
    M = M0 + n * t
    M = M % (2 * math.pi)

    # Solve Kepler equation
    E = solve_kepler(M, e)

    # True anomaly
    nu = 2 * math.atan2(
        math.sqrt(1 + e) * math.sin(E / 2),
        math.sqrt(1 - e) * math.cos(E / 2)
    )

    # Distance
    r = a * (1 - e * math.cos(E))

    # Precompute
    theta = omega + nu

    cos_O = math.cos(Omega)
    sin_O = math.sin(Omega)
    cos_i = math.cos(i)
    sin_i = math.sin(i)
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)

    # Convert to ecliptic xyz
    x = r * (cos_O * cos_t - sin_O * sin_t * cos_i)
    y = r * (sin_O * cos_t + cos_O * sin_t * cos_i)
    z = r * (sin_t * sin_i)

    coords = [x,y,z]
    return coords


def rotationalCalc(jd, jd_epoch, rot_period, W0):
    """
    Compute rotation angle around Z axis.

    rot_period : rotation period in days
    W0         : rotation angle at epoch (radians)
    """

    math.radians(W0)
    
    t = jd - jd_epoch

    Wdot = 2 * math.pi / rot_period

    W = W0 + Wdot * t

    return math.degrees(W % (2 * math.pi))

def currentJulian(current):
    return current / 86400.0 + 2440587.5

def kmToUnits(km, scale):
    return (km*6.68459e-9*scale)

def unitsToKm(units, scale):
    return (units/(6.68459e-9*scale))

def rotationalCalc(meridian, rot_period, epoch, jd):
    return ((meridian+8640*((jd - epoch)/rot_period))%360)
