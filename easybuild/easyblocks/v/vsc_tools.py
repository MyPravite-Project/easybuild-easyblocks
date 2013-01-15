##
# Copyright 2009-2013 Ghent University
#
# This file is part of EasyBuild,
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://vscentrum.be/nl/en),
# the Hercules foundation (http://www.herculesstichting.be/in_English)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# http://github.com/hpcugent/easybuild
#
# EasyBuild is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation v2.
#
# EasyBuild is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with EasyBuild.  If not, see <http://www.gnu.org/licenses/>.
##
"""
EasyBuild support for building and installing VSC-tools, implemented as an easyblock

@author: Kenneth Hoste (Ghent University)
"""
import os

import easybuild.tools.environment as env
from easybuild.easyblocks.generic.pythonpackage import PythonPackage
from easybuild.tools.filetools import run_cmd


class EB_VSC_minus_tools(PythonPackage):
    """Support for building/installing VSC-tools."""

    def build_step(self):
        """No build procedure for VSC-tools."""

        pass

    def install_step(self):
        """Custom install procedure for VSC-tools."""

        args = "install --prefix=%(path)s --install-lib=%(path)s/lib" % {'path': self.installdir}

        pylibdir = os.path.join(self.installdir, 'lib')
        env.setvar('PYTHONPATH', '%s:%s' % (pylibdir, os.getenv('PYTHONPATH')))

        try:
            os.mkdir(pylibdir)

            pwd = os.getcwd()

            dirs = os.listdir(self.builddir)

            pkg_list = ['-'.join(src['name'].split('-')[0:-1]) for src in self.src if src['name'].startswith('vsc')]
            for pkg in pkg_list:

                sel_dirs = [d for d in dirs if d.startswith(pkg)]
                if not len(sel_dirs) == 1:
                    self.log.error("Found none or more than one %s dir: %s" % (pkg, sel_dirs))

                os.chdir(os.path.join(self.builddir, sel_dirs[0]))
                cmd = "python setup.py %s" % args
                run_cmd(cmd, log_all=True, simple=True, log_output=True)

            os.chdir(pwd)

        except OSError, err:
            self.log.error("Failed to install: %s" % err)

    def sanity_check_step(self):
        """Custom sanity check for VSC-tools."""

        custom_paths = {
                        'files': ['bin/%s' % x for x in ['ihmpirun', 'impirun', 'logdaemon', 'm2hmpirun',
                                                         'm2mpirun', 'mhmpirun', 'mmmpirun', 'mmpirun',
                                                         'mympirun', 'mympisanity', 'myscoop', 'ompirun',
                                                         'pbsssh', 'qmpirun', 'sshsleep', 'startlogdaemon',
                                                         'fake/mpirun']],
                        'dirs': ['lib'],
                       }

        super(EB_VSC_minus_tools, self).sanity_check_step(custom_paths=custom_paths)

    def make_module_extra(self):
        """Add install path to PYTHONPATH"""

        txt = super(PythonPackage, self).make_module_extra()

        txt += "prepend-path\tPYTHONPATH\t%s\n" % os.path.join(self.installdir , 'lib')

        return txt