

class parent:
    """
    Декоратор, обозначающий свойство - родитель для заноса в XML
    """
    # todo !!! Возможно он и не нужен т.к. итак строится в порядке прохода дерева (+ не должно быть зацикливаней)
    def __init__(self, obj):
        assert type(obj) == property  #  Декоратор применяется только к свойствам (класс property)

        self.__prop = obj
        pass


class childs:
    """
    Декоратор, обозначающий свойство - список детей для заноса в XML
    """
    def __init__(self, obj):
        assert type(obj) == property  #  Декоратор применяется только к свойствам (класс property)

        self.__prop = obj
        pass


class prop:
    """
    Декоратор, обозначающий свойство для заноса в XML
    """
    def __init__(self, obj):
        assert type(obj) == property  #  Декоратор применяется только к свойствам (класс property)

        self.__prop = obj
        pass


class ObjTreeToXML:
    """
    Базовый класс
    """
    def __init__(self):
        # инициализируем переменные, которые будут хранить списки на добавку в XML
        self.__prop_parent = None
        self.__prop_childs = []
        self.__prop_properties = []


        pass
        self.__initialised_objtreetoxml = True

    def __check_props(self):
        """
        Проходит по всем свойствам (@property) класса - потомка
        и помеченные декораторами включает в список на добавку в XML
        :return:
        """
        pass

    def generate_xml(self):
        assert self.__initialised_objtreetoxml  # Проверка была ли инициализация структур класса ObjTreeToXML

        self.__check_props()  # Заполняет список нужных параметров для заноса в XML
        pass
