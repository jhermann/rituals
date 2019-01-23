# -*- coding: utf-8 -*-
# pylint: disable=bad-continuation
""" Tasks specific to Jenkins.
"""
# Copyright ⓒ  2015 Jürgen Hermann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# The full LICENSE file and source are available at
#    https://github.com/jhermann/rituals
from __future__ import absolute_import, unicode_literals, print_function

import io
import re
import sys

from . import Collection, task
from .. import config
from ..util import notify


DESCRIPTION_TEMPLATES = dict(
    html="""<h2>{project.name} v{project.version}</h2>
    {long_description_html}
    <dl>
        <dt>Summary</dt><dd>{project.description}</dd>
        <dt>URL</dt><dd><a href="{project.url}" target="_blank">{project.url}</a></dd>
        <dt>Author</dt><dd>{project.author} &lt;{project.author_email}&gt;</dd>
        <dt>License</dt><dd>{project.license}</dd>
        <dt>Keywords</dt><dd>{keywords}</dd>
        <dt>Packages</dt><dd>{packages}</dd>
        <dt>Classifiers</dt><dd><pre>{classifiers}</pre></dd>
    </dl>
    """,
    md="""## {project.name} v{project.version}

{project.long_description}

 * **Summary**: {project.description}
 * **URL**: {project.url}
 * **Author**: {project.author} <{project.author_email}>
 * **License**: {project.license}
 * **Keywords**: {keywords}
 * **Packages**: {packages}

**Classifiers**

{classifiers_indented}
""",
)


@task(help=dict(
    markdown="Use Markdown instead of HTML",
))
def description(_dummy_ctx, markdown=False):
    """Dump project metadata for Jenkins Description Setter Plugin."""
    cfg = config.load()
    markup = 'md' if markdown else 'html'
    description_file = cfg.rootjoin("build/project.{}".format(markup))
    notify.banner("Creating {} file for Jenkins...".format(description_file))

    long_description = cfg.project.long_description
    long_description = long_description.replace('\n\n', '</p>\n<p>')
    long_description = re.sub(r'(\W)``([^`]+)``(\W)', r'\1<tt>\2</tt>\3', long_description)

    text = DESCRIPTION_TEMPLATES[markup].format(
        keywords=', '.join(cfg.project.keywords),
        classifiers='\n'.join(cfg.project.classifiers),
        classifiers_indented='    ' + '\n    '.join(cfg.project.classifiers),
        packages=', '.join(cfg.project.packages),
        long_description_html='<p>{}</p>'.format(long_description),
        ##data='\n'.join(["%s=%r" % i for i in cfg.project.iteritems()]),
        **cfg)
    with io.open(description_file, 'w', encoding='utf-8') as handle:
        handle.write(text)


namespace = Collection.from_module(sys.modules[__name__])  # pylint: disable=invalid-name
