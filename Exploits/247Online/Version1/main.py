import os
import sys
import json
import time
import requests
import websocket
import logging
import signal
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import init, Fore

init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    COLORS = {
        "INFO": Fore.CYAN,
        "DEBUG": Fore.YELLOW,
        "WARNING": Fore.LIGHTYELLOW_EX,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.MAGENTA,
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, Fore.WHITE)
        message = super().format(record)
        return f"{color}[{record.levelname}] {message}"

base_dir = os.path.dirname(os.path.abspath(__file__))
log_directory = os.path.join(base_dir, 'logs')
if not os.path.exists(log_directory):
    os.makedirs(log_directory)


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setFormatter(ColoredFormatter("%(asctime)s - %(message)s"))
logger.addHandler(console_handler)

log_file = os.path.join(log_directory, 'bot_log.log')
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(file_handler)

shutdown_flag = False

def load_config():
    """Load configuration from config.json."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, 'config.json')
    
    with open(config_path, "r") as file:
        config = json.load(file)
    return config["accounts"]


def authenticate(token):
    """Authenticate token and check validity."""
    headers = {"Authorization": token, "Content-Type": "application/json"}
    response = requests.get('https://discordapp.com/api/v9/users/@me', headers=headers)
    if response.status_code != 200:
        logger.error(f"[ERROR] Token {token[:10]}... is invalid. Please check it.")
        return None
    user_info = response.json()
    username = user_info.get("username")
    discriminator = user_info.get("discriminator")
    return headers, f"{username}#{discriminator}" if username and discriminator else "Unknown User"

def onliner(ws, token, status, custom_status, heartbeat_interval):
    """Send authentication and presence data to Discord WebSocket."""
    auth = {
        "op": 2,
        "d": {
            "token": token,
            "properties": {
                "$os": "Windows",
                "$browser": "Chrome",
                "$device": "Desktop",
            },
            "presence": {"status": status, "afk": False},
        },
    }
    ws.send(json.dumps(auth))

    custom_presence = {
        "op": 3,
        "d": {
            "since": 0,
            "activities": [
                {
                    "type": 4,
                    "state": custom_status,
                    "name": "Custom Status",
                    "id": "custom",
                }
            ],
            "status": status,
            "afk": False,
        },
    }
    ws.send(json.dumps(custom_presence))

    while not shutdown_flag:
        time.sleep(heartbeat_interval / 1000)
        ws.send(json.dumps({"op": 1, "d": None}))

def connect_to_discord(token, status, custom_status):
    """Establish WebSocket connection and manage presence."""
    headers, user_info = authenticate(token)
    if headers is None:
        return
    
    while not shutdown_flag:
        try:
            ws = websocket.WebSocket()
            ws.connect("wss://gateway.discord.gg/?v=9&encoding=json")
            start_payload = json.loads(ws.recv())
            heartbeat_interval = start_payload["d"]["heartbeat_interval"]
            
            logger.info(f"Token {token[:10]}... ({user_info}) connected to Discord.")
            onliner(ws, token, status, custom_status, heartbeat_interval)

        except websocket.WebSocketException as e:
            logger.warning(f"Connection error for token {token[:10]} ({user_info}): {e}")
            ws.close()
            time.sleep(5)
            continue

        except Exception as e:
            logger.error(f"Unexpected error for token {token[:10]} ({user_info}): {e}")
            time.sleep(10)
            continue
        
        finally:
            ws.close()

def run_accounts():
    """Run multiple accounts using a thread pool for efficiency."""
    accounts = load_config()
    with ThreadPoolExecutor(max_workers=len(accounts)) as executor:
        futures = [
            executor.submit(connect_to_discord, account["token"], account["status"], account["custom_status"])
            for account in accounts
        ]
        
        try:
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Error in thread execution: {e}")
        except KeyboardInterrupt:
            global shutdown_flag
            shutdown_flag = True
            logger.info("Shutting down... please wait.")
            
            for future in futures:
                future.cancel()

def signal_handler(sig, frame):
    global shutdown_flag
    shutdown_flag = True
    logger.info("Ctrl + C detected! Shutting down... please wait.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    run_accounts()
