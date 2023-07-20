class Relation:
    __unique_tuples_only = True

    def __init__(self, *args) -> None:
        self.__domains = args
        self.__dicts = list()

    def set_unique_tuples_only(self, b: bool):
        self.__unique_tuples_only = b
    
    def append(self, *args, **kwargs): self.insert(-1, *args, **kwargs)

    def insert(self, index, *values, **kvalues): 
        d = dict()
        for i, value in enumerate(values): d[self.__domains[i]] = value
        for key in kvalues: d[key] = kvalues[key]
        if self.__unique_tuples_only:
            for de in self.__dicts:
                if self.__match_args(de, *values, *kvalues): return False
        self.__dicts.insert(index, d)
        return True

    def __match_args(self, d, *values, **kvalues):
        for i, value in enumerate(values): 
            key = self.__domains[i]
            if key not in d: return False
            if d[key] != value: return False
        for key in kvalues:
            if key not in d: return False
            if d[key] != kvalues[key]: return False
        return True

    def get(self, *values, **kvalues):
        rtList = self.__dicts.copy()
        i = 0
        while i < len(rtList):
            if not self.__match_args(rtList[i], *values, **kvalues): rtList.pop(i)
            else: i += 1
        return rtList
    
    def remove(self, *values, **kvalues):
        rtList = list()
        i = 0
        while i < len(self.__dicts):
            if self.__match_args(self.__dicts[i], *values, **kvalues): rtList.append(self.__dicts.pop(i))
            else: i += 1
        return rtList