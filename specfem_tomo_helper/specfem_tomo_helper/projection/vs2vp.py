#!/usr/bin/env python

def vs2vp(dvs):
    """ Math function definitions to convert vp to vs from Brocher T. 2005, https://doi.org/10.1785/0120050077

    Parameters
    ----------

    vp : float
        P-wave velocity (km/s)

    """
    if any(dvs) >= 15:
        raise AssertionError('vp values must be in km/s')
    vp = 0.9409 + 2.0947*dvs - 0.8206*dvs**2 + 0.2683*dvs**3 - 0.0251*dvs**4
    return vp
