#!python

# todo Попробую пока функцию - фабрику, а потом нужно попробовать с метаклассами.
# todo   Проследить чтобы поступающих в xml объектах присутствовали все необходимые атрибуты (даже пустые). Это необходимо
#      для того чтобы корректно создавались поля новых классов.

# https://gadjimuradov.ru/post/sqlalchemy-dlya-novichkov/
"""

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

import xml.etree.ElementTree as xml_ET
import base64
import pickle


# todo а для информации parent закинуть в один из property (Надо смотреть как работают связи в ORM)
class XmlToObjTree:
    classes = {}  # Список классов, которые ранее были получены из xml сгенерированы их суррогаты

    def __init__(self, xml_str):
        """
        Инициализирует объект строкой xml
        :param xml_str:
        """
        self.__xml_str = xml_str

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

            def __init__(self, props):
                """
                Объекты инициализируются параметрами(property), полученными из xml
                :param props:
                """
                self.__uid = None  # todo !!!   + добавить возможность включать в xml сериализованные декодеры.
                self.__prop_attributes = dict()
                for prop_name in props:  # просматриваем все свойства объекта xml
                    prop_value, prop_attrs = props[prop_name]  # Извлекаем значение и атрибуты свойства
                    self.__prop_attributes[prop_name] = prop_attrs  # заполняем словарь свойств и их атрибутов

                    if 'type' in prop_attrs:  # Смотрим какие преобразования типов необходимо произвести
                        attr_type = prop_attrs['type']
                        if attr_type == "<class \'int\'>":  # если int
                            prop_value = int(prop_value)
                        elif attr_type == "pickle_encoded base64_encoded":  # если pickle
                            prop_value = pickle.loads(base64.b64decode(prop_value))
                        elif attr_type == "base64_encoded":  # если pickle
                            prop_value = base64.b64decode(prop_value)

                    setattr(self, prop_name, prop_value)  # Заносим каждое свойство в инициализируемый объект

            def add_child(self, child):
                """
                Добавляет ребенка в список порожденных узлов
                :param child:
                :return:
                """
                self.__childs.append(child)
                child.__parent = self

            @property
            def uid(self): # todo !! Нужно -ли? Зависит от ORM
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


"""
def get_class(class_name, props):
    if class_name in classes:  # Если такой класс уже был определен то мы берем его из ранее определенных
        return classes[class_name]

    class Surrogate:
        __uid = None
        __parent = None
        __childs = []
        __prop_attributes = dict()

        def __init__(self, props):
            self.__uid = None  # todo !!!   + добавить возможность включать в xml сериализованные декодеры.
            self.__prop_attributes = dict()
            for prop_name in props:  # просматриваем все свойства объекта xml
                prop_value, prop_attrs = props[prop_name]  # Извлекаем значение и атрибуты свойства
                self.__prop_attributes[prop_name] = prop_attrs  # заполняем словарь свойств и их атрибутов

                if 'type' in prop_attrs:              # Смотрим какие преобразования типов необходимо произвести
                    attr_type = prop_attrs['type']
                    if attr_type == "<class \'int\'>":  # если int
                        prop_value = int(prop_value)
                    elif attr_type == "pickle_encoded base64_encoded":  # если pickle
                        prop_value = pickle.loads(base64.b64decode(prop_value))
                    elif attr_type == "base64_encoded":  # если pickle
                        prop_value = base64.b64decode(prop_value)

                setattr(self, prop_name, prop_value)  # Заносим каждое свойство в инициализируемый объект

        def add_child(self, child):
            """
"""
            Добавляет ребенка в список порожденных узлов
            :param child:
            :return:
            """
"""
            self.__childs.append(child)
            child.__parent = self

        @property
        def uid(self):
            return self.__uid

        @property
        def parent(self):
            return self.__parent

        @property
        def childs(self):
            return self.__childs

        @property
        def props_attributes(self):
            return self.__prop_attributes

    cls = type(class_name, (Surrogate,), {})  # создает класс с указанным именем.

    for prop_name in props:
        prop_value, prop_attrs = props[prop_name]

        setattr(cls, prop_name, None)

    classes[class_name] = cls   # Добавляем созданный класс в список
    return cls


def __get_obj(obj_element):
    class_name = obj_element.get("Class")  # определяем имя класса элемента
    assert class_name  # атрибут Class должен быть у любого объекта
    print(class_name)

    #obj_attrs = obj_element.attrib  # атрибуты объекта !!!!!!!!!!!!!!!!!!!!!
    props = {}
    for prop in obj_element.findall("property"):  # проходим по элементам property, принадлежащим только текущ. объекту
        prop_name = prop.attrib.pop("prop_name")  # Извлекаем атрибут имени свойства и удаляем из списка атрибутов
        prop_value = prop.text  # Значение свойства
        prop_attrs = prop.attrib  # атрибуты свойства
        props[prop_name] = (prop_value, prop_attrs)  # запихиваем свойство объекта в словарь !!!!!!!!!!!!!!!!
        print(prop)

    cls = get_class(class_name, props)  # получаем класс элемента
    obj = cls(props)                    # создаем экземпляр полученного класса

    childs_element = obj_element.find("childs")  # находим элемент с вложенными объектами
    for child_obj in childs_element.findall("Object"):  # Обходим все дочерн объекты (но только для данного объекта)
        obj.add_child(__get_obj(child_obj))

    return obj


def make_obj_tree(xml_str):
    et = xml_ET.fromstring(xml_str)
    obj = __get_obj(et)
    return obj
            
"""