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


def get_class(xml_object_sample):
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



    """
    Surrogate.__class__.__name__ = xml_object_sample.class_name
    Surrogate.
    """

    return Surrogate

#A = get_A()
#B = get_A()


def iter_objects_in_xml(xml_str):
    et = xml_ET.fromstring(xml_str)
    for element in et.iter(tag="Object"):  # Обходим все элементы Object
        print(element)


