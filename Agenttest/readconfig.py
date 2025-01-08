import yaml
import os

Agent = "银狼"
current_path = os.path.abspath(os.path.dirname(__file__))
print(f"正在{current_path}运行")



with open(f'{current_path}/modelconfig.yaml', 'r') as file:
    config = yaml.safe_load(file)
GPTPath = config['Agents'].get(Agent)["GPTPath"]
SoVITSPath = config['Agents'].get(Agent)["SoVITSPath"]
bgPath = config['Agents'].get(Agent)["bgPath"]
print(f"GPT路径{GPTPath},Soviets路径{SoVITSPath},背景路径{bgPath}")