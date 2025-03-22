#test_env.py
from dotenv import dotenv_values

env_values = dotenv_values("api/.env")
print(env_values)
