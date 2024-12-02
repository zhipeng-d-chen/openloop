import requests
import json
import random
import time
import os
from colorama import Fore, Style, init
import urllib3
import asyncio

init()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Colors:
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    RED = Fore.RED
    BLUE = Fore.BLUE
    MAGENTA = Fore.MAGENTA
    WHITE = Fore.WHITE
    RESET = Style.RESET_ALL

banner = """
               ╔═╗╔═╦╗─╔╦═══╦═══╦═══╦═══╗
               ╚╗╚╝╔╣║─║║╔══╣╔═╗║╔═╗║╔═╗║
               ─╚╗╔╝║║─║║╚══╣║─╚╣║─║║║─║║
               ─╔╝╚╗║║─║║╔══╣║╔═╣╚═╝║║─║║
               ╔╝╔╗╚╣╚═╝║╚══╣╚╩═║╔═╗║╚═╝║
               ╚═╝╚═╩═══╩═══╩═══╩╝─╚╩═══╝
               我的gihub：github.com/Gzgod
               我的推特：推特雪糕战神@Hy78516012
"""

def logger(message, level='info', value=""):
    now = time.strftime('%Y-%m-%dT%H:%M:%S')
    colors = {
        'info': Colors.GREEN,
        'warn': Colors.YELLOW,
        'error': Colors.RED,
        'success': Colors.BLUE,
        'debug': Colors.WHITE,
    }
    color = colors.get(level, Colors.WHITE)
    print(f"{color}[{now}] [{level.upper()}]: {message}{Colors.RESET}", f"{Colors.YELLOW}{value}{Colors.RESET}")

def get_random_quality():
    return random.randint(60, 99)

def get_tokens():
    if not os.path.exists('token.txt'):
        logger("Token 文件 token.txt 未找到!", 'error')
        return []
    with open('token.txt', 'r') as file:
        return [line.strip() for line in file if line.strip()]

async def share_bandwidth(token):
    try:
        quality = get_random_quality()

        response = requests.post('https://api.openloop.so/bandwidth/share',
                                 headers={'Authorization': f'Bearer {token}',
                                          'Content-Type': 'application/json'},
                                 json={'quality': quality},
                                 verify=False)

        response.raise_for_status()
        data = response.json()

        if 'data' in data and 'balances' in data['data']:
            balance = data['data']['balances'].get('POINT', 'N/A')
            logger(f"分享带宽成功 信息: {Colors.YELLOW}{data.get('message', '无信息')}{Colors.RESET} | "
                   f"分数: {Colors.YELLOW}{quality}{Colors.RESET} | "
                   f"总收益: {Colors.YELLOW}{balance}{Colors.RESET}")
        else:
            logger(f"意外的响应格式: {data}", 'warning')

    except requests.RequestException as e:
        logger(f"分享带宽时出错: {e}", 'error')

async def share_bandwidth_for_all_tokens():
    tokens = get_tokens()
    for index, token in enumerate(tokens):
        logger(f"正在为第 {index + 1} 个账号分享带宽...", 'info')
        await share_bandwidth(token)

def get_account_info():
    if not os.path.exists('accounts.txt'):
        logger("账户信息文件 accounts.txt 未找到!", 'error')
        return []
    with open('accounts.txt', 'r') as file:
        return [line.strip().split(',') for line in file if line.strip()]

def login_user(email, password):
    try:
        login_payload = {'username': email, 'password': password}

        login_response = requests.post('https://api.openloop.so/users/login',
                                       headers={'Content-Type': 'application/json'},
                                       data=json.dumps(login_payload),
                                       verify=False)

        if login_response.status_code != 200:
            raise requests.HTTPError(f"登录失败，状态码: {login_response.status_code}")

        login_data = login_response.json()
        access_token = login_data.get('data', {}).get('accessToken', '')
        if access_token:
            logger('登录成功，获取到 Token:', 'success', access_token)
            with open('token.txt', 'a') as token_file:
                token_file.write(f"{access_token}\n")
            logger('访问令牌已保存到 token.txt')
        else:
            logger('从登录响应中提取访问令牌失败。', 'error')
    except requests.RequestException as e:
        logger('登录过程中出错:', 'error', e)

def register_user():
    try:
        accounts = get_account_info()
        if not accounts:
            logger("账户信息文件 accounts.txt 为空!", 'error')
            return

        invite_code = 'ol9902e367'

        for email, password in accounts:
            registration_payload = {'name': email, 'username': email, 'password': password, 'inviteCode': invite_code}

            try:
                register_response = requests.post('https://api.openloop.so/users/register',
                                                  headers={'Content-Type': 'application/json'},
                                                  data=json.dumps(registration_payload),
                                                  verify=False)

                if register_response.status_code == 401:
                    logger(f'邮箱 {email} 已存在。尝试登录...')
                    login_user(email, password)
                elif register_response.status_code == 200:
                    logger(f'注册 {email} 成功:', 'success')
                    login_user(email, password)
                else:
                    raise requests.HTTPError(f"注册 {email} 失败，状态码: {register_response.status_code}")
            except requests.RequestException as e:
                logger(f'为 {email} 注册或登录时出错:', 'error', e)

    except KeyboardInterrupt:
        logger('用户中断了进程。', 'info')

def main_menu():
    print(Colors.MAGENTA + banner + Colors.RESET)
    logger('开始分享带宽...')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(share_bandwidth_for_all_tokens())

    while True:
        time.sleep(60)
        loop.run_until_complete(share_bandwidth_for_all_tokens())

if __name__ == "__main__":
    register_user()
    main_menu()
