# -*- coding: utf-8 -*-
# pylint: disable=wildcard-import, unused-wildcard-import, unused-import, bad-continuation
""" Project automation for Invoke.
"""

from invoke.tasks import call
from rituals.easy import *

# Example for selective import
#from rituals.acts.documentation import namespace as _
#namespace.add_collection(_)


@task(pre=[
    clean, build, test_pytest, check_pylint, # pylint: disable=undefined-variable
    #call(clean, all=True),
    #call(build, docs=True),
    #call(test),
    #call(check, reports=True),
]) # pylint: disable=invalid-name
def ci(_):
    """Perform continuous integration tasks."""

namespace.add_task(ci)
