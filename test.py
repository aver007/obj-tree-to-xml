import hashlib
from objtreetoxml import ObjTreeToXML
import xmltoobjtree


class SampleBaseClass(ObjTreeToXML):
    def __init__(self, a, b, c):
        self.__parent = None

        self.__a = a
        self.__b = b
        self.__c = c

        self.__childs = []

        super().__init__()

    @property
    def parent(self):
        return self.__parent

    @ObjTreeToXML.prop_parent
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

    @ObjTreeToXML.tags_for_prop(for_old_DB="True")
    @ObjTreeToXML.property
    @property
    def a(self):
        return self.__a

    @ObjTreeToXML.tags_for_prop(for_old_DB="True")
    @ObjTreeToXML.property
    @property
    def b(self):
        return self.__b

    @ObjTreeToXML.property
    @property
    def c(self):
        # Попробуем поработать с int
        return self.__c

    @ObjTreeToXML.tags_for_prop(nu_etot_samiy_glavniy="vo kak", aga="eshe")
    @ObjTreeToXML.prop_uid
    @ObjTreeToXML.tags_for_prop(a_vot_tak="tozhe mozhno")
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

    @ObjTreeToXML.tags_for_prop(da_eshe_first="ClassWithFilename_1", da_eshe_second="ClassWithFilename_2")
    @ObjTreeToXML.tags_for_prop(haha_first="ClassWithFilename_123", haha_second="ClassWithFilename_234")
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

    @ObjTreeToXML.tags_for_prop(one ='first', two='second', eshe='nu zachem')
    @ObjTreeToXML.property_b64
    @property
    def binarydata(self):
        return bytes.fromhex("12abcdef")

    @ObjTreeToXML.property
    @property
    def listdata(self):
        return [123, 456, 789, bytes.fromhex("12abcdef")]

    @ObjTreeToXML.tags_for_prop(its='vot tak budet perezapisano!!!!!')
    @ObjTreeToXML.tags_for_prop(its='for pickle', whattodo='unbase64 and pickle.loads')
    @ObjTreeToXML.property_serialize_and_b64
    @property
    def serialized_listdata(self):
        return [123, 456, 789, bytes.fromhex("12abcdef")]


if __name__ == "__main__":

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
    json_data = base_hz.get_json()

    print(xml_data)

    with open('rez.xml', 'w') as rez:
        rez.write(xml_data)

    with open('rez.json', 'w') as rez:
        rez.write(json_data)

##########################################################

    with open('rez.xml', 'r') as xml:
        xml_tata = xml.read()

    for obj_from_xml in xmltoobjtree.iter_objects_in_xml(xml_data):
        print(obj_from_xml)











