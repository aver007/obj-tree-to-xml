#!python

# objtreexml

# todo !!! Для всех списков параметров проверить чтобы они не повторялись (чтобы дважды не совать в xml)

# todo !!!     Если в атрибут сначала записывался дескриптор декоратора @property а за ним @"property.setter"
# todo !!! то атрибуту уже передается новый дескриптор полученный от @"property.setter" а старый затирается
# todo !!! и его старый вариант уже не доступен !!! (на его месте уже новый объект дескриптора!!!)
# todo !!! ПОЭТОМУ или переделывать под сохранение в атрибутах моих дескрипторов (переделанных из @property)
# todo !!! или искать другой вариант ((( или @"property.setter" тоже оборачивать в @ObjTreeToXML.property

# todo !!!! Добавить код сохранения данных xml в БД (PostgreSQL или другие)

"""
todo:
1. Введение в работу с pgSQl
2. Фабрика классов в Python (регенерация дерева объектов и классов по данным xml)  (mb тема метаклассов?)
   https://refactoring.guru/ru/design-patterns/abstract-factory
   https://refactoring.guru/ru/design-patterns/abstract-factory/python/example
3. Парсинг xml
4. ORM SQLAlchemy/  Django ORM
5. xml -> DB
6. xml ->
"""

"""
теги свойств prop_name и type - зарезервированы  (возможно еще и UID )!!!! 

"""

import xml.etree.ElementTree as xml_ET
from xmljson import badgerfish
import json
import base64
import pickle


