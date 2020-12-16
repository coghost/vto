import os
import sys

app_root = '/'.join(os.path.abspath(__file__).split('/')[:-2])
sys.path.append(app_root)

import vto

# for k in vto.registered:
#     getattr(vto, k)()
