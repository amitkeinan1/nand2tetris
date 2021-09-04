from lxml import etree

def main():
    file_name = "SquareMain"
    syntax_tree = etree.parse(f"amit_tests/{file_name}Extended.xml")
    root = syntax_tree.getroot()

if __name__ == '__main__':
    main()

