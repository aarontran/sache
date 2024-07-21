README
======

"sache" is a Python tool to help create and load cached NPZ files in scientific
workflows, particularly intended for use with scientific computing.


Usage - summary
---------------

1. Copy `sache.py` into some project folder of your choice.

2. Create a `cache_XXX.py` schema file in the same folder, to specify what
   calculation to perform, and where to save the cache files.

3. Make your cache files, overwriting any that already exist, in parallel using
   Python's multiprocessing library:

        $ sache.py cache_XXX.py -n 16

4. Get help / see other ways to refresh cache:

        $ sache.py --help

5. Load the cached data into Python, with struct-like access:

        $ python
        >>> import cache_bprojectv
        >>> dat = cache_bprojectv.Sachet(runid=..., particle..., step=...)
        >>> print(dat.u_prll)

6. Edit the `cache_XXX.py` and refresh your cache as your scientific workflow
   evolves, and you figure out what cache files you need or can discard, or as
   you figure out your cached data calculation needs to be changed...

7. Cache deletion/invalidation is manual.  Use `rm` or whatever you like.

8. Return to doing science instead of writing glue code for data caching.

That's it!


Usage - walkthrough example
---------------------------

Suppose you have simulation data of particles with positions and velocities.
You wish to interpolate the magnetic field on a Cartesian mesh to each
particle's position, compute the field-parallel and perpendicular velocity
components, and save the projected components to disk.

1. Code up your calculation.  In the example,

        $ cd examples/
        $ vim bprojectv.py          # code up your calculation

2. Specify where you want to save the cached data, how it should be named,
   and any other code needed to "make" your cache given a set of keyword
   arguments.

        $ cd examples/
        $ vim cache_bprojectv.py
        $ mkdir dat_bprojectv/      # cache store directory

   In this example, the calculation is separate from the cache schema, which
   helps enable use in Jupyter notebooks and elsewhere.
   But you could also merge `bprojectv.py` and `cache_bprojectv.py` together.

3. Partial cache refresh, don't modify old files:

        $ sache.py examples/cache_bprojectv.py

4. Full cache refresh, clobber old files:

        $ sache.py examples/cache_bprojectv.py --clobber

5. You can refresh the cache in parallel:

        $ sache.py examples/cache_bprojectv.py -n 16

7. To load cached data into Python, with struct-like access:

        $ python
        >>> import cache_bprojectv
        >>> dat = cache_bprojectv.Sachet(runid=..., particle..., step=...)
        >>> print(dat.u_prll)

You can also access the npz file directly via the numpy interface.

Notice also the suggested name scheme.
The file name `cache_...py` is meant to be self evident to a first-time code
reader who has never seen `sache.py` before (or, the original code author two
years later after they forgot about the existence of `sache.py`).
We want the reader to quickly see just from file browsing that the code has
dependency structure, even without the presence of a Makefile.
