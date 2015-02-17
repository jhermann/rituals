# rituals

Common tasks for [Invoke](http://www.pyinvoke.org/) that are needed again and again.


## Usage

Add `rituals` to you `dev-requirements.txt` or a similar file,
or add it to `setup_requires` in your `setup.py`.
Then at the start of your `tasks.py`, use the following statement to define _all_ tasks that are considered standard:

```py
from rituals.tasks import *
```

Of course, you can also do more selective imports, or remove specific tasks from the standard set via `del`.


## Contributing

To create a working directory for this project, call these commands:

… **TODO**

See CONTRIBUTING.md for more.
