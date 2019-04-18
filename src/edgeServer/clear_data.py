import pickle
import sys
import os

sys.path.insert(0, "../")
from config import *

f = open(EDGE_CONTENT_DICT_FILENAME, 'wb')
pickle.dump(dict(), f)
f.close()

f = open(EDGE_LRU_FILENAME, 'wb')
pickle.dump(dict(), f)
f.close()

for f in os.listdir('data/'):
	os.remove('data/'+f)