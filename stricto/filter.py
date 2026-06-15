"""Module for kwargs parser"""

import re
from enum import Enum
from typing import Self, Any
from .generic import GenericType
from .list_and_tuple import ListAndTuple
from .selector import Selector
from .toolbox import check_value_type

class Operator(Enum):
    EQ = '$eq'
    NE = '$ne'
    GT = '$gt'
    GTE = '$gte'
    LT = '$lt'
    LTE = '$lte'
    REG = '$reg'
    ALL = '$all'
    CONTAINS = '$contains'
    SIZE = '$size'
    AND = '$and'
    OR = '$or'
    NOT = '$not'

class Filterer:

    _operator:Operator = None
    _value:Any|Self|list[Self] = None

    def __init__(self, operator:Operator, value:Any|list[Self]|Self):

        if operator in [ Operator.EQ, Operator.NE, Operator.GT, Operator.GTE, Operator.LT, Operator.LTE, Operator.REG, Operator.SIZE ]:
            if isinstance( value, (list, Filterer) ):
               raise TypeError(f'Operator {operator} need a value')
        
        if operator == Operator.REG:
            if not isinstance(value, (str, re.Pattern )):
               raise TypeError(f'Operator {operator} need a str or a Pattern')

        if operator in [ Operator.AND, Operator.OR ]:
            if not isinstance( value, list ):
               raise TypeError(f'Operator {operator} need a list of Filter')
            for v in value:
                if not isinstance( v, Filterer ):
                    raise TypeError(f'Operator {operator} need a list of Filter')
                
        if not isinstance( value, Filterer ):
            if operator in [ Operator.NOT, Operator.CONTAINS, Operator.ALL ]:
                raise TypeError(f'Operator {operator} need a list of Filter')
        
        self._operator = operator
        self._value = value


    def check( self, value: Any )-> bool:
        """
        Check the value of filterer
        :param value: the value to chech
        :type value: Any
        :return: True if match
        :rtype: bool
        """

        if self._operator == Operator.AND:
            for v in self._value:
                result = v.check( value)
                if result is False:
                    return False
            return True
        elif self._operator == Operator.OR:
            for v in self._value:
                result = v.check( value)
                if result is True:
                    return True
            return False
        elif self._operator == Operator.NOT:
            return not self._value.check( value)
        elif self._operator == Operator.EQ:
            return value == self._value
        elif self._operator == Operator.NE:
            return value != self._value
        elif self._operator == Operator.GT:
            return value > self._value
        elif self._operator == Operator.GTE:
            return value >= self._value
        elif self._operator == Operator.LT:
            return value < self._value
        elif self._operator == Operator.LTE:
            return value <= self._value
        elif self._operator == Operator.REG:
            if isinstance( value, str ):
                return re.match(self._value, value)
        elif self._operator == Operator.CONTAINS:
            if isinstance( value, list ):
                for v in value:
                    if self._value.check( v ) is True:
                        return True
        elif self._operator == Operator.ALL:
            if isinstance( value, list ):
                for v in value:
                    if self._value.check( v ) is False:
                        return False
        elif self._operator == Operator.SIZE:
            if isinstance( value, list ):
                return self._value.check( len(value) )
                    
        return False


class SuperFilter:

    _operator:Operator = None
    _value:Any|Self|list[Self] = None
    _path:str = None

    def __init__(self, path: str, operator:Operator, value:Any|list[Self]|Self):

        if operator in [ Operator.EQ, Operator.NE, Operator.GT, Operator.GTE, Operator.LT, Operator.LTE, Operator.REG, Operator.SIZE ]:
            if isinstance( value, (list, SuperFilter) ):
               raise TypeError(f'Operator {operator} need a value')
        
        if operator == Operator.REG:
            if not isinstance(value, (str, re.Pattern )):
               raise TypeError(f'Operator {operator} need a str or a Pattern')

        if operator in [ Operator.AND, Operator.OR ]:
            if not isinstance( value, list ):
               raise TypeError(f'Operator {operator} need a list of Filter')
            for v in value:
                if not isinstance( v, SuperFilter ):
                    raise TypeError(f'Operator {operator} need a list of Filter')
                
        if not isinstance( value, SuperFilter ):
            if operator in [ Operator.NOT, Operator.CONTAINS, Operator.ALL ]:
                raise TypeError(f'Operator {operator} need a list of Filter')
        
        self._path = path
        self._operator = operator
        self._value = value




    def check_value( self, value: Any )-> bool:
        """
        Check the value of filterer
        :param value: the value to chech
        :type value: Any
        :return: True if match
        :rtype: bool
        """

        if self._operator == Operator.AND:
            for v in self._value:
                result = v.check( value)
                if result is False:
                    return False
            return True
        elif self._operator == Operator.OR:
            for v in self._value:
                result = v.check( value)
                if result is True:
                    return True
            return False
        elif self._operator == Operator.NOT:
            return not self._value.check( value)
        elif self._operator == Operator.EQ:
            return value == self._value
        elif self._operator == Operator.NE:
            return value != self._value
        elif self._operator == Operator.GT:
            return value > self._value
        elif self._operator == Operator.GTE:
            return value >= self._value
        elif self._operator == Operator.LT:
            return value < self._value
        elif self._operator == Operator.LTE:
            return value <= self._value
        elif self._operator == Operator.REG:
            if isinstance( value, str ):
                return re.match(self._value, value)
        elif self._operator == Operator.CONTAINS:
            if isinstance( value, list ):
                for v in value:
                    if self._value.check( v ) is True:
                        return True
        elif self._operator == Operator.ALL:
            if isinstance( value, list ):
                for v in value:
                    if self._value.check( v ) is False:
                        return False
        elif self._operator == Operator.SIZE:
            if isinstance( value, list ):
                return self._value.check( len(value) )
                    
        return False






    def check( self, obj: GenericType )-> bool:

        if self._operator == Operator.AND:
            for v in self._value:
                result = v.check( obj ) 
                if result is False:
                    return False
            return True
        elif self._operator == Operator.OR:
            for v in self._value:
                result = v.check( obj )
                if result is True:
                    return True
            return False
        elif self._operator == Operator.NOT:
            return not self._value.check( obj )
        
        elif self._operator == Operator.CONTAINS:
            selected_object = obj.select( self._path )
            if not isinstance( selected_object, ListAndTuple ):
                return False
            
            for sub in selected_object.get_childs():
                if self._value.check( sub ) is True:
                    return True
            return False
        elif self._operator == Operator.ALL:
            selected_object = obj.select( self._path )
            if not isinstance( selected_object, ListAndTuple ):
                return False
            
            for sub in selected_object.get_childs():
                if self._value.check( sub ) is False:
                    return False
            return True
        

        selected_object = obj.select( self._path )
        if selected_object is None:
            return False
        
        value = selected_object.get_value()

        if self._operator == Operator.EQ:
            return value == self._value
        elif self._operator == Operator.NE:
            return value != self._value
        elif self._operator == Operator.GT:
            return value > self._value
        elif self._operator == Operator.GTE:
            return value >= self._value
        elif self._operator == Operator.LT:
            return value < self._value
        elif self._operator == Operator.LTE:
            return value <= self._value
        elif self._operator == Operator.REG:
            if isinstance( value, str ):
                return re.match(self._value, value)
                
        return False



