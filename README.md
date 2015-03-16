# rituals

Common tasks for [Invoke](http://www.pyinvoke.org/) that are needed again and again.

![GINOSAJI](https://raw.githubusercontent.com/jhermann/rituals/master/static/img/symbol-200.png) … and again and again.

 [![Travis CI](https://api.travis-ci.org/jhermann/rituals.svg)](https://travis-ci.org/jhermann/rituals)
 [![GitHub Issues](https://img.shields.io/github/issues/jhermann/rituals.svg)](https://github.com/jhermann/rituals/issues)
 [![License](https://img.shields.io/pypi/l/rituals.svg)](https://github.com/jhermann/rituals/blob/master/LICENSE)
 [![Development Status](https://pypip.in/status/rituals/badge.svg)](https://pypi.python.org/pypi/rituals/)
 [![Latest Version](https://img.shields.io/pypi/v/rituals.svg)](https://pypi.python.org/pypi/rituals/)
 [![Download format](https://pypip.in/format/rituals/badge.svg)](https://pypi.python.org/pypi/rituals/)
 [![Downloads](https://img.shields.io/pypi/dw/rituals.svg)](https://pypi.python.org/pypi/rituals/)


## Common Tasks

The following lists the common task implementations that the ``invoke_tasks`` module contains.
See the next section on how to integrate them into your `tasks.py`.

* ``help`` –    Default task, when invoked with no task names.
* ``clean`` –   Perform house-cleaning.
* ``build`` –   Build the project.
* ``dist`` –    Distribute the project.
* ``test`` –    Perform standard unittests.
* ``check`` –   Perform source code checks.

The guiding principle for these tasks is to strictly separate
low-level tasks for building and installing (via ``setup.py``)
from high-level convenience tasks a developer uses (via ``invoke``).
Invoke tasks can use Setuptools ones as building blocks,
but never the other way 'round
– this removes any bootstrapping headaches during package installations.

Use ``inv -h ‹task›`` as usual to get details on the options of these tasks.
Look at the [invoke_tasks](https://github.com/jhermann/rituals/blob/master/src/rituals/invoke_tasks.py) source
if you want to know what these tasks do exactly.

:bulb: | The easiest way to get a working project using `rituals` is the [py-generic-project](https://github.com/Springerle/py-generic-project) cookiecutter archetype. That way you have a working project skeleton within minutes that is fully equipped, with all aspects of building, testing, quality checks, continuous integration, documentation, and releasing covered.
---- | :----


## Usage

### Add common tasks to your project's `task.py`

Add `rituals` to your `dev-requirements.txt` or a similar file,
or add it to `setup_requires` in your `setup.py`.
Then at the start of your `tasks.py`, use the following statement to define _all_ tasks that are considered standard:

```py
from rituals.invoke_tasks import *
```

Of course, you can also do more selective imports, or remove specific tasks from the standard set via `del`.

:warning: | These tasks expect an importable `setup.py` that defines a `project` dict with the setup parameters, see [javaprops](https://github.com/Feed-The-Web/javaprops) and [py-generic-project](https://github.com/Springerle/py-generic-project) for examples.
---- | :----

To refer to the current GitHub ``master`` branch, use a ``pip`` requirement like this:

```
-e git+https://github.com/jhermann/rituals.git#egg=rituals
```


### Change default project layout

By default, sources are expected in `src/‹packagename›` and tests in `src/tests`.

You can change this by calling one of the following functions, directly after the import from `rituals.invoke_tasks`.

* `config.set_maven_layout()` – Changes locations to `src/main/python/‹packagename›` and `src/test/python`.
* `config.set_flat_layout()` – Changes locations to `‹packagename›` and `tests`.


### Change default project configuration

**TODO**


## Contributing

To create a working directory for this project, call these commands:

```sh
git clone "https://github.com/jhermann/rituals.git"
cd rituals
. .env # answer the prompt with (y)es
invoke build --docs
```

To use the source in this working directory within another project,
change your current directory to _this_ project,
then call `bin/pip` from *that* project's virtualenv like so:

    …/.venv/…/bin/pip install -e .

See [CONTRIBUTING.md](https://github.com/jhermann/rituals/blob/master/CONTRIBUTING.md) for more.


## Releasing

This is the process of releasing  ``rituals`` itself,
projects that use it will have an identifcal to very similar sequence of commands.

```sh
inv release-prep
inv dist --devpi # local release + tox testing

# … and now also check Travis CI
twine dist/* # upload to PyPI
```


## Related Projects

* [Springerle/py-generic-project](https://github.com/Springerle/py-generic-project)
* [pyinvoke/invocations](https://github.com/pyinvoke/invocations) – A collection of reusable Invoke tasks and task modules.


## Acknowledgements

* Logo elements from [clker.com Free Clipart](http://www.clker.com/).
* In case you wonder about the logo, [watch this](http://youtu.be/9VDvgL58h_Y).
