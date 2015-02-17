# rituals

Common tasks for [Invoke](http://www.pyinvoke.org/) that are needed again and again.

![GPL v2 licensed](http://img.shields.io/badge/license-GPL_v2-red.svg)


## Usage

Add `rituals` to you `dev-requirements.txt` or a similar file,
or add it to `setup_requires` in your `setup.py`.
Then at the start of your `tasks.py`, use the following statement to define _all_ tasks that are considered standard:

```py
from rituals.invoke import *
```

Of course, you can also do more selective imports, or remove specific tasks from the standard set via `del`.

To refer to the current GitHub ``master`` branch, use a ``pip`` requirement like this:

```
-e git+https://github.com/jhermann/rituals.git#egg=rituals
```


## Contributing

To create a working directory for this project, call these commands:

```sh
git clone https://github.com/jhermann/rituals.git
cd rituals; deactivate; /usr/bin/virtualenv .; . ./bin/activate
./bin/pip install -U pip; ./bin/pip install -r dev-requirements.txt
invoke build --docs
```

To use the source in this working directory within another project,
first activate that project's virtualenv.
Then change your current directory to _this_ project,
and either call ``pip install -e .`` or ``python setup.py develop -U``.

See [CONTRIBUTING.md](https://github.com/jhermann/rituals/blob/master/CONTRIBUTING.md) for more.
