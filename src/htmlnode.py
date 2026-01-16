class HTMLNode:
    def __init__(self, tag = None,
        value = None,
        children = None,
        props= None):


        self.tag = tag
        self.value = value
        self.children = children
        self.props = props


    def to_html(self):
        raise NotImplementedError("xx")


    def props_to_html(self):
        full_string = ""
        if not self.props:
            return ""
        for key, value in self.props.items():
            temp_str = f' {key}="{value}"'
            full_string += temp_str
        return full_string
        

    def __repr__(self):

        return f"HTMLNode({self.tag}, {self.value}, {self.children}, {self.props})"

class LeafNode(HTMLNode):

    def __init__(self, tag, value, props = None):
        super().__init__(tag, value , None,  props)


    def to_html(self):
        if self.value is None:
            print("DEBUG Leaf with None value:", self.tag, self.props)
            raise ValueError("invalid HTML: no value")
        if self.tag is None:
            return f"{self.value}"
        props_str = self.props_to_html()
        return f'<{self.tag}{props_str}>{self.value}</{self.tag}>'
        
        
    def __repr__(self):

        return f"HTMLNode({self.tag}, {self.value}, {self.props})"
    
class ParentNode(HTMLNode):

    def __init__(self, tag, children, props = None):
        super().__init__(tag, None, children, props)
    
    def to_html(self):
        if not self.tag:
            raise ValueError("Parent node is missing a tag")
        if self.children is None:
            raise ValueError("Children is missing a value")
        nested_string = ""
        for nested_child in self.children:
            nested_string += nested_child.to_html()
        
        return f"<{self.tag}>{nested_string}</{self.tag}>"
            
