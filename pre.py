from os import path, makedirs, rmdir
from re import finditer, escape
import requests

Import("env")

TAG_FILE ="IMPORT_FILE"
TAG_LINK  ="IMPORT_LINK"
DEFAULT_PATH = {"$PROJ":    path.realpath(path.join(env.subst("$BUILD_DIR"), "..", "..", ".."))}

DEFAULT_PATH["$SRC"]    =path.realpath(path.join(DEFAULT_PATH["$PROJ"], "src"))
DEFAULT_PATH["$LIB"]    =path.realpath(path.join(DEFAULT_PATH["$PROJ"], "lib"))
DEFAULT_PATH["$INCLUDE"]=path.realpath(path.join(DEFAULT_PATH["$PROJ"], "include"))
DEFAULT_PATH["$TEST"]   =path.realpath(path.join(DEFAULT_PATH["$PROJ"], "test"))
DEFAULT_PATH["$BUILD"]  =path.realpath(env.subst("$BUILD_DIR"))

def getTmpNode(node:str) -> str:
    node = path.splitdrive((str(node)))
    drive=node[0][:-1]
    file=node[1][1:]
    return path.join(
        DEFAULT_PATH["$BUILD"], 
        "tmp",
        drive, 
        file
        )

def FindItens(code:str):
    beginList = [match.start() for match in finditer("("+escape(TAG_FILE)+"|"+escape(TAG_LINK)+")", code)]
    endList = []
    for it in beginList:
        while code[it] != "\"":
            it += 1
        endList.append(it)
    return [(b, e) for b, e in zip(beginList, endList)]

def ExpandPath(file):
    itens = path.normpath(file)
    itens = itens.split(path.sep)
    if itens[0].startswith("$"):
        try:
            itens[0] = DEFAULT_PATH[itens[0]]
        except:
            print(f"Error: {itens[0]} not exist")
    else:
        itens[0] += path.sep
    
    return path.join(*itens)

def getLink(link:str):
    try:
        url = requests.get(link)
        print(f"\tfound: [{link}]")
    
        return url.text
    except ValueError:
        raise Exception("Link not found: " + link)

def getFile(item:str):
    file = ExpandPath(item)
    try:
        with open(file) as f:
            print(f"\tfound: [{file}]")
            return f.read()
    except ValueError:
        raise Exception("File not found: " + file)

def getItem(item:str) -> str:
    if item.startswith(TAG_FILE):
        return getFile(item[len(TAG_FILE)+1:])
    else:
        return getLink(item[len(TAG_FILE)+1:])


def changeFile(newFile:str, string:str, begin, end):
    newFile = newFile[0: begin-1:] + string+newFile[end+2::]
    return newFile

def processTxt(var:str):
    newStr = var.replace("\"", r"a\"")
    newStr = newStr.replace("\n", "\\n")

    return newStr

def replace_node_with_another(env, node):
    node = str(node)
    if ".platformio" in node:
        return node
    
    newpath = getTmpNode(node)

    with open(node) as f:
        print(f"File: \t{node}")
        code = f.read()
        for it in reversed(FindItens(code)):
            var = getItem(code[it[0]:it[1]])
            code = code[:it[0]]+processTxt(var)+code[it[1]:]

    makedirs(path.dirname(newpath), exist_ok=True)
    with open(newpath, 'w') as f:
        f.write(code)
    return env.File(newpath)



env.AddBuildMiddleware(replace_node_with_another)
