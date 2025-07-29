import json
from utils.resource_path import ResourcePath

RPC=ResourcePath("config","config")

with open(RPC.file("config.json"), 'r') as f:  # 读取config.json配置文件
    config = json.load(f)
    game_path = config.get('game_path')
    task_index = config.get('combo_task')
    squad_index = config.get('combo_squad')
    level_index = config.get('combo_level')
    check_coffee = config.get('check_coffee')
    check_reward = config.get('check_reward')
    check_lottery = config.get('check_lottery')
    developer_mode = config.get('developer_mode')
    shutdown_index = config.get('shutdown')

    combo_date = config.get("combo_hollow_date")  # 空洞页面
    combo_round = config.get("combo_hollow_round")
    combo_type = config.get("combo_hollow_type")

    if config.get('speed') == 0:
        action_speed = 0.5
        wait_speed = 0.5
        timeout_round = 20  # 20s
        skip_round = 8  # 8s
    if config.get('speed') == 1:
        action_speed = 0.2
        wait_speed = 0.5
        timeout_round = 20  # 20s
        skip_round = 6  # 6s
    if config.get('speed') == 2:
        action_speed = 1
        wait_speed = 0.5
        timeout_round = 30  # 30s
        skip_round = 20  # 15s