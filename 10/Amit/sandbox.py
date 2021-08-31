from lxml import etree
from lxml.etree import Element

if __name__ == '__main__':
    root = Element("root")
    empty_element = Element("empty")
    root.append(empty_element)
    class_tree = etree.ElementTree(root)
    class_tree.write("output1.xml", pretty_print=True)  # work
    class_tree.write("output2.xml", method="html")  # work
    class_tree.write("output3.xml", pretty_print=True, method="html")  # don't work together
