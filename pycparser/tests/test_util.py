#------------------------------------------------------------------------------
# pycparser: test_util.py
#
# Utility code for tests.
#
# Eli Bendersky [https://eli.thegreenplace.net/]
# This file contributed by vit9696@users.noreply.github.com
# License: BSD
#------------------------------------------------------------------------------
import os
import platform
import subprocess
import sys


def cpp_supported():
    """Is cpp (the C preprocessor) supported as a native command?"""
    return platform.system() == 'Linux'


def cpp_path():
    """Path to cpp command."""
    if platform.system() == 'Darwin':
        return 'gcc'
    return 'cpp'


def cpp_args(args=[]):
    """Turn args into a suitable format for passing to cpp."""
    if isinstance(args, str):
        args = [args]
    if platform.system() == 'Darwin':
        return ['-E'] + args
    return args

def _bytes2str(b):
    if sys.version_info[0] == 3:
        return b.decode('latin-1')
    else:
        return b

def run_exe(exe_path, args=[], echo=False):
    """ Runs the given executable as a subprocess, given the
        list of arguments. Captures its return code (rc) and stdout and
        returns a pair: rc, stdout_str
    """
    popen_cmd = [exe_path] + args
    if os.path.splitext(exe_path)[1] == '.py':
        popen_cmd.insert(0, sys.executable)
    if echo:
      print('[cmd]', ' '.join(popen_cmd))
    proc = subprocess.Popen(popen_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc_stdout = proc.communicate()[0]
    return proc.returncode, _bytes2str(proc_stdout)
