beanstalk4py
============

beanstalk4py is crossplatform implementation on Python beanstalkd protocol.

Let's look on put example:

```python
#!/usr/bin/python

import json

from twisted.internet import reactor

from beanstalk4py import BeanstalkClientFactory


class Application(object):

    def _doError(self, error):
        print(error)

    def _doDone(self, result):
        print("Inserted (job_id = %r)" % result)
        reactor.stop()

    def doInsertWorkUnit(self, client):
        print("doWorkUnit")
        job = {
            "url": "http://www.mail.ru",
        }
        client.put(data=json.dumps(job)) \
            .addCallback(self._doDone) \
            .addErrback(self._doError)

    def _haveConnection(self, client):
        print("_haveConnection")
        reactor.callLater(1.0, self.doInsertWorkUnit, client)

    def run(self):
        factory = BeanstalkClientFactory(app=self)
        connector = reactor.connectTCP('192.168.48.5', 11300, factory)
        reactor.run()


def main():
    app = Application()
    app.run()

if __name__ == '__main__':
    main()
```

Let's look on reserve example:

```python
#!/usr/bin/python

import json

from twisted.internet import reactor

from beanstalk4py import BeanstalkClientFactory


class Application(object):

    def _doReserveJob(self, job, client=None):
        print "_doReserveJob"
        print(job)
        jobParam = json.loads(job)
        print(jobParam)
        reactor.callLater(1.0, self.doWorkUnit, client=client)

    def _doSkipJob(self, error, client=None):
        print(error)
        reactor.callLater(1.0, self.doWorkUnit, client=client)

    def doWorkUnit(self, client):
        print("doWorkUnit")
        print(client)
        #client.put(data="Single!")
        #client.stats_job(job_id=1)
        client.reserve() \
            .addCallback(self._doReserveJob, client) \
            .addErrback(self._doSkipJob, client)
       

    def _haveConnection(self, client):
        print("_haveConnection")
        reactor.callLater(1.0, self.doWorkUnit, client)

    def run(self):
        factory = BeanstalkClientFactory(app=self)
        connector = reactor.connectTCP('192.168.48.5', 11300, factory)
        reactor.run()


def main():
    app = Application()
    app.run()

if __name__ == '__main__':
    main()
```

Others
------

Make your own client API. It's easy! The 1.3 protocol doc gives a complete description of the beanstalk protocol.

Note: as of version 1.0 the protocol will remain compatible until beanstalkd 2.0. Any client written to work with a 1.x beanstalkd will also work, unchanged, with any later beanstalkd before 2.0.

Origianl docs in http://github.com/kr/beanstalkd/tree/v1.3/doc/protocol.txt
Currently used spec in https://github.com/vit1251/beanstalk4py/wiki/Beanstalk-Protocol
