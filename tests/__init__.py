import os
import sys

DIRECTORY_SCRIPT = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, "%s%s.." % (DIRECTORY_SCRIPT, os.sep))
