# Full Disclosure: this patch method was taken from stack overflow
def xml_write_patch(method):
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
