from xml.dom import minidom


def xml_write_patcher(method):
    def patching(self, *args, **kwargs):
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

    return patching


t.firstChild.__class__.writexml = xml_write_patcher(t.firstChild.__class__.writexml)
