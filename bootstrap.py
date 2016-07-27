# -*- coding: utf-8 -*- {{{
# vim: set fenc=utf-8 ft=python ff=unix sw=4 ts=4 sts=4 et:

# APBS -- Adaptive Poisson-Boltzmann Solver
#
#  Nathan A. Baker (nathan.baker@pnnl.gov)
#  Pacific Northwest National Laboratory
#
#  Additional contributing authors listed in the code documentation.
#
# Copyright (c) 2010-2016 Battelle Memorial Institute. Developed at the
# Pacific Northwest National Laboratory, operated by Battelle Memorial
# Institute, Pacific Northwest Division for the U.S. Department of Energy.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# Neither the name of the developer nor the names of its contributors may be
# used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.
#}}}

import errno
import os
import subprocess
import sys

__author__ = 'Keith T. Star <keith@pnnl.gov>'

_ENV = 'sphinx-env'
_PACKAGES = 'packages.txt'

def bootstrap(dest = _ENV):
    import venv

    class EnvBuilder(venv.EnvBuilder):
        def __init__(self, *args, **kwargs):
            # Not much going on here...yet.
            super().__init__(*args, **kwargs)

        def post_setup(self, context):
            ''' Deal with dependencies

            Once we have our Python environment we have pip install the packages listed
            in packages.txt, and then we do any bootstrapping.
            '''
            path = os.path.dirname(__file__) or '.'
            packages = os.path.join(path, _PACKAGES)
            if os.path.exists(packages):
                pip = os.path.join(context.bin_path, 'pip')
                cmd = [pip, 'install', '-r', packages]
                subprocess.check_call(cmd)


            python = os.path.join(context.bin_path, 'python')
            if os.name == 'nt':
                python += '.exe'

            cmd = [python, '-m', 'sphinx.bootstrap']
            subprocess.check_call(cmd)



    sys.stdout.write("Creating Python virtual environment...\n")
    if os.name == 'nt':
        use_symlinks = False
    else:
        use_symlinks = True

    builder = EnvBuilder(symlinks = use_symlinks, with_pip = True)
    builder.create(dest)


def main(argv = sys.argv):
    ''' Install Python venv and bootstrap Sphinx

    This script calls itself to bootstrap Sphinx once the virtual environment
    is setup.
    '''

    # Refuse to run as root
    if not getattr(os, 'getuid', lambda: -1)():
        sys.stderr.write("{}: error; please don't run as root!\n".format(
            os.path.basename(argv[0])))
        sys.exit(7)

    # We need Python 3.5 for asyncio support
    if sys.version_info < (3, 5):
        sys.stderr.write("{}: error; Python > 3.5 is required.\n".format(
            os.path.basename(argv[0])))
        sys.exit(6)

    bootstrap()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    except subprocess.CalledProcessError as exc:
        sys.exit(exc.returncode)
