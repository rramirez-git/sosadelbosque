import os
import subprocess
import sys

for root, dirs, files in os.walk(os.getcwd()):
    if root != os.getcwd():
        for f in files:
            if len(f.split('.')) > 1 and 'py' == f.split('.')[1]:
                arch = "{}".format(os.path.join(root, f))
                if "migrations" not in arch:
                    subprocess.call(['pycodestyle', arch],stdout=sys.stdout)
