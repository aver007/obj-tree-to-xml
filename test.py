import hashlib
from objtreexml import ObjTreeToXml, XmlToObjTree


def one_two_three(xyz):
    print('one..')
    print(xyz)
    print('three..')
    return 'one..' + str(xyz) + 'three..'


def three_two_one(xyz):
    print('one..')
    print(xyz)
    print('three..')
    return '1 + ' + xyz + " + 3"


class SampleBaseClass(ObjTreeToXml):
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

    @parent.setter
    def parent(self, value):
        self.__parent = value

    def addchild(self, child):
        self.__childs.append(child)
        child.__parent = self

    @ObjTreeToXml.prop_childs
    @property
    def childs(self):
        return self.__childs

    @ObjTreeToXml.tags_for_prop(for_old_DB="True")
    @ObjTreeToXml.property
    @property
    def a(self):
        return self.__a

    @ObjTreeToXml.tags_for_prop(for_old_DB="True")
    @ObjTreeToXml.property
    @property
    def b(self):
        return self.__b

    @ObjTreeToXml.property
    @property
    def c(self):
        # Попробуем поработать с int
        return self.__c

    @ObjTreeToXml.prop_to_obj_header
    @ObjTreeToXml.tags_for_prop(nu_etot_samiy_glavniy="vo kak", aga="eshe")
    @ObjTreeToXml.tags_for_prop(UID="True")
    @ObjTreeToXml.tags_for_prop(a_vot_tak="tozhe mozhno")
    @ObjTreeToXml.property
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

    @ObjTreeToXml.prop_to_obj_header
    @ObjTreeToXml.tags_for_prop(da_eshe_first="ClassWithFilename_1", da_eshe_second="ClassWithFilename_2")
    @ObjTreeToXml.tags_for_prop(haha_first="ClassWithFilename_123", haha_second="ClassWithFilename_234")
    @ObjTreeToXml.property
    @property
    def filename(self):
        return self.__filename

    @property
    def writemode(self):
        return self.__writemode

    @ObjTreeToXml.property_encoded(str, int)
    @property
    def return_123(self):
        return 123


class ClassWithTown(SampleBaseClass):
    def __init__(self, a, b, c, town, postcode):
        self.__town = town
        self.__postcode = postcode
        super().__init__(a, b, c)

    @ObjTreeToXml.prop_to_obj_header
    @ObjTreeToXml.property
    @property
    def town(self):
        return self.__town

    @property
    def postcode(self):
        return self.__postcode

    @ObjTreeToXml.tags_for_prop(one ='first', two='second', eshe='nu zachem')
    @ObjTreeToXml.property_b64
    @property
    def binarydata(self):
        return bytes.fromhex("12abcdef")

    @ObjTreeToXml.property_encoded(one_two_three, three_two_one)
    @property
    def listdata(self):
        return [123, 456, 789, bytes.fromhex("12abcdef")]

    @ObjTreeToXml.tags_for_prop(its='vot tak budet perezapisano!!!!!')
    @ObjTreeToXml.tags_for_prop(its='for pickle', whattodo='unbase64 and pickle.loads')
    @ObjTreeToXml.property_serialize_and_b64
    @property
    def serialized_listdata(self):
        return [123, 456, 789, bytes.fromhex("12abcdef")]


if __name__ == "__main__":
    import pickle
    pp = pickle.dumps(one_two_three)
    funct = pickle.loads(pp)
    funct("vot eto da !!!! TWO !!!")


##############################
##############################
##############################

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
        xml_data = xml.read()

    tree = XmlToObjTree(xml_data).make_obj_tree()
    print(tree)









