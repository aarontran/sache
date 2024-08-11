#!/usr/bin/env python

from __future__ import division, print_function

import argparse
from datetime import datetime
import importlib
import itertools
from multiprocessing import Pool
import numpy as np
import os
import psutil
import sys

from myutil import printmem, starstarmap


class Sache(object):
    # This parent class assumes the presence of class variables that are only
    # provided by the child class, so the Sache might be called a metaclass or
    # abstract class, even though we aren't using any of Python's metaclass
    # functionality.  I'm not sure if this scheme is the most concise or
    # understandable way to implement the desired UI, but it seems to work.

    def __init__(self, **kwargs):
        """Load a Sachet from disk"""
        if os.path.exists(self._resolve_filename(**kwargs)):
            return self._load(**kwargs)
        return None

    def _load(self, **kwargs):
        fname = self._resolve_filename(**kwargs)
        dat = np.load(fname)
        for k in dat:
            # setattr(...) dynamically injects code, could be dangerous.
            # If keys overwrite the class instance's methods, that's OK because
            # once _load(..) is done, the user treats this object as a struct,
            # and the user likely won't use any object methods.
            setattr(self, k, dat[k])

    @classmethod
    def _resolve_filename(cls, **kwargs):
        return os.path.join(cls.STORE, cls.FNAME_TEMPLATE.format(**kwargs))

    @classmethod
    def _refresh(cls, compress=False, clobber=False, dry_run=False, **kwargs):
        """Wrapper script for multiprocessing, must declare at module level"""
        started = datetime.now()

        fname = cls._resolve_filename(**kwargs)

        if os.path.exists(fname) and not clobber:
            print("Skipping, will not clobber", fname)
            return
        if dry_run:
            print("(dry run) Would create", fname)
            return

        print("Creating", fname)

        out = cls._make(**kwargs)
        if compress:
            np.savez_compressed(fname, **out)
        else:
            np.savez(fname, **out)

        print("Done", fname, "elapsed", datetime.now()-started)


# -----------------------------------------------------------------------------
# Utility routines
# -----------------------------------------------------------------------------

def printmem(pid=False):
    mem = psutil.Process(os.getpid()).memory_info().rss
    if pid:
        print("PID", os.getpid(), "memory usage", mem/1e6, "MB")
    else:
        print("Memory usage", mem/1e6, "MB")


def starstarmap(pool, fn, kwargs_iter):
    """
    Like multiprocessing.Pool.starmap(...), but for iterables of keyword
    arguments.  Nifty hack from:
    https://stackoverflow.com/questions/45718523/pass-kwargs-to-starmap-while-using-pool-in-python
    Inputs:
        pool = multiprocessing.Pool instance
        fn = function
        kwargs_iter = iterable of keyword arguments
    """
    fn_kwargs_iter = zip(itertools.repeat(fn), kwargs_iter)
    return pool.starmap(_apply_kwargs, fn_kwargs_iter)


def _apply_kwargs(fn, kwargs):
    """
    Helper function for starstarmap. Must be defined at module level for
    multiprocessing.Pool(...) to serialize.
    """
    return fn(**kwargs)


# -----------------------------------------------------------------------------
# Command line interface
# -----------------------------------------------------------------------------
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="""
Create cached npz files in scientific workflows.  Input is the name of a Python
module exposing global variables: Sachet, REQUESTS."""
    )
    parser.add_argument("module", help="Python module specifying what caches to create")
    parser.add_argument('--clobber', action='store_true',
                        help="Overwrite existing files on disk")
    parser.add_argument('--dry-run', action='store_true',
                        help="Print file paths to write but do no computation")
    parser.add_argument('--compress', action='store_true',
                        help="Apply compression when saving files")
    parser.add_argument('-n', type=int, default=1,
                        help="Number of parallel workers for Python multiprocessing Pool")
    args = parser.parse_args()

    # allows sache.py to be placed anywhere w.r.t. cache schema, and vice versa
    sys.path.append(os.path.dirname(os.path.abspath(args.module)))

    # this pattern is https://en.wikipedia.org/wiki/Dependency_injection
    modulename = args.module
    if modulename[-3:] == ".py":
        modulename = modulename[:-3]
    module = importlib.import_module(modulename)

    if args.n <= 1:
        # serial version
        for req in module.REQUESTS:
            # avoid  __init__(...) because it reads from disk (which is slow)
            # @classmethod decorator enables the below syntax, idea is from
            # https://stackoverflow.com/a/6384175
            module.Sachet._refresh(compress=args.compress,
                                   clobber=args.clobber,
                                   dry_run=args.dry_run,
                                   **req)
    else:
        # parallel version
        nworkers = args.n
        print("Starting pool with nworkers=", nworkers)

        # not sure if copy is necessary instead of mutate in place
        # but I kind of think it's good practice for future extensibility
        # and code-reading overhead is minimal
        import copy
        requests = copy.deepcopy(module.REQUESTS)
        for x in requests:
            x['compress'] = args.compress
            x['clobber'] = args.clobber
            x['dry_run'] = args.dry_run

        with Pool(nworkers, maxtasksperchild=1) as p:
            #p.starmap(make, requests, chunksize=1)  # testing only
            starstarmap(p, module.Sachet._refresh, requests)
