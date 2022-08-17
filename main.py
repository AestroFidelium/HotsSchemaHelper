import bs4
import re

BASIC_TAG = "Desc"

soup = bs4.BeautifulSoup(open("data.xml"), "xml")

class Tag():
    def __init__(self, soup, parent=None):
        self.soup = soup
        self.name = soup.name
        self.parent = parent
        self.args = {} if isinstance(soup, bs4.NavigableString) else soup.attrs
    
    
    def __iter__(self):
        if isinstance(self.soup, bs4.NavigableString):
            return
        
        def wrapper(child_tag, first=False):
            if list(child_tag.soup.children):
                tags = []
                for child in [a for a in child_tag.soup.children if a != "\n"]:
                    tags.append(wrapper(Tag(child, child_tag)))
                # return {child_tag.name + " " + " ".join(["{}='{}'".format(a,child_tag.args[a]) for a in child_tag.args.keys()]):tags}
                tags.append(child_tag.args)
                return {child_tag.name:tags}
            else:
                return child_tag
        
        tags = []
        for child in [a for a in self.soup.children if a != "\n"]:
            tags.append(wrapper(Tag(child, parent=self), first=True))
        # print({self.name:tags})
        yield {str(self.name):tags}
        
    
    
    @property
    def argstext(self):
        return " ".join(['{}="{}"'.format(a,self.args[a]) for a in self.args.keys()])
    
    def __repr__(self):
        return '<{} {}'.format(self.name, " ".join(['{}="{}"'.format(a,self.args[a]) for a in self.args.keys()]))
    



xstemplate = """<xs:element name="{0}">
        <xs:complexType>
            <xs:sequence>
                <xs:choice minOccurs="0" maxOccurs="unbounded">
                    {1}
                </xs:choice>
            </xs:sequence>
            {2}
        </xs:complexType>
    </xs:element>"""


def template(tags):
    for tag in tags:
        if isinstance(tag, Tag):
            output = xstemplate.format(tag.name, "", "".join(['<xs:attribute name="{0}" type="{1}" use="{2}" />'.format(var, "xs:string", "required") for var, _ in tag.args.items()]))
            # print(output,end="\n\n")
        elif isinstance(tag, dict):
            key = next(iter(tag.keys()))
            data = tag[key]
            args = data.pop(-1)
            for var in data:
                if isinstance(var, Tag):
                    print(var)
                else:
                    print(type(var))
            # print("".join(data))
            
            # output = xstemplate.format(key, "", "".join(['<xs:attribute name="{0}" type="{1}" use="{2}" />'.format(var, "xs:string", "required") for var, _ in tag.args.items()]))
            # print(output,end="\n\n")


TagList = []
for tag in soup.find(BASIC_TAG):
    tag = Tag(tag)
    if tag.args.get("name",None) == "HealthBarBackgroundTemplate":
        for _child in list(tag):
            child = _child[next(iter(_child.keys()))]
            # print(child[0].args)
            template(child)
            break