class Type(object):
    def asDict(self):
        d = dict(type=self.__class__.__name__.lower())
        for n, v in self.__dict__.items():
            if v is not None:
                d[n] = v
        return d


class Any(Type):
    def reduce(self, value):
        return value


class Int(Type):
    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max

    def reduce(self, value):
        value = int(value)
        if self.min is not None and value < self.min:
            raise TypeError('Value is less than minimal (%i < %i)' % (value, self.min))
        if self.max is not None and value > self.max:
            raise TypeError('Value is more than maximum (%i > %i)' % (value, self.max))
        return value


class List(Type):
    def __init__(self, *list):
        self.list = list

    def reduce(self, value):
        if value not in self.list:
            raise TypeError('Value %s not in list %s' % (value, self.list))
        return value


class Decimal(Type):
    def __init__(self, precision=None, min=None, max=None):
        self.precision = precision
        self.min = min
        self.max = max

    def reduce(self, value):
        value = float(value)
        if self.min is not None and value < self.min:
            raise TypeError('Value is less than minimal (%i < %i)' % (value, self.min))
        if self.max is not None and value > self.max:
            raise TypeError('Value is more than maximum (%i > %i)' % (value, self.max))
        return value


class Bool(Type):
    def reduce(self, value):
        return bool(value)


class Str(Type):
    def reduce(self, value):
        return str(value)

            
class reduceArgTypes(object):
    def __init__(self, *argTypes):
        self.argTypes = argTypes

    def __call__(self, func):
        def wrapped(*args):
            argTypes = wrapped.argTypes
            if len(argTypes) != len(args):
                raise TypeError('%s takes exactly %i arguments (%i given)' % (func.__name__, len(argTypes), len(args))) 
            typedArgs = []
            for arg, argType in zip(args, argTypes):
                typedArgs.append(argType.reduce(arg))
            return func(*typedArgs)
        wrapped.argTypes = self.argTypes
        return wrapped
