import xml.etree.ElementTree as xml_ET
from xmljson import badgerfish
import json
import base64
import pickle

# todo !!! Для всех списков параметров проверить чтобы они не повторялись (чтобы дважды не совать в xml)

# todo !!!     Если в атрибут сначала записывался дескриптор декоратора @property а за ним @"property.setter"
# todo !!! то атрибуту уже передается новый дескриптор полученный от @"property.setter" а старый затирается
# todo !!! и его старый вариант уже не доступен !!! (на его месте уже новый объект дескриптора!!!)
# todo !!! ПОЭТОМУ или переделывать под сохранение в атрибутах моих дескрипторов (переделанных из @property)
# todo !!! или искать другой вариант ((( или @"property.setter" тоже оборачивать в @ObjTreeToXml.property

# todo !!!! Добавить код сохранения данных xml в БД (PostgreSQL или другие)

"""
todo:
1. Введение в работу с pgSQl
-2. Фабрика классов в Python (регенерация дерева объектов и классов по данным xml)  (mb тема метаклассов?)
   https://refactoring.guru/ru/design-patterns/abstract-factory
   https://refactoring.guru/ru/design-patterns/abstract-factory/python/example
+3. Парсинг xml
4. ORM SQLAlchemy/  Django ORM
5. xml -> DB
6. xml ->
"""

"""
теги свойств prop_name и type - зарезервированы  (возможно еще и UID )!!!! 

"""


class ObjTreeToXml:  # todo Переименовать класс и исходн файл тк добавил JSON
    """
      Подмешиваемый класс к классам, создающим связанные в древовидную структуру объекты. Добавляет возможность
    сохранения всего дерева в xml с указанием какие конкретно атрибуты объектов нужно сохранить. Атрибуты для
    сохранения в xml отмечаются декораторами для дескрипторов свойств объектов (@property) @ObjTreeToXml.property
    @ObjTreeToXml.property_b64 @ObjTreeToXml.property_serialize_and_b64.
      Для отметки свойства, используемого как уникальный идентификатор объекта - декоратор @ObjTreeToXml.prop_uid
    Свойство с родителем - @ObjTreeToXml.prop_parent, свойство со списком детей - @ObjTreeToXml.prop_childs
      Атрибут объекта в xml "Class" устанавливается автоматически по названию класса объекта.
      Каждому свойству можно добавить дополнительные атрибуты для записи в xml с использованием декоратора
    @ObjTreeToXml.tags_for_prop
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
        ObjTreeToXml.__props_to_obj_header.add(wrapped)  # todo !! добавить проверку на единственность для ДАННОГО класса

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
        ObjTreeToXml.__childs_for_xml.add(wrapped)  # todo !! добавить проверку на единственность для ДАННОГО класса

        # Возвращает тоже свойство (ничего не меняет)
        return wrapped

    @staticmethod
    def tags_for_prop(**tags):
        """
            Декоратор определяющий каким свойствам (оно обязательно должно быть @property) нужно указать какие доп.
        пометки для внесения в xml.
            Декорируемое свойство уже должно быть помечено как @ObjTreeToXml.property или @ObjTreeToXml.property_b64
        :param tags: словарь тегов (имя=значение)
        :return:
        """
        def make_tag(wrapped):  # wrapped - объект дескриптора которому ставится пометка
            # Основной функциорнал по учету свойств
            assert isinstance(wrapped, property)  # Декоратор применяется только к свойствам (класс property)
            # Теги ставятся толко свойствам помеченным как @ObjTreeToXml.property или @ObjTreeToXml.property_b64
            assert wrapped in (  # @ObjTreeToXml.property или @ObjTreeToXml.property_b64 или
                    ObjTreeToXml.__props_for_xml |
                    ObjTreeToXml.__props_b64_xml |
                    ObjTreeToXml.__props_serialize_and_b64
            )  # @ObjTreeToXml.property или @ObjTreeToXml.property_b64 или @ObjTreeToXml.property_serialize_and_b64

            if wrapped not in ObjTreeToXml.__prop_tags:  # Если конкретному декоратору не принадлежало раньше тегов
                ObjTreeToXml.__prop_tags[wrapped] = dict()  # то создаем запись в словаре для словаря будущих тегов

            ObjTreeToXml.__prop_tags[wrapped].update(tags)   # дескриптору в список добавляется пометка

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
        ObjTreeToXml.__props_for_xml.add(wrapped)

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
        ObjTreeToXml.__props_b64_xml.add(wrapped)

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
        ObjTreeToXml.__props_serialize_and_b64.add(wrapped)

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
        if prop in ObjTreeToXml.__prop_tags:  # Если для свойства существуют пометки
            for tag_name, tag_value in ObjTreeToXml.__prop_tags[prop].items():
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
        for prop, attr_name in ObjTreeToXml.__iter_props(self):  # Итерируем по свойствам (property) объекта
            if prop in ObjTreeToXml.__props_to_obj_header:       # если это свойство в списке для внесения в Obj header
                attr_value = prop.fget(self)                     # извлекаем значение атрибута объекта
                xml_of_this_obj.set(attr_name, attr_value)

        # enumerate and adding properties
        # xml_obj_properties = xml_ET.SubElement(xml_of_this_obj, "properties")
        for prop, attr_name in ObjTreeToXml.__iter_props(self):     # Итерируем по свойствам (property) объекта
            if prop in ObjTreeToXml.__props_for_xml:                # если это свойство в списке для внесения в xml
                attr_value = prop.fget(self)                        # извлекаем значение атрибута объекта
                property_element = xml_ET.SubElement(xml_of_this_obj, "property")  # каждому свойству - элемент xml
                property_element.set('prop_name', attr_name)
                property_element.text = str(attr_value)
                if type(attr_value) != str:                         # Тип параметра указывается если он не строка
                    property_element.set('type', str(type(attr_value)))

                # Для свойства ищем теги и добавляем к элементу
                ObjTreeToXml.__add_prop_tag_to_element(property_element, prop)


        # enumerate and adding properties to base64
        for prop, attr_name in ObjTreeToXml.__iter_props(self):     # Итерируем по свойствам (property) объекта
            if prop in ObjTreeToXml.__props_b64_xml:                # если это свойство в списке для внесения в base64
                attr_value = prop.fget(self)                        # извлекаем значение атрибута объекта
                property_element = xml_ET.SubElement(xml_of_this_obj, "property")  # каждому свойству - элемент xml
                property_element.set('prop_name', attr_name)
                property_element.text = base64.b64encode(attr_value).decode("UTF-8")
                property_element.set('type', 'base64_encoded')

                # Для свойства ищем теги и добавляем к элементу
                ObjTreeToXml.__add_prop_tag_to_element(property_element, prop)

        # enumerate and adding properties to serialize and b64
        for prop, attr_name in ObjTreeToXml.__iter_props(self):     # Итерируем по свойствам (property) объекта
            if prop in ObjTreeToXml.__props_serialize_and_b64:      # если это свойство в списке для внесения в base64
                attr_value = prop.fget(self)                        # извлекаем значение атрибута объекта
                #sub_element = xml_ET.SubElement(xml_obj_properties, attr_name)
                property_element = xml_ET.SubElement(xml_of_this_obj, "property")  # каждому свойству - элемент xml
                property_element.set('prop_name', attr_name)
                property_element.text = base64.b64encode(pickle.dumps(attr_value)).decode("UTF-8")
                property_element.set('type', 'pickle_encoded base64_encoded')

                # Для свойства ищем теги и добавляем к элементу
                ObjTreeToXml.__add_prop_tag_to_element(property_element, prop)

        # enumerate childs
        childs_element = xml_ET.SubElement(xml_of_this_obj, "childs")  # каждому свойству - элемент xml
        for prop, attr_name in ObjTreeToXml.__iter_props(self):  # Итерируем по свойствам (property) объекта
            if prop in ObjTreeToXml.__childs_for_xml:            # если это свойство в списке свойст-ссылок на детей
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
 Для записи в таблицу старого типа можно помечать определенные атрибуты с помощью тега (@ObjTreeToXml.tags_for_prop)
for_old_DB="True". Параметры будут извлекаться по ним и добавляться 
"""

