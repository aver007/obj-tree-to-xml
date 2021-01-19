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
    __childs_for_xml = set()
    __uids_for_xml = set()

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
        ObjTreeToXML.__parent_for_xml = wrapped  # todo !! добавить проверку на единственность для ДАННОГО класса

        # Возвращает тоже свойство (ничего не меняет)
        return wrapped

    @staticmethod
    def prop_uid(wrapped):
        """
        Декоратор определяющий свойство, используемое как UID (оно обязательно должно быть @property)
        :param wrapped: Декорируемый параметр
        :return: Декорируемый параметр
        """
        # Основной функциорнал по учету свойства
        assert isinstance(wrapped, property)  # Декоратор применяется только к свойствам (класс property)
        ObjTreeToXML.__uids_for_xml.add(wrapped)  # todo !! добавить проверку на единственность для ДАННОГО класса

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
        ObjTreeToXML.__childs_for_xml.add(wrapped)  # todo !! добавить проверку на единственность для ДАННОГО класса

        # Возвращает тоже свойство (ничего не меняет)
        return wrapped

    def xml_element(self):
        # todo !!!! Может сделать скрытым???  как def __xml_element(self):
        xml_of_this_obj = xml_ET.Element(self.__class__.__name__)

        # add uid
        for obj_prop_name in dir(self.__class__):           # Проходим по именам атрибутов текущего объекта (из класса)
            prop = getattr(self.__class__, obj_prop_name)   # получаем очер. атрибут (property берется только из класса)
            if isinstance(prop, property):                  # проверяем чтобы он был свойством (property)
                if prop in ObjTreeToXML.__uids_for_xml:    # если это свойство в списке UID
                    attr_name = obj_prop_name
                    attr_value = prop.fget(self)                  # извлекаем значение атрибута объекта
                    print("UID:", attr_name, attr_value)          # сохраняем
                    xml_of_this_obj.set("UID", str(attr_value))   # todo !! Только так??? со str()???

        # enumerate and adding properties
        for obj_prop_name in dir(self.__class__):           # Проходим по именам атрибутов текущего объекта (из класса)
            prop = getattr(self.__class__, obj_prop_name)   # получаем очер. атрибут (property берется только из класса)
            if isinstance(prop, property):                  # проверяем чтобы он был свойством (property)
                if prop in ObjTreeToXML.__props_for_xml:    # если это свойство в списке для внесения в xml
                    attr_name = obj_prop_name
                    attr_value = prop.fget(self)                      # извлекаем значение атрибута объекта
                    print("property: ", attr_name, attr_value)        # сохраняем
                    xml_of_this_obj.set(attr_name, str(attr_value))   # todo !! Только так??? со str()???

        # add data  about parent obj
        # todo !! (mb only UID)

        # enumerate childs
        for obj_prop_name in dir(self.__class__):           # Проходим по именам атрибутов текущего объекта (из класса)
            prop = getattr(self.__class__, obj_prop_name)   # получаем очер. атрибут (property берется только из класса)
            if isinstance(prop, property):                  # проверяем чтобы он был свойством (property)
                if prop in ObjTreeToXML.__childs_for_xml:   # если это свойство в списке свойст-ссылок на детей
                    child_list = prop.fget(self)            # из свойства извлекаем атрибут - список на объекты детей
                    for child in child_list:
                        print("child:", child)
                        xml_of_this_obj.append(child.xml_element())  # проходим по каждому ребенку рекурсивно

        return xml_of_this_obj

    def get_xml(self):
        xml_elem = self.xml_element()
        return xml_ET.tostring(xml_elem, encoding="unicode")


