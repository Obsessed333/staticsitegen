from htmlnode import LeafNode, ParentNode, HTMLNode
from textnode import TextNode, TextType, BlockType
import re
import os

def text_node_to_html_node(text_node):
    if text_node.text_type == TextType.TEXT:
        return LeafNode(None, text_node.text)
    elif text_node.text_type == TextType.BOLD:
        return LeafNode("b", text_node.text)
    elif text_node.text_type == TextType.ITALIC:
        return LeafNode("i", text_node.text)
    elif text_node.text_type == TextType.CODE:
        return LeafNode("code", text_node.text)
    elif text_node.text_type == TextType.LINK:
        return LeafNode("a", text_node.text, {"href":text_node.url})
    elif text_node.text_type == TextType.IMAGE:
        return LeafNode("img", "", {"src": text_node.url, "alt": text_node.text})
    else:
        raise Exception("ERROR: Enter a supported text type")

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_node_list = []
    
    for old_node in old_nodes:

        if old_node.text_type != TextType.TEXT:
            new_node_list.append(old_node)
            continue

        if old_node.text.count(delimiter) % 2 != 0:
            raise Exception("delimiter is not closed")

        temp = old_node.text.split(delimiter)
        for i, chunk in enumerate(temp):

            if chunk == "":
                continue

            if i % 2 == 0:
                new_node_list.append(TextNode(chunk, TextType.TEXT))

            else:
                new_node_list.append(TextNode(chunk, text_type))

    return new_node_list

def extract_markdown_images(text):
    matches = re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches

def extract_markdown_links(text):
    matches = re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches

def split_nodes_image(old_nodes):
    new_node_list = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_node_list.append(old_node)
            continue

        image = extract_markdown_images(old_node.text)
        if not image:
            new_node_list.append(old_node)
            continue
        current = old_node.text
        for alt, url in image:
            
            before, after = current.split(f"![{alt}]({url})", 1)
            if before:
                new_node_list.append(TextNode(before, TextType.TEXT))
            new_node_list.append(TextNode(alt, TextType.IMAGE, url))
            current = after
        if current:
            new_node_list.append(TextNode(current, TextType.TEXT))
            
    return new_node_list

def split_nodes_link(old_nodes):
    new_node_list = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_node_list.append(old_node)
            continue

        link = extract_markdown_links(old_node.text)
        if not link:
            new_node_list.append(old_node)
            continue
        current = old_node.text
        for text, url in link:
            
            before, after = current.split(f"[{text}]({url})", 1)
            if before:
                new_node_list.append(TextNode(before, TextType.TEXT))
            new_node_list.append(TextNode(text, TextType.LINK, url))
            current = after
        if current:
            new_node_list.append(TextNode(current, TextType.TEXT))
            
    return new_node_list

