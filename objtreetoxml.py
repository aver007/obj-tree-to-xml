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
    __parent_for_xml = set()
    __childs_for_xml = set()
    __uid_for_xml = set()

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
    def prop_parent(wrapped):
        """
          Декоратор определяющий свойство, определяющее родительскую ветку (оно обязательно должно быть @property)
          В xml добавляется не сам объект - parent, а только его UID, если есть !!!
          Свойство добавлено для удобства последующей обработки полученного xml так как в структуре xml и так видно кто
        чей родитель.
        :param wrapped: Декорируемый параметр
        :return: Декорируемый параметр
        """
        # Основной функциорнал по учету свойства
        assert isinstance(wrapped, property)  # Декоратор применяется только к свойствам (класс property)
        ObjTreeToXML.__parent_for_xml.add(wrapped)  # todo !! добавить проверку на единственность для ДАННОГО класса

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
        ObjTreeToXML.__uid_for_xml.add(wrapped)  # todo !! добавить проверку на единственность для ДАННОГО класса

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

    def __iter_props(self):
        """
        Итератор по свойствам (@property) класса объекта
        :return: tuple(Очередной дескриптор класса объекта, имя атрибута)
        """
        for class_attr_name in dir(self.__class__):          # Проходим по именам атрибутов текущего объекта (из класса)
            prop_descriptor = getattr(self.__class__, class_attr_name)  # получаем очер. атрибут (property берется только из класса)
            if isinstance(prop_descriptor, property):                   # проверяем чтобы он был свойством (property)
                yield prop_descriptor, class_attr_name                  # возвращаем дескриптор св-ва и имя атрибута

    def __xml_element(self):
        xml_of_this_obj = xml_ET.Element("Object")  # Имя раздела в xml определяется по имени класса
        xml_of_this_obj.set("Class", self.__class__.__name__)  # todo !! Только так??? со str()???

        # add UID
        for prop, attr_name in ObjTreeToXML.__iter_props(self):  # Итерируем по свойствам (property) объекта
            if prop in ObjTreeToXML.__uid_for_xml:               # если это свойство в списке UID
                attr_value = prop.fget(self)                     # извлекаем значение атрибута объекта
                print("UID:", attr_name, attr_value)             # сохраняем
                xml_of_this_obj.set("UID_attr_name", str(attr_name))  # todo !! Только так??? со str()???
                xml_of_this_obj.set("UID", str(attr_value))  # todo !! Только так??? со str()???

        # add data about parent obj UID
        for prop, attr_name in ObjTreeToXML.__iter_props(self):  # Итерируем по свойствам (property) объекта
            if prop in ObjTreeToXML.__parent_for_xml:            # если это свойство в списке parents
                print(prop)

        """
        # add data about parent obj UID
        for obj_prop_name in dir(self.__class__):          # Проходим по именам атрибутов текущего объекта (из класса)
            prop = getattr(self.__class__, obj_prop_name)  # получаем очер. атрибут (property берется только из класса)
            if isinstance(prop, property):                 # проверяем чтобы он был свойством (property)

                
                for par_descriptor in ObjTreeToXML.__parent_for_xml:
                    val = par_descriptor.fget(self)
                if prop in ObjTreeToXML.__parent_for_xml:  # если это свойство в списке parents
                    attr_name = obj_prop_name              # todo !! Убрать (не используется)
                    attr_value = prop.fget(self)           # извлекаем значение атрибута объекта (ссылку на родителя)
                    parent_UID = 00
                    print("parent UID:", attr_name, attr_value)   # сохраняем
                    xml_of_this_obj.set("parent UID", str(attr_value))  # todo !! Только так??? со str()???
        """

        # enumerate and adding properties
        xml_obj_properties = xml_ET.SubElement(xml_of_this_obj, "properties")
        for prop, attr_name in ObjTreeToXML.__iter_props(self):     # Итерируем по свойствам (property) объекта
            if prop in ObjTreeToXML.__props_for_xml:                # если это свойство в списке для внесения в xml
                attr_value = prop.fget(self)                        # извлекаем значение атрибута объекта
                print("property: ", attr_name, attr_value)          # сохраняем
                sub_element = xml_ET.SubElement(xml_obj_properties, attr_name)
                sub_element.text = str(attr_value)
                sub_element.set('type', str(type(attr_value)))

        # enumerate childs
        for prop, attr_name in ObjTreeToXML.__iter_props(self):  # Итерируем по свойствам (property) объекта
            if prop in ObjTreeToXML.__childs_for_xml:            # если это свойство в списке свойст-ссылок на детей
                child_list = prop.fget(self)                     # из свойства извлекаем список на объекты детей
                for child in child_list:
                    print("child:", child)
                    xml_of_this_obj.append(child.__xml_element())  # проходим по каждому ребенку рекурсивно

        return xml_of_this_obj

    def get_xml(self):
        xml_elem = self.__xml_element()
        return xml_ET.tostring(xml_elem, encoding="unicode")


