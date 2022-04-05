import subprocess
import threading
import time
from datetime import datetime
import os
import re
import json
from concurrent.futures import ThreadPoolExecutor


# The server process
server = subprocess.Popen('./bedrock_server',
                          stdout=subprocess.PIPE,
                          stdin=subprocess.PIPE)

# Detect player connection
regex = re.compile(r'Player connected: (\w+), xuid: (\d+)')
players = {}

# Send MOTD
def motd(cmd):
    time.sleep(5)
    server.stdin.write(cmd.encode('utf-8'))
    server.stdin.flush()


def mkdir():
    if not os.path.exists('logs/'):
        os.makedirs('logs/')


pool = ThreadPoolExecutor(max_workers=4)


try:
    # Redirect STDOUT to file
    mkdir()
    log = datetime.now().strftime("logs/%Y-%m-%d_%H-%M-%S.log")
    file = open(log, 'wb')
    while True:
        line = server.stdout.readline()
        txt = line.decode('utf-8').strip()
        print(txt)

        file.write(line)
        file.flush()

        # Player connection
        search = regex.search(txt)
        if search:
            username = search.group(1)
            xuid = search.group(2)

            # Raw JSON data
            data = {
                "rawtext": [{
                    "text": "\ua080§6枫叶小镇§r\ua080\n"
                }, {
                    "text": "欢迎, %s\n" % username
                }]
            }

            # Read last login time
            last_login = players.get(xuid)
            if last_login:
                data["rawtext"].append({
                    "text":
                    "上次登录: %s" % last_login.strftime("%Y-%m-%d, %H:%M:%S")
                })
            players[xuid] = datetime.now()

            # Send command
            cmd = 'tellraw %s %s\n' % (username, json.dumps(data))
            print(cmd)
            pool.submit(motd, cmd)

except KeyboardInterrupt as e:
    print("Shutting down server...")
    file.close()
    server.stdin.write(b'stop')
    server.stdin.flush()
