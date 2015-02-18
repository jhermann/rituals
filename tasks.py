# -*- coding: utf-8 -*-
# pylint: disable=wildcard-import, unused-wildcard-import, bad-continuation
""" Project automation for Invoke.
"""

from invoke import run, task
from rituals.invoke_tasks import *


@task
def ci(): # pylint: disable=invalid-name
    """Perform continuous integration tasks."""
    run("invoke clean --all build --docs test check")
