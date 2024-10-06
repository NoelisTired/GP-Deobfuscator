import requests

from colorama import Fore, Style

import random

import time

import subprocess

import json

import configparser

import pytz

import datetime

class SeedMineBot:

    total_balance = 0



    def __init__(self, query, proxy=None):

        self.query = query

        self.headers = {

            'accept': 'application/json, text/plain, */*',

            'accept-language': 'en-ID,en-US;q=0.9,en;q=0.8,id;q=0.7',

            'telegram-data': self.query,

            'dnt': '1',

            'origin': 'https://cf.seeddao.org',

            'priority': 'u=1, i',

            'referer': 'https://cf.seeddao.org/',

            'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',

            'sec-ch-ua-mobile': '?0',

            'sec-ch-ua-platform': '"Windows"',

            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'

        }

        self.session = self.create_session(proxy)

        self.config = self.load_config()



    def load_config(self):

        config = configparser.ConfigParser()

        config.read('Bot/seed.ini')

        return config['Ghalibie']



    def create_session(self, proxy=None):

        session = requests.Session()

        # Removed retry and adapter setup

        if proxy:

            proxy_parts = proxy.split(':')

            if len(proxy_parts) == 4:

                proxy_url = f"http://{proxy_parts[2]}:{proxy_parts[3]}@{proxy_parts[0]}:{proxy_parts[1]}"

                session.proxies.update({

                    'http': proxy_url,

                    'https': proxy_url

                })

        return session



    def check_user(self):

        url = "https://elb.seeddao.org/api/v1/profile"

        try:

            response = self.session.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:

                data = response.json()

                print(Fore.CYAN + Style.BRIGHT + f"[ 📍 ] Name : {data['data']['name']}")

                # NotPixelBot.total_balance += data['balance']  # Update total balance



                # Find highest levels of upgrades

                upgrades = data.get('upgrades', [])

                highest_levels = {

                    'mining-speed': 0,

                    'storage-size': 0,

                    'holy-water': 0

                }

                for upgrade in upgrades:

                    upgrade_type = upgrade['upgrade_type']

                    upgrade_level = upgrade['upgrade_level']

                    if upgrade_type in highest_levels and upgrade_level > highest_levels[upgrade_type]:

                        highest_levels[upgrade_type] = upgrade_level



                print(Fore.CYAN + Style.BRIGHT + f"[ ⛏️ ] Mining Level: {highest_levels['mining-speed']}")

                print(Fore.CYAN + Style.BRIGHT + f"[ 📦 ] Storage Level: {highest_levels['storage-size']}")

                print(Fore.CYAN + Style.BRIGHT + f"[ 💧 ] Holy Level: {highest_levels['holy-water']}")



            elif response.status_code == 401:

                print(Fore.RED + Style.BRIGHT + f"[ ❌ ] Unauthorized. Need to refresh query.")

                return False

            elif response.status_code == 500:

                print(Fore.RED + Style.BRIGHT + f"[ ❌ ] Internal Server Error.")

            else:

                print(Fore.RED + Style.BRIGHT + f"[ ❌ ] Failed to fetch data, Status Code: {response.status_code}")

                return False

        except requests.exceptions.RequestException as e:

            print(Fore.RED + f"An error occurred: {e}")

            return False

        return True



    def check_balance(self):

        url = 'https://elb.seeddao.org/api/v1/profile/balance'

        try:

            response = self.session.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:

                data = response.json()

                balance = data['data'] // 1000000000

                SeedMineBot.total_balance += balance

                print(Fore.CYAN + Style.BRIGHT + f"[ 🌱 ] Balance: {balance}")

            elif response.status_code == 401:

                print(Fore.RED + Style.BRIGHT + f"[ ❌ ] Unauthorized. Need to refresh query.")

                return False

            elif response.status_code == 500:

                print(Fore.RED + Style.BRIGHT + f"[ ❌ ] Internal Server Error.")

            else:

                print(Fore.RED + Style.BRIGHT + f"[ ❌ ] Failed to fetch data, Status Code: {response.status_code}")

                return False

        except requests.exceptions.RequestException as e:

            print(Fore.RED + f"An error occurred: {e}")

            return False

        return True

    def claim(self):

        url = 'https://elb.seeddao.org/api/v1/seed/claim'

        try:

            response = self.session.post(url, headers=self.headers, timeout=10)

            if response.status_code == 200:

                data = response.json()

                print(Fore.CYAN + Style.BRIGHT + f"[ 🌿 ] Claim : Success. {data['data']['amount'] // 1000000000}")

            elif response.status_code == 401:

                print(Fore.RED + Style.BRIGHT + f"[ ❌ ] Unauthorized. Need to refresh query.")

                return False

            elif response.status_code == 400:

                print(Fore.RED + Style.BRIGHT + f"[ 🌿 ] Failed. Too Early")

                return False

            elif response.status_code == 500:

                print(Fore.RED + Style.BRIGHT + f"[ ❌ ] Internal Server Error.")

            else:

                print(Fore.RED + Style.BRIGHT + f"[ ❌ ] Failed to fetch data, Status Code: {response.status_code}")

                return False

        except requests.exceptions.RequestException as e:

            print(Fore.RED + f"An error occurred: {e}")

            return False

        return True

    

    def check_worm(self):

        url = 'https://elb.seeddao.org/api/v1/worms'

        try:

            response = self.session.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:

                worm_data = response.json()['data']

                next_refresh = worm_data['next_worm']

                is_caught = worm_data['is_caught']

                type_worm = worm_data['type']



                next_refresh_dt = datetime.datetime.fromisoformat(next_refresh[:-1] + '+00:00')  # Menghapus Z dan menambahkan UTC offset

                now_utc = datetime.datetime.now(pytz.utc)



                # Menghitung selisih waktu dalam detik

                time_diff_seconds = (next_refresh_dt - now_utc).total_seconds()

                hours = int(time_diff_seconds // 3600)

                minutes = int((time_diff_seconds % 3600) // 60)

                print(Fore.CYAN + Style.BRIGHT + f"[ 🐛 ] Type {type_worm}. Next in {hours} hours {minutes} mins - Status: {'Caught' if is_caught else 'Available'}")



                if is_caught == False:

                    response = self.session.post('https://elb.seeddao.org/api/v1/worms/catch', headers=self.headers, timeout=10)

                    if response.status_code == 200:

                        worm_data = response.json()['data']

                        status = worm_data['status']

                        if status == 'failed':

                            print(f"{Fore.RED+Style.BRIGHT}[ 🐛 ] Caught Failed!")

                        else:

                            print(f"{Fore.GREEN+Style.BRIGHT}[ 🐛 ] Caught Success!")

                    elif response.status_code == 200:

                        print(f"{Fore.RED+Style.BRIGHT}[ 🐛 ] Worms Disappeared!")

                    else:

                        print(f"{Fore.RED+Style.BRIGHT}[ 🐛 ] Error. status code:", response.json())

                elif is_caught == True:



                    print(f"{Fore.GREEN+Style.BRIGHT}[ 🐛 ] Already Caught. Type {type_worm} ")

                else:

                    print(f"{Fore.RED+Style.BRIGHT}[ 🐛 ] Error. status code:", response.json())

            elif response.status_code == 401:

                print(Fore.RED + Style.BRIGHT + f"[ 🐛 ] Unauthorized. Need to refresh query.")

                return False

            elif response.status_code == 500:

                print(Fore.RED + Style.BRIGHT + f"[ 🐛 ] Internal Server Error.")

            else:

                print(Fore.RED + Style.BRIGHT + f"[ ❌ ] Failed to fetch data, Status Code: {response.status_code}")

                return False

        except requests.exceptions.RequestException as e:

            print(Fore.RED + f"An error occurred: {e}")

            return False

        return True

    



    @classmethod

    def print_total_balance(cls):

        print(Fore.CYAN + Style.BRIGHT + f"[ 💵 ] Total Balance from all accounts: {cls.total_balance}")



    def run(self):

        if not self.check_user():

            return False

        self.check_balance()

        self.claim()

        self.check_worm()

 

        # if self.config.get('autocleartask', 'n').lower() == 'y':

        #     self.clear_tasks()

        return True