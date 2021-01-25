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


def get_class(obj_attrs, props):
    if obj_attrs['Class'] in classes:  # Если такой класс уже был определен то мы берем его из ранее определенных
        return classes[obj_attrs['Class']]

    class Surrogate:
        __UID = None
        __UID_attr = None
        __parent = None
        __childs = []
        __props = dict()

        def __init__(self, obj_attrs, props):
            for prop_name in props:
                prop_value, prop_attrs = props[prop_name]
                if 'type' in prop_attrs:              # Смотрим какие преобразования типов необходимо произвести
                    attr_type = prop_attrs['type']
                    if attr_type == "<class \'int\'>":  # если int
                        prop_value = int(prop_value)
                    elif attr_type == "pickle_encoded base64_encoded":  # если pickle
                        prop_value = pickle.loads(base64.b64decode(prop_value))
                    elif attr_type == "base64_encoded":  # если pickle
                        prop_value = base64.b64decode(prop_value)

                setattr(self, prop_name, prop_value)

        @property
        def uid(self):
            pass

        @property
        def uid_attr(self):
            pass

        @property
        def parent(self):
            # todo КАК? просто UID родителя или всетаки связь с объектом??
            pass

        @property
        def childs(self):
            # todo КАК? просто список UID детей или всетаки связь с объектами??
            pass

    cls = type(obj_attrs['Class'], (Surrogate,), {})  # создает класс с указанным именем.

    for prop_name in props:
        prop_value, prop_attrs = props[prop_name]

        setattr(cls, prop_name, None)

    classes[obj_attrs['Class']] = cls   # Добавляем созданный класс в список
    return cls


def iter_objects_in_xml(xml_str):
    et = xml_ET.fromstring(xml_str)
    for obj in et.iter(tag="Object"):  # Обходим все объекты
        obj_attrs = obj.attrib         # атрибуты объекта !!!!!!!!!!!!!!!!!!!!!
        print(obj)
        props = {}
        for prop in obj.findall("property"):  # проходим по элементам property, принадлежащим только текущему объекту
            prop_name = prop.attrib.pop("prop_name")   # Извлекаем атрибут имени свойства и удаляем из списка атрибутов
            prop_value = prop.text                     # Значение свойства
            prop_attrs = prop.attrib                   # атрибуты свойства
            props[prop_name] = (prop_value, prop_attrs)  # запихиваем свойство объекта в словарь !!!!!!!!!!!!!!!!
            print(prop)

        cls = get_class(obj_attrs, props)
        obj = cls(obj_attrs, props)
        print(cls, obj)
        yield obj



