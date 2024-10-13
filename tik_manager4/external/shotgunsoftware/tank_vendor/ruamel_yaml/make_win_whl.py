
"""
The windows whl file has no C stuff but a
ruamel.yaml-0.9.2-py2-none-any.whl file overrules the .tar.gz on Linux.

You can create a .whl and copy it to impure names (or start
with an impure one), not sure if this is necessary.

"""

import sys
import os
import shutil


def main():
    src = sys.argv[1]
    print src, '-->'
    dir_name = os.path.dirname(src)
    base_name = os.path.basename(src)
    p, v, rest = base_name.split('-', 2)
    #print dir_name
    for pyver in ['cp26', 'cp27', 'cp33', 'cp34']:
        for platform in ['win32', 'win_amd64']:
            dst = os.path.join(dir_name,
                               '%s-%s-%s-none-%s.whl' % (
                                   p, v, pyver, platform
                               ))
            print dst
            shutil.copy(src, dst)

main()