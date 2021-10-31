#!/usr/bin/python3.8

import sys
import os
import regex as re
#import re
import _thread
import time
import json

args = []
conf = {
    "project": "defaultName",
    "file": "index.html",
    "vars": {}
}

if os.path.isfile("conf.json"):
    nConf = json.load(open("conf.json", "r"))
    for key in nConf:
        conf[key] = nConf[key]


# util functions


def saveConf():
    open("conf.json", "w").write(json.dumps(conf, indent=2))


def load(text, func, args=()):
    frame = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    lFrame = len(frame)
    idFrame = 0

    global res, stat
    res = stat = None

    def lFunc(*args):
        global res, stat
        try:
            res = func(*args)
            stat = True
        except Exception as err:
            res = err
            stat = False

    _thread.start_new_thread(lFunc, args)

    while stat == None:
        print(f"\r  {frame[idFrame%lFrame]} {text}", end="")
        idFrame += 1
        time.sleep(0.1)

    if stat:
        print(f"\r\033[32m  ✔️ {text}\033[39m")
    else:
        print(f"\r\033[31m  ✖️ {text}")
        print(f"    Error: {res}\033[39m")
        exit()

    return res


# compiling functions


def getFile():
    return open(f"src/{conf['file']}").read()


def saveFile(data):
    open(f"release/{conf['file']}", "w").write(data)


def setExtern(data):
    links = re.findall(
        r"(?=\<link).*?(?<=\>)|(?=\<script).*?(?<=\<\/script\>)", data)

    for link in links:

        filePath = re.findall(
            r'(?<=href\=\").*?(?=\")|(?<=src\=\").*?(?=\")', link)[0]
        filePath = f"src/{filePath}"

        if os.path.isfile(filePath):

            content = str(open(filePath, 'rb').read())[
                2:-1].replace("\\'", "'")

            if "stylesheet" in link:
                data = re.sub(
                    link, f"<style>\n{content}\n</style>", data)

            elif "script" in link:
                data = re.sub(
                    link, f"<script>{content}</script>", data)

    return data


def setVar(data):
    for key in conf['vars']:
        data = data.replace(f"<#{key}>", conf['vars'][key])
    return re.sub(r"(?<=\<\#).*?(?=\>)", "unknow", data)


def removeComment(data):
    toAvoid = "\n".join([s[0] for s in re.findall(
        r"\"(.*?)\"|\'(.*?)\'|\`(.*?)\`|\/(.*?)\/", data) if s[0] != ""])
    for c in re.findall(r"(?s)(?=\/\/).*?(?<=\n)", data):
        if c[:-5] not in toAvoid:
            data = re.sub(c, "", data)
    return data


def removeDescription(data):
    return re.sub(r"(?s)(?=\/\*).*?(?<=\*\/)|(?=\<\!\-\-).*?(?<=\-\-\>)", "", data)


def removeUseless(data):
    return re.sub(r"\s+", " ", re.sub(r"\r\n|\n|\r|\t", "", data))


# cmd functions


def chooseFile():
    if len(args) >= 1:
        if not os.path.isfile(f"src/{args[0]}"):
            print(
                f"""Error: '{f"src/{args[0]}"}' isn't an available file path""")
            exit()
        conf['file'] = args[0]
    else:
        print("Error: no filepath typed")
        exit()


def new():

    if len(args) == 1:
        global conf
        conf = {
            "project": args[0],
            "file": "index.html",
            "vars": {}
        }
    else:
        print("Error: no project name given")
        exit()

    def createNewEnv():
        if not os.path.isdir(conf['project']):
            os.mkdir(conf['project'])
            os.chdir(conf['project'])
        if not os.path.isdir("src"):
            os.mkdir("src")
        if not os.path.isdir("release"):
            os.mkdir("release")
        if not os.path.isfile("src/index.html"):
            open("src/index.html",
                 "w").write("<html>\n    <head></head>\n    <body></body>\n</html>")
        saveConf()

    print(f"Create new environment...")
    load("Create new folders/files", createNewEnv)
    print("Done.")


def build():
    print("Compiling ...")
    data = load("Get file", getFile,)
    cArg = "".join(arg for arg in args if arg[0] == "%")
    if "r" not in cArg:
        data = load("Set externs ressources from files (%l)",
                    setExtern, (data,))
    if "v" not in cArg:
        data = load("Set variables from conf.json (%v)", setVar, (data,))
    if "d" not in cArg:
        data = load("Remove description (%d)", removeDescription, (data,))
    if "c" not in cArg:
        data = load("Remove comment (%c)", removeComment, (data,))
    if "u" not in cArg:
        data = load("Remove useless characters (%u)", removeUseless, (data,))

    load("Saving", saveFile, (data,))
    print("Done.")


def help():
    if (len(args) == 0):
        print("Web Page Compiler (v0.1)\n\nUsage:\n    --command \033[3m [arguments]\033[0m\n\nCommands:\n{cmd}\n\nReport bugs at : \033[3mhttps://github.com/random\033[0m"
              .format(cmd='\n'.join(f"""{f'    {cmd}'.ljust(18)}\033[3m{f"{' '.join([arg for arg in commands[cmd]['args']])}".ljust(18)}{commands[cmd]["desc"]}\033[0m""" for cmd in commands)))
    else:
        for cmd in args:
            cmd = f"--{cmd}"
            if cmd in commands:
                cmdArgs = '\n'.join(
                    [f"""    {f"{arg}".ljust(8)}\033[3m{commands[cmd]['args'][arg]}\033[0m""" for arg in commands[cmd]['args']])
                print(
                    f"""Usage:\n    {cmd} \033[3m [arguments]\033[0m\n\nDescription:\n    {commands[cmd]['desc']}\n\nArguments:\n{cmdArgs}""")
            else:
                print(f"Error: Command '{cmd}' not available, use --help")
    exit()


commands = {
    "--new": {"func": new,  "args": {"name": "Project name"}, "desc": "Create new wpc environment"},
    "--build": {"func": build, "args": {"%r": "Skip using ressources from files", "%v": "Skip using variables of conf.json", "%d": "Skip removing descriptions", "%c": "Skip removing comments", "%u": "Skip removing useless characters"}, "desc": "Compile code, use arg to skip specific step"},
    "--file": {"func": chooseFile,  "args": {"path": "Path of specific file"}, "desc": "Selecte a specific file"},
    "--help": {"func": help,  "args": {"command": "Show this help"}, "desc": "Show support about wpc, use arg to point command details"},
}


# main


if __name__ == "__main__":

    if len(sys.argv) > 1:

        for cmdId in range(len(sys.argv)):

            if sys.argv[cmdId][0] == "-":

                if sys.argv[cmdId] in commands:
                    args = []

                    for arg in sys.argv[cmdId+1:]:
                        if arg[0] == "-":
                            break
                        args.append(arg)

                    if len(args) > len(commands[sys.argv[cmdId]]["args"]):
                        print(
                            f"Error: too much arguments for {sys.argv[cmdId]}, try --help")
                        exit()

                    commands[sys.argv[cmdId]]["func"]()

                else:
                    print(
                        f"Error: Command '{sys.argv[cmdId]}' not available, use --help")

    else:
        print("Error: No command typed, use --help")
