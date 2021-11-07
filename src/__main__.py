"""
Web Page Compressor (v0.1)
==========================

[Dependencies]
json : pip install json
datauri : pip install python-datauri

Wep Page Compressor is a Python command line util who can compres html/css/js,
it's usefull to build only one page website.
"""

__version__ = "0.0.4"
__author__ = "Lucas Maillet"


from datauri import DataURI
import re
import os
from threading import Thread
import time
import json
import argparse


conf = {
    "files": ["index.html"],
    "vars": {}
}

# util functions


def saveConf():
    """

    Description
    ----------
    Save configuration.

    """
    open("conf.json", "w").write(json.dumps(conf, indent=2))


def load(text: str, callBack: callable, args: tuple = ()):
    """

    Description
    ----------
    Wrap a function with a loading animation.

    Parameters
    ----------
    text : STRING
        Text to show next to the animation.
    callBack : CALLABLE
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

    def call(*args):
        global res, stat
        try:
            res = callBack(*args)
            stat = True
        except Exception as err:
            res = err
            stat = False

    Thread(target=call, args=args).start()

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


def getFile(filePath: str) -> str:
    """

    Description
    ----------
    Read file.

    Returns
    ----------
    STRING
        File content.

    """
    return open(f"src/{filePath}").read()


def saveFile(filePath: str, data: str):
    """

    Description
    ----------
    Save file.

    """
    open(f"release/{filePath}", "w").write(data)


def setExtern(data: str) -> str:
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

            # TODO
            # Find a better solution to differentiate "\n" and real newline
            # than this one which is really, REALLY ugly:

            content = re.sub(r"""', '|", "|', "|", '""", "", str(open(filePath, "r").readlines())[
                2:-2].replace("\\'", "'"))

            if "stylesheet" in link:

                subFilePaths = re.findall(
                    r"(?<=url\(\").*?(?=\"\))", content)

                for subFilePath in subFilePaths:
                    subContent = DataURI.from_file(f"src/{subFilePath}")
                    content = re.sub(
                        f"{subFilePath}", f"{str(subContent)}", content)

                data = re.sub(
                    link, f"<style>\n{content}\n</style>", data)

            elif "script" in link:
                data = re.sub(
                    link, f"<script>{content}</script>", data)

    return data


def setVar(data: str) -> str:
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


def removeDescription(data: str) -> str:
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


def removeUseless(data: str) -> str:
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


PARSER = argparse.ArgumentParser()
PARSER.add_argument(
    "filePath", help="path of specific file to compress.", nargs='?', type=str)
PARSER.add_argument("-n", "--new", help="generate new WPC environment..",
                    metavar="webpage", default=False, type=str)
PARSER.add_argument("-b", "--build", help="build webpage.",
                    metavar='mode', nargs='?', default=False, const=" ", type=str)
PARSER.add_argument('-v', '--version', action='version',
                    version=__version__, help="Show program's version number and exit.")

ARGV = PARSER.parse_args()

if ARGV.filePath and not os.path.exists(f"src/{ARGV.filePath}"):
    raise FileNotFoundError("FilePath isn't available")

if ARGV.new:
    """

    Description
    ----------
    Re/Generate a new WPC environment.

    """

    def createNewEnv():
        if not os.path.isdir(ARGV.new):
            os.mkdir(ARGV.new)
            os.chdir(ARGV.new)
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
    exit()

elif ARGV.build:
    """

    Description
    ----------
    Build a new webpage.

    """

    if ARGV.filePath:
        conf["files"] = [ARGV.filePath]

    elif os.path.isfile("conf.json"):
        nConf = json.load(open("conf.json", "r"))
        for key in nConf:
            conf[key] = nConf[key]

    for filePath in conf["files"]:

        print(f"Compiling {filePath}...")

        data = load("Get file", getFile, (filePath,))

        if "e" not in ARGV.build:
            data = load("Set externs ressources from files (e)",
                        setExtern, (data,))
        if "v" not in ARGV.build:
            data = load("Set variables from conf.json (v)",
                        setVar, (data,))
        if "d" not in ARGV.build:
            data = load("Remove description (d)",
                        removeDescription, (data,))
        if "u" not in ARGV.build:
            data = load("Remove useless characters (u)",
                        removeUseless, (data,))

        load("Saving", saveFile, (filePath, data))

    print("Done.")
