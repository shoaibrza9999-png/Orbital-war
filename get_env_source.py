import kaggle_environments
import os
path = os.path.join(os.path.dirname(kaggle_environments.__file__), "envs", "orbit_wars", "orbit_wars.py")
with open(path, 'r') as f:
    print(f.read())
