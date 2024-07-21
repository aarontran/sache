#!/usr/bin/env python
"""
Project particle velocity data into B-field aligned coordinates
"""

from __future__ import division, print_function

import numpy as np
import scipy as sp


def bprojectv(xv, yv, zv, flds, prtl, **kwargs):
    """
    Project particle velocities into B-field aligned coordinates.

    Inputs:
        xy, yv, zv = 1D vectors of shape (nx,), (ny,), (nz,) respectively that
                     hold Cartesian coordinate mesh positions
        r = user-created wrapper around a simulation run HybridVPICRun(...)
        flds = dict with 'b' key, where flds['b'] has shape (3,nx,ny,nz) with
               specifying B-field components and simulation coordinate mesh
        prtl = dict with keys 'x', 'y', 'z', 'ux', 'uy', 'uz' labeling
               particle positions and velocities within simulation domain
        **kwargs = passed to scipy.interpolate.RegularGridInterpolator(...)
    """
    # quantities at particles locations, NOT flds on mesh
    bx_interp = sp.interpolate.RegularGridInterpolator((xv,yv,zv), flds['b'][0], **kwargs)
    by_interp = sp.interpolate.RegularGridInterpolator((xv,yv,zv), flds['b'][1], **kwargs)
    bz_interp = sp.interpolate.RegularGridInterpolator((xv,yv,zv), flds['b'][2], **kwargs)

    # RegularGridInterpolator requires this particular coordinate shape
    ppos = np.array([ prtl['x'], prtl['y'], prtl['z'] ]).T
    bx = bx_interp( ppos )
    by = by_interp( ppos )
    bz = bz_interp( ppos )
    b = np.array([bx,by,bz])

    u = np.array([ prtl['ux'], prtl['uy'], prtl['uz'] ])

    bmag = np.sum(b**2,axis=0)**0.5
    bhat = b / bmag

    # v_\parallel = \vec{v}\cdot\vec{B} / |\vec{B}| = \vec{v}\cdot\hat{b}
    # \vec{v}_\perp = \vec{v} - (\vec{v}\cdot\hat{b}) \hat{b}
    u_prll = np.sum(u*bhat, axis=0)  # a signed quantity
    u_perp = u - u_prll * bhat

    out = dict(
        u_prll = u_prll,
        u_perp = u_perp,
    )

    return out
