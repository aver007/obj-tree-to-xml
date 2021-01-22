#!python

# todo Попробую пока функцию - фабрику, а потом нужно попробовать с метаклассами.


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


def get_class(obj_attrs, props):
    class Surrogate:
        __UID = None
        __UID_attr = None
        __parent = None
        __childs = []
        __props = dict()

        def __init__(self, input_xml_object):
            pass

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

    cl = obj_attrs["Class"]
    Surrogate.__class__.__name__ = cl  # todo !!! Не работает. Похоже нужно использовать метаклассы !!!!!
    for attr in obj_attrs:
        setattr(Surrogate, "__" + attr, None)

    return Surrogate

#A = get_A()
#B = get_A()


def iter_objects_in_xml(xml_str):
    et = xml_ET.fromstring(xml_str)
    for obj in et.iter(tag="Object"):  # Обходим все объекты
        obj_attrs = obj.attrib         # атрибуты объекта
        print(obj)
        props = {}
        for prop in obj.findall("property"):  # проходим по элементам property, принадлежащим только текущему объекту
            prop_name = prop.attrib.pop("prop_name")   # Извлекаем атрибут имени свойства и удаляем из списка атрибутов
            prop_value = prop.text                     # Значение свойства
            prop_attrs = prop.attrib                   # атрибуты свойства
            props[prop_name] = (prop_value, prop_attrs)  # запихиваем свойство в словарь
            print(prop)

        cls = get_class(obj_attrs, props)
        print(cls)



