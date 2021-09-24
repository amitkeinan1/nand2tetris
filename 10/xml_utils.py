def xml_write_patch(method):
    """
    Full Disclosure: this patch method was taken from stack overflow:
    `https://stackoverflow.com/questions/16813938/
     python-print-pretty-xml-create-opening-and-closing-tags-for-empty-tags-text`
     it is used to allow pretty line by line printing of xmls in which empty elements appear with an opening tag and a
     closing tag, as expected by the tests, and not a single self-closing tag.
    """
    def patch_method(self, *args, **kwargs):
        old = self.childNodes
        try:
            if not self.childNodes:
                class Dummy(list):
                    def __bool__(self):
                        return True

                old, self.childNodes = self.childNodes, Dummy([])
            return method(self, *args, **kwargs)
        finally:
            self.childNodes = old

    return patch_method
