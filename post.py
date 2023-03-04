from os import path
from shutil import rmtree


Import("env")

def DeleteFiles(source, target, env):
    dir = path.join(path.realpath(env.subst("$BUILD_DIR")), "tmp")
    rmtree(dir)
    
env.AddPostAction("checkprogsize", DeleteFiles)