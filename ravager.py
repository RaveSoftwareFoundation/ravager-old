#!/usr/bin/python3
from io import BytesIO, StringIO
import json
import zipfile


try:
    import requests
    import sys
except ImportError as e:
    print(f"Failed to import {e.name} - package not installed.")
    exit(1)

def cmd_help():
    print(f"""ravager - Rave package manager
commands:
    i - install package from RSF repo, example:
        ravager i carcasity
    ir - install package from github repo, example:
        ravager ir ravesoftwarefoundation/carcasity
    u - update package (if possible), example:
        ravager u carcasity
    r - remove package (if exists), example:
        ravager r carcasity
    l - local package list, example:
        ravager l
    s - search in RSF repo, example:
        ravager s carcasity
    h, help - this text""")
    exit(0)

def cmdnotfound():
    print(f"Command {sys.argv[1]} not found.")
    exit(1)

def cmd_install():
    print("RSF repo install is not available yet. Use 'ir'.")
    exit(1)

def cmd_repoinstall():
    if len(sys.argv) < 3:
        print("syntax: ravager ir user/repo")
        exit(1)
    repo = sys.argv[2]
    print(f"Looking for '{repo}'...")
    try:
        pack = requests.get(f"https://raw.githubusercontent.com/{repo}/main/pack.json")
        pack.raise_for_status()
    except Exception as e:
        print(f"An error occured while looking for '{repo}' - {e}")
        exit(1)
    try:
        pack = pack.json()
    except Exception as e:
        print(f"pack.json is invalid - {e}")
        exit(1)
    print(f"Package '{pack['name']}' v{pack['version']} found, installing...")
    try:
        dist = requests.get(f"https://raw.githubusercontent.com/{repo}/main/pack.{pack['version']}.dist")
        dist.raise_for_status()
    except Exception as ex:
        print(f"An error occured while getting '{pack['name']}' - {ex}")
        exit(1)
    try:
        z = zipfile.ZipFile(BytesIO(dist.content))
        z.extractall("./pkgs/")
    except Exception as ex:
        print(f"An error occured while unzipping dist - {ex}")
        exit(1)
    open(f"./pkgs/{pack['id']}/pack.json", "w").write(json.dumps(pack))
    print("Done.")

def cmd_update():
    print("Updating is not available yet. Use 'r', then 'i'/'ir'.")
    exit(1)

def cmd_remove():
    print("Removing is not available yet. Use command line to remove package.")
    exit(1)

def cmd_list():
    print("List is not available yet. Use command line to see packages.")
    exit(1)

def cmd_search():
    print("RSF repo search is not available yet.")
    exit(1)

def main():    
    if len(sys.argv) < 2:
        cmd_help()
    {
        "h": cmd_help,
        "i": cmd_install,
        "ir": cmd_repoinstall,
        "u": cmd_update,
        "r": cmd_remove,
        "l": cmd_list,
        "s": cmd_search
    }.get(sys.argv[1], cmdnotfound)()

if __name__ == "__main__":
    main()