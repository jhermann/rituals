# -*- coding: utf-8 -*-
# pylint: disable=wildcard-import, unused-wildcard-import, unused-import, bad-continuation
""" Project automation for Invoke.
"""

from invoke.tasks import call
from rituals.easy import *
#from rituals.invoke_tasks import clean, build, test, check


@task(pre=[
    clean, build, test_pytest, check, # pylint: disable=undefined-variable
    #call(clean, all=True),
    #call(build, docs=True),
    #call(test),
    #call(check, reports=True),
]) # pylint: disable=invalid-name
def ci(_):
    """Perform continuous integration tasks."""

namespace.add_task(ci)
