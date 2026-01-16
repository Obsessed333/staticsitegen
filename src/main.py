from textnode import TextNode, TextType
from functions import generate_pages_recursive
import os
import shutil
import sys

static = "./static"
docs = "./docs"
content = "./content"
template = "./template.html"

basepath = sys.argv[0]

def main():
    if (os.path.exists(docs) and (os.path.isdir(docs))):
        shutil.rmtree(docs)
    os.mkdir(docs)
    copy_static(static, docs)
    generate_pages_recursive(content, docs, template, basepath)



def copy_static(src, dst):
    for filename in os.listdir(src):
        file_path = os.path.join(src, filename)
        if os.path.isfile(file_path):
            shutil.copy(file_path, dst)
        elif os.path.isdir(file_path):
            dst_sub = os.path.join(dst, filename)
            os.mkdir(dst_sub)
            copy_static(file_path, dst_sub)


    

if __name__ == "__main__":
    main()
    