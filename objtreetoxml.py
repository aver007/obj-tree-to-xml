

class Parent:
    """
    Декоратор, обозначающий свойство - родитель для заноса в XML
    """
    # todo !!! Возможно он и не нужен т.к. итак строится в порядке прохода дерева (+ не должно быть зацикливаней)
    def __init__(self, obj):
        assert type(obj) == property  #  Декоратор применяется только к свойствам (класс property)

        self.__prop = obj
        pass


class Childs:
    """
    Декоратор, обозначающий свойство - список детей для заноса в XML
    """
    def __init__(self, obj):
        assert type(obj) == property  #  Декоратор применяется только к свойствам (класс property)

        self.__prop = obj
        pass


class Prop:
    """
    Декоратор, обозначающий свойство для заноса в XML
    """
    def __init__(self, obj):
        assert type(obj) == property  # Декоратор применяется только к свойствам (класс property)

        self.__prop = obj
        pass

    def __getattr__(self, attr):
        return getattr(self.__prop, attr)  # Возвращение свойств обернутого объекта

    def __repr__(self):
        return str(self.__prop)


class ObjTreeToXML:
    """
    Базовый класс
    """
    def __init__(self):
        # инициализируем переменные, которые будут хранить списки на добавку в XML
        self.__prop_parent = None
        self.__prop_childs = []
        self.__prop_properties = []

        self.__check_props()
        self.__initialised_objtreetoxml = True

    def __check_props(self):
        """
        Проходит по всем свойствам (@property) класса - потомка
        и помеченные декораторами включает в список на добавку в XML
        :return:
        """
        for pr in dir(self):
            # итерация по всем атрибутам объекта
            ty = type(getattr(self, pr))
            if ty == Prop:
                # если текущий атрибут - декоратор, обозначающий свойство для заноса в XML - добавляем в свойства
                self.__prop_properties.append(pr)
            elif ty == Parent:
                # если текущий атрибут - декоратор, обозначающий родителя для заноса в XML - добавляем в свойства
                self.__prop_parent = pr
            elif ty == Childs:
                # если текущий атрибут - декоратор, обозначающий детей для заноса в XML - добавляем в свойства
                self.__prop_childs = pr

    def generate_xml(self):
        assert self.__initialised_objtreetoxml  # Проверка была ли инициализация структур класса ObjTreeToXML

        self.__check_props()  # Заполняет список нужных параметров для заноса в XML
        pass
