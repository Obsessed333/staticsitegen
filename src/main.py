from textnode import TextNode, TextType
from functions import generate_page
import os
import shutil

static = "./static"
public = "./public"
content = "./content"
template = "./template.html"


def main():
    if (os.path.exists(public) and (os.path.isdir(public))):
        shutil.rmtree(public)
    os.mkdir(public)
    copy_static(static, public)
    copy_content(content, public, template)

def copy_content(src, dst, template):
    for filename in os.listdir(src):
        file_path = os.path.join(src, filename)
        if file_path.endswith(".md"):
            name = filename[:-3] + ".html"
            final_path = os.path.join(dst, name)
            generate_page(file_path, template, final_path)
        elif os.path.isdir(file_path):
            dst_sub = os.path.join(dst, filename)
            if os.path.exists(dst_sub) == False:
                    os.mkdir(dst_sub)
            copy_content(file_path, dst_sub, template)

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
    