class ObjTreeToXML:  # todo Переименовать класс и исходн файл тк добавил JSON
    """
      Подмешиваемый класс к классам, создающим связанные в древовидную структуру объекты. Добавляет возможность
    сохранения всего дерева в xml с указанием какие конкретно атрибуты объектов нужно сохранить. Атрибуты для
    сохранения в xml отмечаются декораторами для дескрипторов свойств объектов (@property) @ObjTreeToXML.property
    @ObjTreeToXML.property_b64 @ObjTreeToXML.property_serialize_and_b64.
      Для отметки свойства, используемого как уникальный идентификатор объекта - декоратор @ObjTreeToXML.prop_uid
    Свойство с родителем - @ObjTreeToXML.prop_parent, свойство со списком детей - @ObjTreeToXML.prop_childs
      Атрибут объекта в xml "Class" устанавливается автоматически по названию класса объекта.
      Каждому свойству можно добавить дополнительные атрибуты для записи в xml с использованием декоратора
    @ObjTreeToXML.tags_for_prop
    """
    __childs_for_xml = set()
    __prop_tags = {}
    __props_for_xml = set()
    __props_b64_xml = set()
    __props_serialize_and_b64 = set()
    __props_to_obj_header = set()

    @staticmethod
    def prop_to_obj_header(wrapped):
        """
        Декоратор определяющий свойство, которое можно добавить в заголовок объекта в xml.
        Рекомендуется такие свойства выбирать из тех, которые уже определены в список свойств для xml.
        :param wrapped: Декорируемый параметр
        :return: Декорируемый параметр
        """
        # Основной функциорнал по учету свойства
        assert isinstance(wrapped, property)  # Декоратор применяется только к свойствам (класс property)
        ObjTreeToXML.__props_to_obj_header.add(wrapped)  # todo !! добавить проверку на единственность для ДАННОГО класса

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

    @staticmethod
    def tags_for_prop(**tags):
        """
            Декоратор определяющий каким свойствам (оно обязательно должно быть @property) нужно указать какие доп.
        пометки для внесения в xml.
            Декорируемое свойство уже должно быть помечено как @ObjTreeToXML.property или @ObjTreeToXML.property_b64
        :param tags: словарь тегов (имя=значение)
        :return:
        """
        def make_tag(wrapped):  # wrapped - объект дескриптора которому ставится пометка
            # Основной функциорнал по учету свойств
            assert isinstance(wrapped, property)  # Декоратор применяется только к свойствам (класс property)
            # Теги ставятся толко свойствам помеченным как @ObjTreeToXML.property или @ObjTreeToXML.property_b64
            assert wrapped in (  # @ObjTreeToXML.property или @ObjTreeToXML.property_b64 или
                    ObjTreeToXML.__props_for_xml |
                    ObjTreeToXML.__props_b64_xml |
                    ObjTreeToXML.__props_serialize_and_b64
            )  # @ObjTreeToXML.property или @ObjTreeToXML.property_b64 или @ObjTreeToXML.property_serialize_and_b64

            if wrapped not in ObjTreeToXML.__prop_tags:  # Если конкретному декоратору не принадлежало раньше тегов
                ObjTreeToXML.__prop_tags[wrapped] = dict()  # то создаем запись в словаре для словаря будущих тегов

            ObjTreeToXML.__prop_tags[wrapped].update(tags)   # дескриптору в список добавляется пометка

            # Возвращает тоже свойство (ничего не меняет)
            return wrapped

        return make_tag

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
    def property_b64(wrapped):
        """
        Декоратор определяющий свойство (оно обязательно должно быть @property) значение которого
        при сохранении в xml будет закодировано в base64

        :param wrapped: Декорируемый параметр
        :return: Декорируемый параметр
        """
        # Основной функциорнал по учету свойств
        assert isinstance(wrapped, property)  # Декоратор применяется только к свойствам (класс property)
        ObjTreeToXML.__props_b64_xml.add(wrapped)

        # Возвращает тоже свойство (ничего не меняет)
        return wrapped

    @staticmethod
    def property_serialize_and_b64(wrapped):
        """
        Декоратор определяющий свойство (оно обязательно должно быть @property) значение которого
        при сохранении в xml будет сериализовано

        :param wrapped: Декорируемый параметр
        :return: Декорируемый параметр
        """
        # Основной функциорнал по учету свойств
        assert isinstance(wrapped, property)  # Декоратор применяется только к свойствам (класс property)
        ObjTreeToXML.__props_serialize_and_b64.add(wrapped)

        # Возвращает тоже свойство (ничего не меняет)
        return wrapped

    @staticmethod
    def __add_prop_tag_to_element(element, prop):
        """
          Ищет пометки установленные для указанного свойства и записывает их в указанный элемент xml
        :param element: элемент xml
        :param prop: свойство для которого искать пометки
        :return:
        """
        if prop in ObjTreeToXML.__prop_tags:  # Если для свойства существуют пометки
            for tag_name, tag_value in ObjTreeToXML.__prop_tags[prop].items():
                element.set(tag_name, tag_value)

    def __iter_props(self):
        """
        Итератор по свойствам (@property) класса объекта
        :return: tuple(Очередной дескриптор класса объекта, имя атрибута)
        """
        for class_attr_name in dir(self.__class__):          # Проходим по именам атрибутов текущего объекта (из класса)
            prop_descriptor = getattr(self.__class__, class_attr_name)  # получаем очер. атрибут (property берется
                                                                        # только из класса)
            if isinstance(prop_descriptor, property):                   # проверяем чтобы он был свойством (property)
                yield prop_descriptor, class_attr_name                  # возвращаем дескриптор св-ва и имя атрибута

    def __xml_element(self):
        """
          Возвращает объект xml.etree.ElementTree.Element для объекта дерева вместе с порождаемыми объектами до
        самого конца дерева.
        :return: xml.etree.ElementTree.Element()
        """
        xml_of_this_obj = xml_ET.Element("Object")  # Имя раздела в xml определяется по имени класса
        xml_of_this_obj.set("Class", self.__class__.__name__)

        # adding props to show in Object header
        for prop, attr_name in ObjTreeToXML.__iter_props(self):  # Итерируем по свойствам (property) объекта
            if prop in ObjTreeToXML.__props_to_obj_header:       # если это свойство в списке для внесения в Obj header
                attr_value = prop.fget(self)                     # извлекаем значение атрибута объекта
                xml_of_this_obj.set(attr_name, attr_value)

        # enumerate and adding properties
        # xml_obj_properties = xml_ET.SubElement(xml_of_this_obj, "properties")
        for prop, attr_name in ObjTreeToXML.__iter_props(self):     # Итерируем по свойствам (property) объекта
            if prop in ObjTreeToXML.__props_for_xml:                # если это свойство в списке для внесения в xml
                attr_value = prop.fget(self)                        # извлекаем значение атрибута объекта
                property_element = xml_ET.SubElement(xml_of_this_obj, "property")  # каждому свойству - элемент xml
                property_element.set('prop_name', attr_name)
                property_element.text = str(attr_value)
                if type(attr_value) != str:                         # Тип параметра указывается если он не строка
                    property_element.set('type', str(type(attr_value)))

                # Для свойства ищем теги и добавляем к элементу
                ObjTreeToXML.__add_prop_tag_to_element(property_element, prop)


        # enumerate and adding properties to base64
        for prop, attr_name in ObjTreeToXML.__iter_props(self):     # Итерируем по свойствам (property) объекта
            if prop in ObjTreeToXML.__props_b64_xml:                # если это свойство в списке для внесения в base64
                attr_value = prop.fget(self)                        # извлекаем значение атрибута объекта
                property_element = xml_ET.SubElement(xml_of_this_obj, "property")  # каждому свойству - элемент xml
                property_element.set('prop_name', attr_name)
                property_element.text = base64.b64encode(attr_value).decode("UTF-8")
                property_element.set('type', 'base64_encoded')

                # Для свойства ищем теги и добавляем к элементу
                ObjTreeToXML.__add_prop_tag_to_element(property_element, prop)

        # enumerate and adding properties to serialize and b64
        for prop, attr_name in ObjTreeToXML.__iter_props(self):     # Итерируем по свойствам (property) объекта
            if prop in ObjTreeToXML.__props_serialize_and_b64:      # если это свойство в списке для внесения в base64
                attr_value = prop.fget(self)                        # извлекаем значение атрибута объекта
                #sub_element = xml_ET.SubElement(xml_obj_properties, attr_name)
                property_element = xml_ET.SubElement(xml_of_this_obj, "property")  # каждому свойству - элемент xml
                property_element.set('prop_name', attr_name)
                property_element.text = base64.b64encode(pickle.dumps(attr_value)).decode("UTF-8")
                property_element.set('type', 'pickle_encoded base64_encoded')

                # Для свойства ищем теги и добавляем к элементу
                ObjTreeToXML.__add_prop_tag_to_element(property_element, prop)

        # enumerate childs
        childs_element = xml_ET.SubElement(xml_of_this_obj, "childs")  # каждому свойству - элемент xml
        for prop, attr_name in ObjTreeToXML.__iter_props(self):  # Итерируем по свойствам (property) объекта
            if prop in ObjTreeToXML.__childs_for_xml:            # если это свойство в списке свойст-ссылок на детей
                child_list = prop.fget(self)                     # из свойства извлекаем список на объекты детей
                for child in child_list:
                    childs_element.append(child.__xml_element())  # проходим по каждому ребенку рекурсивно

        return xml_of_this_obj

    def get_xml(self):
        """
          Возвращает строку с полной структурой xml текущего объекта.
        :return: str()
        """
        return xml_ET.tostring(self.__xml_element(), encoding="unicode")

    def get_json(self):
        """
          Возвращает строку с полной структурой json текущего объекта. Используется конвенция BadgerFish
        :return: str()
        """
        E_tree = self.__xml_element()
        js = badgerfish.data(E_tree)
        return json.dumps(js)


