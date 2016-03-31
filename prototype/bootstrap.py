#!/usr/bin/env python3
# -*- coding: utf-8 -*- {{{
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

_WINDOWS = sys.platform.startswith('win')
_ENV = 'env'
_PACKAGES = 'packages.txt'


def bootstrap(dest=_ENV, prompt='(sphinx)'):
    '''Download and install Virtualenv to setup our Python environment.

    The virtual environtment well be setup in dest.
    '''

    import contextlib
    import re
    import shutil
    import tarfile
    import tempfile
    from urllib.request import urlopen

    _DOAP_URL = "https://pypi.python.org/pypi?:action=doap&name=virtualenv"
    _VENV_URL = "https://pypi.python.org/packages/source/v/virtualenv/virtualenv-{}.tar.gz"

    class EnvBuilder:
        def __init__(self, version=None, prompt=None):
            self.version = version
            self.prompt = prompt
            self.env_exe = None

        def _fetch(self, url):
            '''Open URL and return response, or quit'''
            sys.stdout.write("Fetching {}...\n".format(url))

            response = urlopen(url)
            if response.getcode() != 200:
                sys.stderr.write('Download failed!  Server response is {} {}.\n'.format(
                    response.code, response.msg))
                sys.exit(1)

            return response

        def get_version(self):
            '''Return the latest version from the Virtualenv DOAP record.'''
            with contextlib.closing(self._fetch(_DOAP_URL)) as response:
                doap_xml = response.read()

                self.version = re.search(b'<revision>([^<]*)</revision>',
                                         doap_xml).group(1).decode('utf-8')

            return self.version

        def download(self, directory):
            '''Download the Virtualenv tarball'''
            if self.version is None:
                self.get_version()

            url = _VENV_URL.format(self.version)
            sys.stdout.write("Downloading Virtualenv {}\n".format(self.version))
            tarball = os.path.join(directory, 'virtualenv.tar.gz')
            with contextlib.closing(self._fetch(url)) as response:
                with open(tarball, 'wb') as file:
                    shutil.copyfileobj(response, file)

            with contextlib.closing(tarfile.open(tarball, 'r|gz')) as archive:
                archive.extractall(directory)

        def create(self, directory):
            '''Create a virtual environtment.'''
            tmpdir = tempfile.mkdtemp()
            try:
                self.download(tmpdir)
                args = [sys.executable]
                args.append(os.path.join(tmpdir, 'virtualenv-{}'.format(
                    self.version), 'virtualenv.py'))
                if self.prompt:
                    args.extend(['--prompt', prompt])

                args.append(directory)
                subprocess.check_call(args)

                if _WINDOWS:
                    self.env_exe = os.path.join(directory, 'Scripts', 'python.exe')
                else:
                    self.env_exe = os.path.join(directory, 'bin', 'python')

                assert(os.path.exists(self.env_exe))
                                
            finally:
                shutil.rmtree(tmpdir, ignore_errors=True)
                            

    sys.stdout.write("Creating Python virtual environment...\n")
    builder = EnvBuilder(prompt=prompt)
    builder.create(dest)
        
    return builder.env_exe


def run_pip():
    '''Call pip in the virtual environment to install packages.'''
    cmd = ['pip', 'install']
    cmd[:0] = [sys.executable, '-m']
    subprocess.check_called(cmd)


def install_packages():
    '''Install and or update dependencies from packages.txt.'''
    path = os.path.dirname(__file__) or '.'
    packages = os.path.join(path, _PACKAGES)
    if os.path.exists(packages):
        cmd = [sys.executable, '-m', 'pip', 'install', '-r', packages]
        subprocess.check_call(cmd)


def main(argv=sys.argv):
    # Refuse to run as root
    if not getattr(os, 'getuid', lambda: -1)():
        sys.stderr.write("{}: error; please don't run as root!\n".format(
            os.path.basename(argv[0])))
        sys.exit(7)

    python = os.path.join('$VIRTUAL_ENV', 'Scripts' if _WINDOWS
                          else 'bin', 'python')

    if _WINDOWS:
        python += '.exe'

    # We need Python 3.4 for asyncio support
    if sys.version_info.major != 3 and sys.version_info.minor >= 4:
        sys.stderr.write("{}: error; Python > 3.4 is required.\n".format(
            os.path.basename(argv[0])))
        sys.exit(6)

    # Install Virtualenv and Sphinx dependencies
    if hasattr(sys, 'real_prefix'):
        # script called from virtual environment, so install/update and bootstrap modules
        install_packages()

        from sphinx.bootstrap import generate_types
        # Generate the PDBx/mmCIF JSON Schema
        generate_types()

    else:
        # script called from system python -- bootstrap
        try:
            # Don't install if our environment is already setup
            if os.listdir(_ENV):
                sys.stderr.write("{}: error; Virtualenv is already setup.\n".format(
                    os.path.basename(argv[0])))
                sys.exit(5)

        except OSError as exc:
            if exc.errno != errno.ENOENT:
                raise
            
        env_exe = bootstrap()

        # Now do stage 2...
        # TODO: On OSX this doesn't appear to give the correct path to the Python
        # executable, and pip doesn't install packages into the local environment.
        args = [env_exe, __file__]
        subprocess.check_call(args)

                
                
if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		pass
