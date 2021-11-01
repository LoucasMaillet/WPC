#!/usr/bin/python3.8
"""
Web Page Compressor (v0.1)
==========================

[Dependencies]
regex : pip install regex
json : pip install json

Wep Page Compressor is a Python command line util who can compres html/css/js,
it's usefull to build only one page website.
"""


import sys
import os
import regex as re
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
    """

    Description
    ----------
    Save configuration.

    """
    open("conf.json", "w").write(json.dumps(conf, indent=2))


def load(text: str, func: callable, args: tuple = ()):
    """

    Description
    ----------
    Wrap a function with a loading animation.

    Parameters
    ----------
    text : STRING
        Text to show next to the animation.
    func : CALLABLE
        Function to wrap with animation.
    args : TUPLE <optional>
        Arguments of the function.

    Returns
    ----------
    res : UNKNOW TYPE
        The results of the function executed.

    """
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
    """

    Description
    ----------
    Read file.

    Returns
    ----------
    STRING
        File content.

    """
    return open(f"src/{conf['file']}").read()


def saveFile(data : str):
    """

    Description
    ----------
    Save file.

    """
    open(f"release/{conf['file']}", "w").write(data)


def setExtern(data : str):
    """

    Description
    ----------
    Get extern ressource from file by filePath.

    Parameters
    ----------
    data : STRING
        FileContent to add extern fileContent.

    Returns
    ----------
    data : STRING
        FileContent transformed.

    """
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
    """

    Description
    ----------
    Transform <#key> by key value in vars in conf.json.

    Parameters
    ----------
    data : STRING
        FileContent to change his variable.

    Returns
    ----------
    data : STRING
        FileContent transformed.

    """
    for key in conf['vars']:
        data = data.replace(f"<#{key}>", conf['vars'][key])
    return re.sub(r"(?<=\<\#).*?(?=\>)", "unknow", data)


def removeDescription(data):
    """

    Description
    ----------
    Remove javascript/css description ("/* ... */") and html description ("<!-- ... -->").

    Parameters
    ----------
    data : STRING
        FileContent to remove his description.

    Returns
    ----------
    data : STRING
        FileContent transformed.

    """
    return re.sub(r"(?s)(?=\/\*).*?(?<=\*\/)|(?=\<\!\-\-).*?(?<=\-\-\>)", "", data)


def removeUseless(data):
    """

    Description
    ----------
    Remove useless chacraters (\r\n, \n, \r, \t, \s+).

    Parameters
    ----------
    data : STRING
        FileContent to remove useless characters.

    Returns
    ----------
    data : STRING
        FileContent transformed.

    """
    return re.sub(r"\s+", " ", re.sub(r"\r\n|\n|\r|\t", "", data))


# cmd functions


def chooseFile():
    """

    Description
    ----------
    Select a specific filePath.

    """
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
    """

    Description
    ----------
    Re/Generate a new WPC environment.

    """
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
    """

    Description
    ----------
    Build a new webpage.

    """
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
    if "u" not in cArg:
        data = load("Remove useless characters (%u)", removeUseless, (data,))

    load("Saving", saveFile, (data,))
    print("Done.")


def help():
    """

    Description
    ----------
    Show a help support.

    """
    if (len(args) == 0):
        print("Web Page Compressor (v0.1)\n\nUsage:\n    --command \033[3m [arguments]\033[0m\n\nCommands:\n{cmd}\n\nReport bugs at : \033[3mhttps://github.com/LoucasMaillet/WPC\033[0m"
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
    "--build": {"func": build, "args": {"%r": "Skip using ressources from files", "%v": "Skip using variables of conf.json", "%d": "Skip removing descriptions", "%u": "Skip removing useless characters"}, "desc": "Compile code, use arg to skip specific step"},
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
