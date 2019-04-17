import pickle
import sys

sys.path.insert(0, "../../")
from config import *

f = open(ORIGIN_METADATA_FILENAME, 'wb')
pickle.dump(dict(), f)
f.close()