# todo !!!! Почитать ORM, DOM, XML to DB, SQLAlchemy, Django-ORM
"""
 Для записи в таблицу старого типа можно помечать определенные атрибуты с помощью тега (@ObjTreeToXML.tags_for_prop)
for_old_DB="True". Параметры будут извлекаться по ним и добавляться 
"""

"""
Можно насоздавать таблиц по именам классов объектов со столбцами (UID, prop,prop,prop.....)
и добавит две таблицы связей - childs и parents:
childs = UID, child_UID (Если одному UID соответствует несколько child_UID, то создается несколько строк с одним UID)
parents = UID, parent_UID (Если одному UID соответствует несколько parent_UID, то создается несколько строк с одним UID)

также добавить Processing info:
UID| Текст информации обработки (напр. вывод распаковки архива итд)

также добавить Dete info:
UID| Rule Text| Rule file| простр имен| rule ver .... (для него можно создать отдельный класс листа) 

"""


class XmlToOldDB:
    def __init__(self, xml_str):
        """
        Инициализирует объекты
        :param xml_str:
        """
        pass

    def __write_mssql(self):
        pass

    def write_to_db(self, dbname, user, password):
        """
        Сам выбирает вариант из приведенных выше
        :param dbname:
        :param user:
        :param password:
        :return:
        """
        pass


# todo !!! Или такой вариант ))
def xml_to_db(xml_str, dbname, username, password):
    pass
