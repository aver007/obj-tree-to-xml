import hashlib
from objtreetoxml import ObjTreeToXML


class SampleBaseClass(ObjTreeToXML):
    def __init__(self, a, b, c):
        self.__parent = None

        self.__a = a
        self.__b = b
        self.__c = c

        self.__childs = []

        super().__init__()

    @ObjTreeToXML.prop_parent
    @property
    def parent(self):
        return self.__parent

    @parent.setter
    def parent(self, value):
        self.__parent = value

    def addchild(self, child):
        self.__childs.append(child)
        child.__parent = self

    @ObjTreeToXML.prop_childs
    @property
    def childs(self):
        return self.__childs

    @ObjTreeToXML.property
    @property
    def a(self):
        return self.__a

    @property
    def b(self):
        return self.__b

    @ObjTreeToXML.property
    @property
    def c(self):
        # Попробуем поработать с int
        return self.__c

    @ObjTreeToXML.prop_uid
    @ObjTreeToXML.property
    @property
    def md5_from_a_b(self):
        return hashlib.md5((self.a + self.b).encode("UTF-8")).hexdigest()

    @property
    def classname(self):
        return self.__class__.__name__


class ClassWithFilename(SampleBaseClass):
    def __init__(self, a, b, c, filename, writemode):
        self.__filename = filename
        self.__writemode = writemode
        super().__init__(a, b, c)

    @ObjTreeToXML.property
    @property
    def filename(self):
        return self.__filename

    @property
    def writemode(self):
        return self.__writemode


class ClassWithTown(SampleBaseClass):
    def __init__(self, a, b, c, town, postcode):
        self.__town = town
        self.__postcode = postcode
        super().__init__(a, b, c)

    @ObjTreeToXML.property
    @property
    def town(self):
        return self.__town

    @property
    def postcode(self):
        return self.__postcode


if __name__ == "__main__":
    """class Foo(object):
        bar = 'spam'

        def __init__(self):
            self.zlp = 11
            self.__pnh = 99

    print(Foo().__dict__)

    print(*Foo.__dict__)

    exit()
    """

    filename_obj_readme = ClassWithFilename("a-a_readme", "b-b_readme", 98, "Readme.txt", 123456)

    town_obj_kalin = ClassWithTown("a-a", "b-b", 123, "Kaliningrad", 236029)
    town_obj_moscow = ClassWithTown("a-a_moscow", "b-b", 321, "Moscow", 999999)
    filename_obj_readme.addchild(town_obj_kalin)
    filename_obj_readme.addchild(town_obj_moscow)

    base_hz = SampleBaseClass("a-a_BASE", "b-b_BASE", 1000)
    town_obj_petersburg = ClassWithTown("a-a", "b-b_piter", 123, "Saint-Petersburg", 111111)
    base_hz.addchild(town_obj_petersburg)
    base_hz.addchild(filename_obj_readme)

    xml_data = base_hz.get_xml()

    print(xml_data)

    with open('rez.xml', 'w') as rez:
        rez.write(xml_data)








