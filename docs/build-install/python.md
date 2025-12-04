[](){#ref-python}
# Installing Python software

There is no one-size-fits-all approach to installing Python environments, for example pip, uv and Conda can all be used.
Furthermore, environments can be installed on top of uenv, in containers, or bare metal for the brave.

[](){#ref-python-uenv}
## uenv

Uenv provide a base for installing Python software, by using the Python interpretter, compilers, MPI and Python packages provided by the uenv.

[](){#ref-python-uenv-venv}
## Installing venv on top of a uenv view

When stacking a Python virtual environment on top of a _uenv view_, keep Python’s import resolution predictable with the following:

- **Unset `PYTHONPATH`**. Anything there is *prepended* to Python's `sys.path`, which can lead to surprising imports.
- **Set `PYTHONUSERBASE` to the view's root directory** (e.g., `/user-environment/env/default`) so the interpreter’s _user site_ resolves inside the view.
    - You can derive this automatically from the interpreter you’re about to use: take the parent of `which python`:
      ```bash
      export PYTHONUSERBASE=$(dirname $(dirname $(which python)))
      ```
    - Do not use tools that resolve symlinks (such as `readlink -f` or Python's `Path.resolve()`), as the Python interpreter in the _uenv view_ is a symlink - following it would point outside the view.
- **Create the venv with `--system-site-packages`**.
`venv` disables the user site by default; enabling system site restores both the system site and the user site, so packages provided by the _uenv view_ become visible inside the venv.
=== "uv"
    ```console title="Creating a Python virtual environment on top of a uenv view"
    # start the uenv with the default view
    $ uenv start --view=default prgenv-gnu/25.6:v2
    # unset PYTHONPATH to avoid surprises
    $ unset PYTHONPATH
    # set PYTHONUSERBASE to the root of the view
    $ export PYTHONUSERBASE="$(dirname "$(dirname "$(which python)")")"
    # create the virtual environment with access to system site packages
    # - optionally seed it with pip, setuptools and wheel
    # - optionally make it relocatable and copy linked files (useful for moving venvs)
    $ uv venv --python $(which python) --system-site-packages --seed --relocatable --link-mode=copy path/to/my-venv
    # activate the virtual environment
    $ source path/to/my-venv/bin/activate
    # verify that packages from the uenv are visible (note Locations)
    (my-venv) $ python -m pip list -v
    Package Version Location                                                   Installer
    ------- ------- ---------------------------------------------------------- ---------
    meson   1.7.0   /user-environment/env/default/lib/python3.13/site-packages pip
    pip     25.3    /path/to/my-venv/lib/python3.13/site-packages              uv
    # upgrade a package into the venv (overrides the view's version)
    (my-venv) $ uv pip install --upgrade meson

    # verify that the upgraded package is now coming from the venv
    (my-venv) $ python -m pip list -v
    Package Version Location                                         Installer
    ------- ------- ------------------------------------------------ ---------
    meson   1.9.1   /path/to/my-venv-uv/lib/python3.13/site-packages uv
    pip     25.3    /path/to/my-venv-uv/lib/python3.13/site-packages uv
    ```

=== "venv"

    ```console title="Creating a Python virtual environment on top of a uenv view"
    # start the uenv with the default view
    $ uenv start --view=default prgenv-gnu/25.6:v2
    # unset PYTHONPATH to avoid surprises
    $ unset PYTHONPATH
    # set PYTHONUSERBASE to the root of the view
    $ export PYTHONUSERBASE="$(dirname "$(dirname "$(which python)")")"
    # create the virtual environment with access to system site packages
    $ python -m venv --system-site-packages path/to/my-venv
    # activate the virtual environment
    $ source path/to/my-venv/bin/activate
    # verify that packages from the uenv are visible (note Locations)
    (my-venv) $ python -m pip list -v
    python -m pip list -v
    Package Version Location                                                   Installer
    ------- ------- ---------------------------------------------------------- ---------
    meson   1.7.0   /user-environment/env/default/lib/python3.13/site-packages pip
    pip     25.1.1  /path/to/my-venv/lib/python3.13/site-packages              pip
    # upgrade a package into the venv (overrides the view's version)
    (my-venv) $ pip install --upgrade meson
    # verify that the upgraded package is now coming from the venv
    (my-venv) $ pip list
    Package Version Location                                      Installer
    ------- ------- --------------------------------------------- ---------
    meson   1.9.1   /path/to/my-venv/lib/python3.13/site-packages pip
    pip     25.1.1  /path/to/my-venv/lib/python3.13/site-packages pip
    ```

!!! note "Listing only the packages that live in the uenv’s user-site"
    To see _just_ what's in the uenv view (not what's installed into the venv), list by the user-site path that your interpreter is using:
    ```console
    (my-venv) $ python -m pip list -v --path "$(python -c 'import site; print(site.getusersitepackages())')"
    ```

!!! note "Troubleshooting"
    - `pip install --user` will fail here.
    The uenv is a read-only squashfs; a `--user` install would try to write into `PYTHONUSERBASE` (the uenv), which is not possible.
    - Some uenv views already set `PYTHONUSERBASE`. If you start a uenv view that does this, you can skip setting `PYTHONUSERBASE` yourself.
    - The virtual environment is _specific_ to a particular uenv and won't work unless used from inside this exact uenv - it relies on the resources packaged inside the uenv.
!!! note "Performance considerations"
    On our Lustre parallel file system, large virtual environments can be slow due to many small files.
    See [How to squash virtual environments][ref-guides-storage-venv] for turning a venv into a compact image to improve startup and import performance.
