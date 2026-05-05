from kaggle_environments import make

env = make("orbit_wars", configuration={"episodeSteps": 10}, debug=True)
steps = env.run(["base_bot.py", "base_bot.py"])
obs = steps[0][0].observation
print(obs.keys())
print("Player:", obs['player'])
print("Step:", obs['step'])
print("Planets length:", len(obs['planets']))
print("Planets example:", obs['planets'][0])
if 'fleets' in obs:
    print("Fleets length:", len(obs['fleets']))
else:
    print("No fleets in obs")

env_cfg = env.configuration
print("Env Config:", env_cfg)