"""
Можно насоздавать таблиц по именам классов объектов со столбцами (UID, prop,prop,prop.....)
и добавит две таблицы связей - childs и parents:
childs = UID, child_UID (Если одному UID соответствует несколько child_UID, то создается несколько строк с одним UID)
parents = UID, parent_UID (Если одному UID соответствует несколько parent_UID, то создается несколько строк с одним UID)

также добавить Processing info:
UID| Текст информации обработки (напр. вывод распаковки архива итд)

также добавить Detect info:
UID| Rule Text| Rule file| простр имен| rule ver .... (для него можно создать отдельный класс листа) 
"""

##########################################################################
##########################################################################
##########################################################################
##########################################################################

"""
https://gadjimuradov.ru/post/sqlalchemy-dlya-novichkov/


from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

DeclarativeBase = declarative_base()


class Post(DeclarativeBase):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    name = Column('name', String)
    url = Column('url', String)

    def __repr__(self):
        return "".format(self.code)

"""

# todo Проследить чтобы поступающих в xml объектах присутствовали все необходимые атрибуты (даже пустые). Это необходимо
#      для того чтобы корректно создавались поля новых классов.

# todo а для информации parent закинуть в один из property (Надо смотреть как работают связи в ORM)


class XmlToObjTree:
    classes = {}  # Список классов, которые ранее были получены из xml сгенерированы их суррогаты

    def __init__(self, xml_str):
        """
        Инициализирует объект строкой xml
        :param xml_str:
        """
        self.__xml_str = xml_str

    # todo Попробую пока функцию - фабрику, а потом нужно попробовать с метаклассами (а нужны ли они сдесь?)
    @staticmethod
    def __get_class(class_name, props):
        """
        Возвращает класс с указанным именем из созданых ранее. Если ранее не создавался - генерирует класс на основе
        переданного списка атрибутов
        :param class_name: имя класса
        :param props: словарь свойств класса с атрибутами
        :return:
        """
        if class_name in XmlToObjTree.classes:  # Если такой класс уже был опред. то мы берем его из ранее определенных
            return XmlToObjTree.classes[class_name]

        class Surrogate:
            """
            Класс от которого наследуются все создаваемые из xml классы. Имеет метод инициализации по полученным из xml
            параметрам . В классе реализовано добавление детей и организация связей с рподительскими объектами.
            """
            __uid = None
            __parent = None
            __childs = []
            __prop_attributes = dict()

            def __init__(self, properties):
                """
                Объекты инициализируются параметрами(property), полученными из xml
                :param properties:
                """
                self.__uid = None  # todo !!!   + добавить возможность включать в xml сериализованные декодеры.
                self.__prop_attributes = dict()
                for property_name in properties:  # просматриваем все свойства объекта xml
                    prop_value, prop_attrs = properties[property_name]  # Извлекаем значение и атрибуты свойства
                    self.__prop_attributes[property_name] = prop_attrs  # заполняем словарь свойств и их атрибутов

                    if 'type' in prop_attrs:  # Смотрим какие преобразования типов необходимо произвести
                        attr_type = prop_attrs['type']
                        if attr_type == "<class \'int\'>":  # если int
                            prop_value = int(prop_value)
                        elif attr_type == "pickle_encoded base64_encoded":  # если pickle
                            prop_value = pickle.loads(base64.b64decode(prop_value))
                        elif attr_type == "base64_encoded":  # если pickle
                            prop_value = base64.b64decode(prop_value)

                    setattr(self, property_name, prop_value)  # Заносим каждое свойство в инициализируемый объект

            def add_child(self, child):
                """
                Добавляет ребенка в список порожденных узлов
                :param child:
                :return:
                """
                self.__childs.append(child)
                child.__parent = self

            @property
            def uid(self):  # todo !! Нужно -ли? Зависит от ORM
                return self.__uid

            @property
            def parent(self):
                """
                Возвращает объект родителя
                :return:
                """
                return self.__parent

            @property
            def childs(self):
                """
                Возвращает список детей
                :return:
                """
                return self.__childs

            @property
            def props_attributes(self):
                """
                Возвращает словарь с атрибутами для каждого свойства из xml
                :return:
                """
                return self.__prop_attributes

        cls = type(class_name, (Surrogate,), {})  # создает класс с указанным именем (а по структуре как Surrogate).

        for prop_name in props:
            # prop_value, prop_attrs = props[prop_name]
            setattr(cls, prop_name, None)  # Добавляет вновь созданному классу атрибуты из xml

        XmlToObjTree.classes[class_name] = cls  # Добавляем созданный класс в список
        return cls  # возвращаем класс

    @staticmethod
    def __get_obj(obj_element):
        """
        Возвращает объект (с подобъектами - детьми) для данного элемента xml
        :param obj_element: class xml.etree.ElementTree.Element(tag, attrib={}, **extra)
        :return: Объект из xml (с подобъектами - детьми, структура всего дерева)
        """
        class_name = obj_element.get("Class")  # определяем имя класса элемента
        assert class_name  # атрибут Class должен быть у любого объекта
        print(class_name)

        props = {}
        for prop in obj_element.findall(
                "property"):  # проходим по элементам property, принадлежащим только текущ. объекту
            prop_name = prop.attrib.pop("prop_name")  # Извлекаем атрибут имени свойства и удаляем из списка атрибутов
            prop_value = prop.text  # Значение свойства
            prop_attrs = prop.attrib  # атрибуты свойства
            props[prop_name] = (prop_value, prop_attrs)  # запихиваем свойство объекта в словарь !!!!!!!!!!!!!!!!
            print(prop)

        cls = XmlToObjTree.__get_class(class_name, props)  # получаем класс элемента
        obj = cls(props)  # создаем экземпляр полученного класса

        childs_element = obj_element.find("childs")  # находим элемент с вложенными объектами
        for child_obj in childs_element.findall("Object"):  # Обходим все дочерн объекты (но только для данного объекта)
            obj.add_child(XmlToObjTree.__get_obj(child_obj))

        return obj

    def make_obj_tree(self):
        """
        Возвращает дерево объектов из xml
        :return:
        """
        et = xml_ET.fromstring(self.__xml_str)
        obj = XmlToObjTree.__get_obj(et)
        return obj

##########################################################################
##########################################################################
##########################################################################
##########################################################################

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
