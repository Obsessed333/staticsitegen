import unittest

from textnode import TextNode, TextType, BlockType
from functions import text_node_to_html_node, split_nodes_delimiter, extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link
from functions import text_to_textnodes, markdown_to_blocks, block_to_block_type, markdown_to_html_node
from htmlnode import ParentNode

class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)
        
    def test_text_diff(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.ITALIC)
        if self.assertNotEqual(node, node2) and self.assertNotEqual(node.text_type, node2.text_type):
            return True
    
    def test_urlnone(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertIsNone(node.url)

    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")
    
    def test_split(self):

        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(len(new_nodes), 3)
        self.assertEqual(new_nodes[0].text, "This is text with a ")
        self.assertEqual(new_nodes[0].text_type, TextType.TEXT)

    def test_splitodd(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        
    
    def test_extract_markdown_images(self):
        matches = extract_markdown_images("This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)")
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_link(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a link ", TextType.TEXT),
             TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
              TextNode(" and ", TextType.TEXT),
             TextNode(
               "to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"
     ),
            ],
            new_nodes,
        )
                                        
    def test_text_to_textnode(self):

        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        cuck = text_to_textnodes(text)

        self.assertListEqual(cuck, [
    TextNode("This is ", TextType.TEXT),
    TextNode("text", TextType.BOLD),
    TextNode(" with an ", TextType.TEXT),
    TextNode("italic", TextType.ITALIC),
    TextNode(" word and a ", TextType.TEXT),
    TextNode("code block", TextType.CODE),
    TextNode(" and an ", TextType.TEXT),
    TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
    TextNode(" and a ", TextType.TEXT),
    TextNode("link", TextType.LINK, "https://boot.dev"),
] )
                                    
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_heading1(self):
        block = "# This is a heading"
        result = block_to_block_type(block)
        self.assertEqual(result, BlockType.HEADING)
    
    def test_heading2(self):
        block = "###### This is a heading"
        result = block_to_block_type(block)
        self.assertEqual(result, BlockType.HEADING)
    
    def test_paragraph(self):
        block = "This is a paragraph"
        result = block_to_block_type(block)
        self.assertEqual(result, BlockType.PARAGRAPH)
    
    def test_code(self):
        block = "```\nThis is a code```"
        result = block_to_block_type(block)
        self.assertEqual(result, BlockType.CODE)

    def test_quote(self):
        block = "> this\n> is\n> a quote"
        result = block_to_block_type(block)
        self.assertEqual(result, BlockType.QUOTE)
    
    def test_unorderedlist(self):
        block = "- this\n- is\n- an unordered\n- list"
        result = block_to_block_type(block)
        self.assertEqual(result, BlockType.UNORDERED_LIST)

    def test_orderedlist(self):
        block = "1. this\n2. is an\n3. ordered list"
        result = block_to_block_type(block)
        self.assertEqual(result, BlockType.ORDERED_LIST)
        
    def test_paragraphs(self):
            md = """
        This is **bolded** paragraph
        text in a p
        tag here

        This is another paragraph with _italic_ text and `code` here

        """

            node = markdown_to_html_node(md)
            html = node.to_html()
            self.assertEqual(
                html,
                "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
            )

    def test_codeblock(self):
            md = """
        ```
        This is text that _should_ remain
        the **same** even with inline stuff
        ```
        """

            node = markdown_to_html_node(md)
            html = node.to_html()
            self.assertEqual(
                html,
                "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
            )

    def test_orderedlists(self):
        md = "1. this\n2. is an\n3. ordered list"
        

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
                html,
                "<div><ol><li>this</li><li>is an</li><li>ordered list</li></ol></div>",
            )
    def test_unorderedlists(self):
        md = "- this\n- is an\n- unordered list"
        

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
                html,
                "<div><ul><li>this</li><li>is an</li><li>unordered list</li></ul></div>",
            )
    def test_paragraphs(self):
        md = "this is an _italic_ paragraph"

        node= markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html , "<div><p>this is an <i>italic</i> paragraph</p></div>")
    
    def test_headers1(self):
        md = "# 1"

        node= markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html , "<div><h1>1</h1></div>")

    def test_headers6(self):
        md = "###### 6"

        node= markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html , "<div><h6>6</h6></div>")
    
    def test_quotes(self):
        md = "> this is\n> a quote\n"

        node= markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html , "<div><blockquote>this is a quote</blockquote></div>")
if __name__ == "__main__":
    unittest.main()
