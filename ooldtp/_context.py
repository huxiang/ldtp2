import ldtp

class _Wrapper(object):
    def __new__(cls, *args, **kwargs):
        if not cls._generated:
            cls._generated = True
            d = ldtp.__dict__
            cls._wrapped_methods =[]
            for attr in d:
                if cls._isRemoteMethod(d[attr]) and cls._isRelevant(d[attr]):
                    setted = attr
                    if hasattr(cls, attr):
                        setted = "_remote_"+setted
                    cls._wrapped_methods.append(setted)
                    setattr(cls, setted, d[attr])
        return object.__new__(cls)

    def __getattribute__(self, name):
        obj = object.__getattribute__(self, name)
        if name in object.__getattribute__(self, '_wrapped_methods'):
            wrapper = object.__getattribute__(self, '_wrapMethod')
            return wrapper(obj)
        return obj

    def _isRemoteMethod(cls, obj):
        return hasattr(obj, '_Method__name')
    _isRemoteMethod = classmethod(_isRemoteMethod)

    def _listArgs(cls, func):
        l = [a.strip() for a in func.__doc__.split('\n')]
        l = filter(lambda x: x.startswith('@param '), l)
        l = [x[7:].split(':')[0] for x in l]
        return l
    _listArgs = classmethod(_listArgs)

class Context(_Wrapper):            
    _generated = False

    def __init__(self, window_name):
        self._window_name = window_name

    def _wrapMethod(self, obj):
        return _ContextFuncWrapper(self._window_name, obj)

    def _isRelevant(cls, obj):
        args = cls._listArgs(obj)
        return args and 'window_name' == args[0]
    _isRelevant = classmethod(_isRelevant)

    def getchild(self, child_name, role=''):
        matches = self._remote_getchild(child_name, role)
        if len(matches) == 1:
            return Component(self._window_name, matches[0])
        else:
            return [Component(self._window_name, x) for x in matches]
    
class _ContextFuncWrapper:
    def __init__(self, window_name, func):
        self._window_name = window_name
        self._func = func

    def __call__(self, *args, **kwargs):
        return self._func(self._window_name, *args, **kwargs)

class Component(_Wrapper):            
    _generated = False

    def __init__(self, window_name, object_name):
        self._window_name = window_name
        self._object_name = object_name

    def _wrapMethod(self, func):
        return _ComponentFuncWrapper(
            self._window_name, self._object_name, func)

    def _isRelevant(cls, obj):
        args = cls._listArgs(obj)
        return len(args) >= 2 and \
            'window_name' == args[0] and 'object_name' == args[1]
    _isRelevant = classmethod(_isRelevant)
    
class _ComponentFuncWrapper:
    def __init__(self, window_name, object_name, func):
        self._window_name = window_name
        self._object_name = object_name
        self._func = func

    def __call__(self, *args, **kwargs):
        return self._func(
            self._window_name, self._object_name, *args, **kwargs)

if __name__ == "__main__":
    c = Component('Calculator', 'btnNumeric1')
    print dir(c)
    c.click()
