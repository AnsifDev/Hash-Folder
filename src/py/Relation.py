from typing import Callable

from pyparsing import Any


class Relation:
    # __unique_tuples_only = True
    CONSTRAINT_UNIQUE = 1
    CONSTRAINT_NOT_NULL = 2
    CONSTRAINT_PRIMARY = 3

    def __init__(self, *domains: str) -> None:
        self.__domains = domains
        self.__dicts = list[dict[str, Any]]()
        self.__contraints = dict[str, int]()
        self.__defualts = dict[str, Any]()
        self.__conditions = dict[str, Callable[[dict], bool]]()
        self.__assertions = dict[str, Callable[[], bool]]()

    #Definitions
    
    def set_defaults(self, **defaults): 
        for domain in defaults: self.__defualts[domain] = defaults[domain]
        return self
    
    def set_conditions(self, **conditions: Callable[[dict], bool]):
        for domain in conditions: self.__conditions[domain] = conditions[domain]
        return self
    
    def set_constraints(self, **constraints: int):
        for domain in constraints: self.__contraints[domain] = constraints[domain]
        return self

    def remove_default(self, domain: str): return self.__defualts.pop(domain)

    def remove_condition(self, domain: str): return self.__conditions.pop(domain)

    def remove_constraint(self, domain: str, contraint: int): self.__contraints[domain] &= ~contraint

    def add_assertion(self, name: str, condition_callback: Callable[[], bool]): self.__assertions[name] = condition_callback

    def remove_assertion(self, name: str): return self.__assertions.pop(name)

    # def add_trigger_on_insert(self, name)

    #manipulations
    def __parse(self, d: dict[str, Any], *values, **kvalues):
        for i, value in enumerate(values): d[self.__domains[i]] = value
        for key in kvalues: d[key] = kvalues[key]

        for domain in self.__defualts:
            if domain not in d: d[domain] = self.__defualts[domain]

        for domain in self.__contraints:
            contraint = self.__contraints[domain]
            if (contraint & self.CONSTRAINT_NOT_NULL) > 0 and (domain not in d or d[domain] == None): return False
            if (contraint & self.CONSTRAINT_UNIQUE) > 0:
                for t in self.__dicts:
                    if t[domain] == d[domain]: return False

        for domain in self.__conditions:
            if domain in d: 
                if not self.__conditions[domain](d): return False
        
        for row in self.__dicts:
            if row == d: return False
        
        return True

    def insert(self, *values, **kvalues):
        d = dict[str, Any]()
        if not self.__parse(d, *values, **kvalues): return False
        self.__dicts.append(d)
        for assertion in self.__assertions:
            if not self.__assertions[assertion]():
                self.__dicts.remove(d)
                return False
            
        return True

    def update(self, condition_callback: Callable[[dict], bool], *values, **kvalues):
        for row in self.get(condition_callback):
            if not self.__parse(row, *values, **kvalues): return False

    def get(self, condition_callback: Callable[[dict], bool] = None):
        rtList = self.__dicts.copy()
        i = 0
        while i < len(rtList):
            if condition_callback and not condition_callback(rtList[i]): rtList.pop(i)
            else: i += 1
        return rtList
   
    def delete(self, condition_callback: Callable[[dict], bool] = None):
        rtList = list()
        i = 0
        while i < len(self.__dicts):
            if not condition_callback or condition_callback(self.__dicts[i]): rtList.append(self.__dicts.pop(i))
            else: i += 1
        return rtList
