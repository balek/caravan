from .base import VanSession, VanModule, deviceCommand, Str, Any



class Props(VanModule):
    def __init__(self, session):
        super(Props, self).__init__(session, 'props')
        self.props = {}

    @deviceCommand(Str())
    def getProp(self, name):
        d = self.props
        for n in name.split('.'):
            d = d[n]
        return d

    @deviceCommand(Str(), Any())
    def setProp(self, name, value):
        d = self.props
        for n in name.split('.')[:-1]:
            d = d.setdefault(n, {})
        d[name.rsplit('.', 1)[-1]] = value
        

class AppSession(VanSession):
    def start(self):
        Props(self)



if __name__ == '__main__':
    from autobahn.twisted.wamp import ApplicationRunner
    runner = ApplicationRunner("ws://127.0.0.1/ws", "realm1")
    runner.run(AppSession)
