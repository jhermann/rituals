# -*- coding: utf-8 -*-
# pylint: disable=wildcard-import, unused-wildcard-import, unused-import, bad-continuation
""" Project automation for Invoke.
"""

from invoke import run, task
from rituals.invoke_tasks import * # pylint: disable=redefined-builtin


@task(pre=[
    inv('clean', all=True),
    inv('build', docs=True),
    inv('test'),
    inv('check', reports=True),
]) # pylint: disable=invalid-name
def ci():
    """Perform continuous integration tasks."""
