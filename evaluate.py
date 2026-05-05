from kaggle_environments import make

def evaluate(agent1_file, agent2_file, num_episodes=10):
    env = make("orbit_wars", configuration={"episodeSteps": 1000}, debug=False)
    wins_1 = 0
    wins_2 = 0
    draws = 0
    for i in range(num_episodes):
        steps = env.run([agent1_file, agent2_file])
        rewards = [agent.reward for agent in steps[-1]]
        if rewards[0] > rewards[1]:
            wins_1 += 1
        elif rewards[0] < rewards[1]:
            wins_2 += 1
        else:
            draws += 1
        print(f"Episode {i+1}: {rewards}")
    print(f"Results for {agent1_file} (P1) vs {agent2_file} (P2):")
    print(f"P1 wins: {wins_1}, P2 wins: {wins_2}, Draws: {draws}")

if __name__ == "__main__":
    print("Evaluating my_bot vs base_bot (10 episodes)")
    evaluate("my_bot.py", "base_bot.py", num_episodes=10)
    print("Evaluating base_bot vs my_bot (10 episodes)")
    evaluate("base_bot.py", "my_bot.py", num_episodes=10)
