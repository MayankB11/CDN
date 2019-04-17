import pickle
import sys
import os

sys.path.insert(0, "../../")
from config import *

f = open(ORIGIN_METADATA_FILENAME, 'wb')
pickle.dump(dict(), f)
f.close()

for f in os.listdir('data/'):
	os.remove('data/'+f)