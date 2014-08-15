#@PydevCodeAnalysisIgnore
from __future__ import absolute_imports

from types import MethodType

from twisted.internet.defer import inlineCallbacks, gatherResults

from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp.types import PublishOptions

from .types import *



class deviceCommand(reduceArgTypes):
    def __init__(self, *argTypes):
	argTypes = (Any(),) + argTypes
        super(deviceCommand, self).__init__(*argTypes)

    def __call__(self, func):
        wrapped = super(deviceCommand, self).__call__(func)
        wrapped.command = lambda: map(lambda t: t.asDict(), self.argTypes[1:])
        return wrapped


class VanDevice(object):
    state = None

    def __init__(self, parent, name):
        parent.children[name] = self
        self.parent = parent
        self.name = name
        self.children = {}
        self.registrations = []
        self.commands = {}
        if hasattr(self, 'stateType') and hasattr(self, 'set'):
            setCommand = deviceCommand(self.stateType)(self.__class__.set)
            self.set = MethodType(setCommand, self)
        for command in dir(self):
            func = getattr(self, command)
            if hasattr(func, 'command'):
                self.commands[command] = func.command()
                self.registrations.append(self.registerCommand(func, command))

    def __del__(self):
        for r in self.registrations:
            r.addCallback(lambda r: r.unregister())

    def registerCommand(self, func, command):
        return self.parent.registerCommand(func, '%s.%s' % (self.name, command))

    def emitEvent(self, event, *args, **kwargs):
        return self.parent.emitEvent('%s.%s' % (self.name, event), *args, **kwargs)

    @deviceCommand()
    def get(self):
        return self.state

    @deviceCommand()
    def list(self):
        return map(lambda d: d.asDict(), self.children.values())

    def asDict(self):
        return { 'name': self.name, 'state': self.state, 'commands': self.commands }

    def changeState(self, value):
        if self.state != value:
            self.emitEvent('changed', value)
        self.state = value
        return value

    def __getitem__(self, name):
        return self.parent.__getitem__('%s.%s' % (self.name, name))

    def __setitem__(self, name, value):
        return self.parent.__setitem__('%s.%s' % (self.name, name), value)

    def props(self, name):
        return self.parent.props('%s.%s' % (self.name, name))


class VanEndpoint(object):
    def __init__(self, session, name):
        self.session = session
        self.name = name

    def __call__(self, *args, **kwargs):
        return self.session.call(self.name, *args, **kwargs)

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError
        return VanEndpoint(self.session, '%s.%s' % (self.name, name))

    def on(self, event, func):
        return self.session.subscribe(func, '%s.%s' % (self.name, event))

    def call(self, name, *args, **kwargs):
        return self.session.call('%s.%s' % (self.name, name), *args, **kwargs)


class VanRootEndpoint(object):
    def __getattr__(self, name):
        return VanEndpoint(self.session, name)

devices = VanRootEndpoint()



class VanModule(VanDevice):
    def announce(self):
        self.parent.emitEvent('announce', self.asDict())

    def __init__(self, session, name):
        super(VanModule, self).__init__(session, name)
        self.parent.subscribe(self.announce, 'discover')
        self.announce()


class VanSession(ApplicationSession):
    children = {}

    def registerCommand(self, func, command):
        self.register(func, command)

    def emitEvent(self, event, *args, **kwargs):
        return self.publish(event, *args, options=PublishOptions(excludeMe=False), **kwargs)

    def announce(self):
        self.session.publish('announce', self.name)

    def onJoin(self, details):
        devices.session = self
        return self.start()

    def __getitem__(self, name):
        return self.call('props.getProp', name)

    def __setitem__(self, name, value):
        return self.call('props.setProp', name, value)

    def props(self, name):
        return self.call('props.list', name)
