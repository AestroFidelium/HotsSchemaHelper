import bs4
import re
import collections
from pprint import pprint


BASIC_TAG = "Desc"
soup = bs4.BeautifulSoup(open("data.xml"), "xml")
HISTORY_TAGS = []

class Tag():
    def __init__(self, soup, parent=None):
        self.soup = soup
        self.parent = parent
        self.name = soup.name
        self.args = {} if isinstance(soup, bs4.NavigableString) else soup.attrs
        self.children = []
        self.params = {}
        self.choice = []
        for child in self.soup.children:
            if child == "\n":
                continue
            self.children.append(Tag(child, self))

        if self not in HISTORY_TAGS:
            HISTORY_TAGS.append(self)
        else:
            old_tag = HISTORY_TAGS[HISTORY_TAGS.index(self)]

            for par, val in self.args.items():
                
                if x := old_tag.params.get(par, None):
                    if isinstance(x, list):
                        if val not in x:
                            x.append(val)
                            old_tag.params.update({par: x})
                    else:
                        if x != val:
                            x = [x, val]
                            old_tag.params.update({par: x})
                else:
                    old_tag.params.update({par: val})

    def __eq__(self, other):
        return self.name == other.name

    def __ne__(self, other):
        return self.name == other.name

    @property
    def args_txt(self):
        return " ".join(['{}="{}"'.format(x, y) for x, y in self.args.items()])

    def __repr__(self):
        return "<{} {}>".format(self.name, " ".join(['{}="{}"'.format(x, y) for x, y in self.args.items()]))


XS_SELECTOR = """ <xs:element name="{}">
    <xs:complexType>
      {}
    </xs:complexType>
  </xs:element>"""

XS_CHOICE = """<xs:choice minOccurs="0" maxOccurs="unbounded">
        {}
      </xs:choice>"""
XS_ELEMENT = """<xs:element ref="{}"/>"""

XS_ATTRIBUTE = """<xs:attribute name="{}" use="{}">
        <xs:simpleType>
          <xs:union memberTypes="{}">
            <xs:simpleType>
              <xs:restriction base="{}">
                {}
              </xs:restriction>
            </xs:simpleType>
          </xs:union>
        </xs:simpleType>
      </xs:attribute>"""

XS_ENUMERATION = """<xs:enumeration value="{}"/>"""


def tag_install(x):
    if x in ["name", "val", "type", "value", "frame", "action", "event", "time", "index"]:
        return "required"
    else:
        return "optional"
    # return "optional", "required"

def main():
    first_tag = Tag(soup.find(BASIC_TAG))

    for h_tag in HISTORY_TAGS:
        if h_tag.params == {}:
            h_tag.params = h_tag.args
        try:
            catch_tag = HISTORY_TAGS[HISTORY_TAGS.index(h_tag.parent)]
            if h_tag not in catch_tag.choice:
                catch_tag.choice.append(h_tag)
        except:
            pass

    with open("hots copy.xsd", "w", encoding="utf-8") as file:

        main = """<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
{}
</xs:schema>"""
        outputs = []
        for h_tag in HISTORY_TAGS:
            outputs.append(XS_SELECTOR.format(
                h_tag.name,
                "\n".join([
                    XS_CHOICE.format("\n        ".join(
                        [XS_ELEMENT.format(x.name) for x in h_tag.choice])),
                    "\n".join([XS_ATTRIBUTE.format(x, tag_install(x), "xs:string", "xs:string", "\n                ".join(
                        [XS_ENUMERATION.format(y) for y in h_tag.params[x]])) for x in h_tag.params])
                ])
            ))

        file.write(main.format("\n".join(outputs)))


if __name__ == "__main__":
    main()
