import os

def ensure_directory_exists(path):
    try:
        os.mkdir(path)
    except OSError:
        pass #print ("Creation of the directory %s failed" % path) #probably it already exists