def text_to_textnodes(text):

    nodes = [TextNode(text, text_type= TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes

def markdown_to_blocks(markdown):

    blocks = []
    for chunk in markdown.split("\n\n"):
        chunk = chunk.strip()
        if chunk:          
            blocks.append(chunk)
    return blocks

def block_to_block_type(markdown):
    block = markdown
    lines = block.split("\n")

    if block.startswith(("# ", "## ", "### ", "#### ", "##### ", "###### ")):
        return BlockType.HEADING

    if len(lines) > 1 and lines[0].startswith("```") and lines[-1].startswith("```"):
        return BlockType.CODE

    first = lines[0].lstrip()
    if first.startswith(">"):
        for line in lines:
            if not line.lstrip().startswith(">"):
                return BlockType.PARAGRAPH
        return BlockType.QUOTE


    if block.startswith("- "):
        for line in lines:
            if not line.startswith("- "):
                return BlockType.PARAGRAPH
        return BlockType.UNORDERED_LIST


    if block.startswith("1. "):
        i = 1
        for line in lines:
            if not line.startswith(f"{i}. "):
                return BlockType.PARAGRAPH
            i += 1
        return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH
              
def markdown_to_html_node(markdown):

    blocks = markdown_to_blocks(markdown)
    block_list = []

    for i, block in enumerate(blocks):
        ## print("BLOCK", i, "=", repr(block))
        block = block_to_html_node(block)
        block_list.append(block)
    
    final_node = ParentNode("div", children=block_list)
    return final_node

def block_to_html_node(block):
    block_type = block_to_block_type(block)
    ## print("DEBUG block type:", block_type)
    count = 0
    if block_type == BlockType.PARAGRAPH:
        lines = block.split("\n")
        cleaned_lines = [line.strip() for line in lines if line.strip()]
        joined = " ".join(cleaned_lines)
        children = text_to_children(joined)
        return ParentNode("p", children)

    elif block_type == BlockType.HEADING:
        while block and block[0] == "#":
            count +=1
            block = block[1:]
        block = block.strip()
        children = text_to_children(block)
        return ParentNode(f"h{count}", children)
    
    elif block_type == BlockType.CODE:
        lines = block.split("\n")
        content_lines = lines[1:-1]
        indents = [
            len(line) - len(line.lstrip(" "))
            for line in content_lines
            if line.strip() != ""
        ]
        if indents:
            min_indent = min(indents)
        else:
            min_indent = 0
        no_indent_lines = []
        for line in content_lines:
            no_indent_lines.append(line[min_indent:])
        inner = "\n".join(no_indent_lines) + "\n"
        node = LeafNode("code", inner)
        return ParentNode("pre", [node])
    
    elif block_type == BlockType.QUOTE:
        lines = block.split("\n")
        cleaned = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                line = line[1:]
                if line.startswith(" "):
                    line = line[1:]
            cleaned.append(line)
        joined = " ".join(cleaned)
        children = text_to_children(joined)
        return ParentNode("blockquote", children)
    
    elif block_type == BlockType.UNORDERED_LIST:
        lines = block.split("\n")
        li_nodes = []
        for line in lines:
            if not line.strip():
                continue
            line = line.lstrip("- ")
            children = text_to_children(line)
            li_node = ParentNode("li",children)
            li_nodes.append(li_node)
        return ParentNode("ul", li_nodes)
    
    elif block_type == BlockType.ORDERED_LIST:
        lines = block.split("\n")
        li_nodes = []
        count = 1
        for line in lines:
            if not line.strip():
                continue
            line = line.strip()
            line = line[len(f"{count}. "):]
            children = text_to_children(line)
            li_node = ParentNode("li", children)
            li_nodes.append(li_node)
            count += 1
        return ParentNode("ol", li_nodes)
        
def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    children = []
    for node in text_nodes:
        child = text_node_to_html_node(node)
        children.append(child)
    return children

def extract_title(markdown):
    blocks = markdown_to_blocks(markdown)
    header = False
    for block in blocks:
        if block.startswith("# "):
            title = block[2:]
            title = title.strip()
            header = True
            return title
    if header == False:
        raise Exception("there is no h1 header")
    
def generate_page(from_path, template_path, dest_path, basepath):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    with open(from_path, "r") as f:
        contents_from_path = f.read()
    with open(template_path, "r") as f:
        contents_from_template = f.read()
    content_html = markdown_to_html_node(contents_from_path).to_html()
    title = extract_title(contents_from_path)
    contents_from_template = contents_from_template.replace("{{ Title }}", title)
    contents_from_template = contents_from_template.replace("{{ Content }}", content_html)
    contents_from_template = contents_from_template.replace('href="/', f'href="' + basepath)
    contents_from_template = contents_from_template.replace('src="/', f'src="' + basepath)
    dir_name = os.path.dirname(dest_path)
    os.makedirs(dir_name, exist_ok = True)
    with open(dest_path, "w") as f:
        f.write(contents_from_template)

def generate_pages_recursive(src, dst, template, basepath):
    for filename in os.listdir(src):
        file_path = os.path.join(src, filename)
        if file_path.endswith(".md"):
            name = filename[:-3] + ".html"
            final_path = os.path.join(dst, name)
            generate_page(file_path, template, final_path, basepath)
        elif os.path.isdir(file_path):
            dst_sub = os.path.join(dst, filename)
            if os.path.exists(dst_sub) == False:
                    os.mkdir(dst_sub)
            generate_pages_recursive(file_path, dst_sub, template, basepath)