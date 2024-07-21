#!/usr/bin/env python

from sache import Sache

# ----------------------------------------
# sache schema: declare what data to cache
# ----------------------------------------

class Sachet(Sache):

    STORE = "./dat"

    FNAME_TEMPLATE = "{runid:s}_{species:s}_n{step:06d}.npz"

    @classmethod
    def _make(cls, **kwargs):
        # required input: **kwargs same as FNAME_TEMPLATE below
        # required output: dict of numpy arrays

        runid = kwargs['runid']
        species = kwargs['species']
        step = kwargs['step']

        # xv = ... YOUR CODE HERE
        # yv = ... YOUR CODE HERE
        # zv = ... YOUR CODE HERE
        # flds = ... YOUR CODE HERE
        # prtl = ... YOUR CODE HERE

        out = bprojectv(xv, yv, zv, flds, prtl, verbose=True,
                        bounds_error=False, fill_value=np.nan)
        return out

# ------------------------------------------------------------
# sache schema: declare all the cache files you want to create
# ------------------------------------------------------------

REQUESTS = [
    dict(runid="your.latest.simulation.run", species='ion', step=0),
    dict(runid="your.latest.simulation.run", species='ion', step=100),
    # ... et cetera
]

# -------------------------
# sache schema: boilerplate
# -------------------------

if __name__ == '___main__':
    raise Exception("Error: use sache.py for command-line interface")
