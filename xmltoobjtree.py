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

classes = {}

# todo попробовать вывести атрибуты объекта просто в properties Object Class="ClassWithTown"
#  UID_attr_name="md5_from_a_b"
#  UID="10d003d943bb12e6e600065636b51b36"
#  parent="4fdd5fc560bbc2801d95f03179160bf5"

# todo Может вообще поубирать этих parent (они и так поидее должны связываться во время создания объектов)
# todo а для информации parent закинуть в один из property (Надо смотреть как работают связи в ORM)
# todo а UID оставить внутри какого-то property (только метку на него поставить UID)


def get_class(class_name, props):
    if class_name in classes:  # Если такой класс уже был определен то мы берем его из ранее определенных
        return classes[class_name]

    class Surrogate:
        __uid = None
        __parent = None
        __childs = []
        __prop_attributes = dict()

        def __init__(self, props):
            self.__uid = None
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
            Добавляет ребенка в список порожденных узлов
            :param child:
            :return:
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

    obj_attrs = obj_element.attrib  # атрибуты объекта !!!!!!!!!!!!!!!!!!!!!
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