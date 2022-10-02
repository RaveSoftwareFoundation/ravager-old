#!/usr/bin/python3
from io import BytesIO
import json
from termios import FF1
import zipfile
import os
import shutil

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
    return

def cmd_install():
    print("RSF repo install is not available yet. Use 'ir'.")
    return

def cmd_repoinstall(repo=None, skip_if_exists=False):
    if repo is None:
        if len(sys.argv) < 3:
            print("syntax: ravager ir user/repo")
            return False
        repo = sys.argv[2]

    print(f"Looking for '{repo}'...")
    try:
        pack = requests.get(f"https://raw.githubusercontent.com/{repo}/main/pack.json")
        pack.raise_for_status()
    except Exception as e:
        print(f"An error occured while looking for '{repo}' - {e}")
        return False
    try:
        pack = pack.json()
    except Exception as e:
        print(f"pack.json is invalid - {e}")
        return False
    if os.path.isdir(f"./pkgs/{pack['id']}/"):
        print("Package is already installed. If you want to update, use 'u' instead.")
        return True
    print(f"Package '{pack['name']}' v{pack['version']} found, installing...")
    try:
        dist = requests.get(f"https://raw.githubusercontent.com/{repo}/main/pack.{pack['version']}.dist")
        dist.raise_for_status()
    except Exception as ex:
        print(f"An error occured while getting '{pack['name']}' - {ex}")
        return False
    try:
        z = zipfile.ZipFile(BytesIO(dist.content))
        z.extractall("./pkgs/")
    except Exception as ex:
        print(f"An error occured while unzipping dist - {ex}")
        return False
    open(f"./pkgs/{pack['id']}/pack.json", "w").write(json.dumps(pack))
    print(f"Warning: this is github package, so you should use id '{pack['id']}' for commands like 'r' or 'u'.")
    print("Done.")
    return True

def cmd_update():
    if len(sys.argv) < 3:
        print("syntax: ravager u packageid")
        return
    id = sys.argv[2]
    if not os.path.isfile(f"./pkgs/{id}/pack.json"):
        print(f"Package {id} doesn't exist!")
        return
    pack = json.loads(open(f"./pkgs/{id}/pack.json").read())
    print(f"Looking for '{id}' online...")
    try:
        packre = requests.get(f"https://raw.githubusercontent.com/{pack['source']}/main/pack.json")
        packre.raise_for_status()
    except Exception as e:
        print(f"An error occured while looking for '{id}' - {e}")
        return
    try:
        packre = packre.json()
    except Exception as e:
        print(f"remote pack.json is invalid - {e}")
        return
    if packre["version"] <= pack["version"]:
        print(f"Package '{id}' is already up-to-date!")
        exit(0)
    print(f"Removing old package...")
    shutil.rmtree(f"./pkgs/{id}/")
    print(f"Installing remote...")
    try:
        dist = requests.get(f"https://raw.githubusercontent.com/{pack['source']}/main/pack.{packre['version']}.dist")
        dist.raise_for_status()
    except Exception as ex:
        print(f"An error occured while getting '{packre['name']}' - {ex}")
        return
    try:
        z = zipfile.ZipFile(BytesIO(dist.content))
        z.extractall("./pkgs/")
    except Exception as ex:
        print(f"An error occured while unzipping dist - {ex}")
        return
    open(f"./pkgs/{packre['id']}/pack.json", "w").write(json.dumps(packre))
    print(f"Warning: this is github package, so you should use id '{packre['id']}' for commands like 'r' or 'u'.")
    print("Done.")

def cmd_remove():
    if len(sys.argv) < 3:
        print("syntax: ravager r packageid")
    if not os.path.isdir(f"./pkgs/{sys.argv[2]}"):
        print("Package doesn't exist!")
        return
    shutil.rmtree(f"./pkgs/{sys.argv[2]}/")
    print("Done.")

def cmd_list():
    packages = [x[0] for x in os.walk("./pkgs/")]
    for i in packages:
        if os.path.isfile(f"{i}/pack.json"):
            pack = json.loads(open(f"{i}/pack.json").read())
            print(f"{pack['name']} ({pack['id']}), v{pack['version']}")
    print(f"{len(packages)} packages total.")

def cmd_search():
    print("RSF repo search is not available yet.")
    return

def cmd_installdeps():
    if len(sys.argv) < 3:
        print("syntax: ravager d deps.txt")
        return
    try:
        deps = open(sys.argv[2]).read()
    except Exception as ex:
        print(f"An error occured while reading {sys.argv[2]} - {ex}")
        return
    if "---REPO START---" in deps:
        print("Custom repo list provided, reading")
        repos = deps.split("---REPO START---\n")[1].split("\n---REPO END---")[0].split("\n")
        print(repos)
    cmds = deps.split("---REPO END---\n")
    if len(cmds) < 2:
        cmds1 = cmds[0].split('\n')
    else:
        cmds1 = cmds[1].split("\n")
    cmds = []
    for i in cmds1:
        if i.strip() != "":
            cmds.append(i.strip())
    total = 0
    for i in cmds:
        i = i.split(" ")
        if i[0] == "ir":
            res = cmd_repoinstall(i[1])
            if res: total += 1
        else:
            print(f"Installing using {i[0]} is not supported.")
            return
    print(f"{total}/{len(cmds)} packages installed.")

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
        "s": cmd_search,
        "d": cmd_installdeps
    }.get(sys.argv[1], cmdnotfound)()

if __name__ == "__main__":
    main()