#!python
# todo !!! Проверить работу при применении к нескольким разным классам, в том числе наследующим друг
# todo     друга (нет ли коллизий списков параметров?)

# todo !!! Для всех списков параметров проверить чтобы они не повторялись (чтобы дважды не совать в xml)

import xml.etree.ElementTree as xml_ET

class ObjTreeToXML:
    """
    Базовый класс
    """
    __props_for_xml = set()
    __parent_for_xml = None
    __childs_for_xml = None

    @staticmethod
    def property(wrapped):
        """
        Декоратор определяющий свойство (оно обязательно должно быть @property)
        :param wrapped: Декорируемый параметр
        :return: Декорируемый параметр
        """
        # Основной функциорнал по учету свойств
        assert isinstance(wrapped, property)  # Декоратор применяется только к свойствам (класс property)
        ObjTreeToXML.__props_for_xml.add(wrapped)

        # Возвращает тоже свойство (ничего не меняет)
        return wrapped

    @staticmethod
    def prop_parent_uid(wrapped):
        """
        Декоратор определяющий свойство, определяющее родительскую ветку (оно обязательно должно быть @property)
        :param wrapped: Декорируемый параметр
        :return: Декорируемый параметр
        """
        # Основной функциорнал по учету свойства
        assert isinstance(wrapped, property)  # Декоратор применяется только к свойствам (класс property)
        ObjTreeToXML.__parent_for_xml = wrapped  # todo !! добавить проверку на единственность для данного класса

        # Возвращает тоже свойство (ничего не меняет)
        return wrapped

    @staticmethod
    def prop_childs(wrapped):
        """
        Декоратор определяющий свойство, определяющее исходящие из объекта ветки (оно обязательно должно быть @property)
        :param wrapped: Декорируемый параметр
        :return: Декорируемый параметр
        """
        # Основной функциорнал по учету свойства
        assert isinstance(wrapped, property)  # Декоратор применяется только к свойствам (класс property)
        ObjTreeToXML.__childs_for_xml = wrapped  # todo !! добавить проверку на единственность для данного класса

        # Возвращает тоже свойство (ничего не меняет)
        return wrapped

    def xml_element(self):
        # todo !!!! Может сделать скрытым???  как def __xml_element(self):
        xml_of_this_obj = xml_ET.Element(self.__class__.__name__)

        # enumerate and adding properties
        for prop_name in dir(self.__class__):             # Проходим по именам атрибутов текущего объекта
            prop = getattr(self.__class__, prop_name)     # получаем этот атрибут
            if isinstance(prop, property):                # проверяем чтобы он был свойством (property)
                if prop in ObjTreeToXML.__props_for_xml:  # если это свойство в списке для внесения в xml
                    name = prop_name
                    value = prop.fget(self)
                    print(name, value)

        # add data about parent obj

        # enumerate childs
        childs = ObjTreeToXML.__childs_for_xml.fget(self)
        for child_obj in ObjTreeToXML.__childs_for_xml:
            xml_of_this_obj.append(child_obj.xml_element())

        return xml_of_this_obj

    def get_xml(self):
        return xml_ET.ElementTree(self.xml_element())


