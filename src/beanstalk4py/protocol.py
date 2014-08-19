#!/usr/bin/env python

import sys

from twisted.protocols.basic import LineReceiver
from twisted.internet import defer


class BeanstalkClient(LineReceiver):
    def __init__(self, app):
        self._app = app
        self._buffer = None
        self._expectDataSize = 0
        self._waitResponseState = False
        self._cmd = None
        self._d = None
        #
        self._clearBuffer()

    def connectionMade(self):
        self._app._haveConnection(self)
        #self.transport.loseConnection()

    def lineReceived(self, line):
        #
        print("S: %r" % line)
        #
        if self._cmd is not None:
            # Step 1. Prepare name
            cmds = self._cmd.split("-")
            parts = []
            for cmd in cmds:
                cmd = cmd.title()
                parts.append(cmd)
            # Step 2. Invoke name
            cbName = "_handle" + "".join(parts)
            cb = getattr(self, cbName)
            if callable(cb):
                cb(line)

    def put(self, priority=1, delay=30, ttr=60, data=None):
        """ Insert job into the currently used tube. Options may be
        :param priority: priority to use to queue the job. Jobs with smaller priority values will be scheduled before jobs with larger priorities. The most urgent priority is 0
        :param delay: An integer number of seconds to wait before putting the job in the ready queue. The job will be in the "delayed" state during this time
        :param ttr: "time to run" - An integer number of seconds to allow a worker to run this job. This time is counted from the moment a worker reserves this job. If the worker does not delete, release, or bury the job within ttr seconds, the job will time out and the server will release the job. The minimum ttr is 1. If the client sends 0, the server will silently increase the ttr to 1.
        :param data: The job body.
        """
        assert not self._waitResponseState
        self._waitResponseState = True
        #
        self._cmd = "put"
        #
        self._d = defer.Deferred()
        #
        bytes = len(data)
        self.sendLine("put {priority} {delay} {ttr} {bytes}".format(priority=priority, delay=delay, ttr=ttr, bytes=bytes))
        self.sendLine(data)
        #
        return self._d

    def delete(self, job_id):
        assert not self._waitResponseState
        self._waitResponseState = True
        #
        self._cmd = "delete"
        #
        self.sendLine("delete {job_id}".format(job_id=job_id))

    def reserve(self, timeout=None):
        assert not self._waitResponseState
        self._waitResponseState = True
        #
        self._cmd = "reserve"
        #
        self._d = defer.Deferred()
        #
        if timeout is None:
            self.sendLine("reserve".format())
        else:
            self.sendLine("reserve-with-timeout {timeout}".format(timeout=timeout))
        #
        return self._d

    def _handlePut(self, response):
        responses = response.split(" ")
        if responses[0] == "INSERTED":
            self._waitResponseState = False
            self._d.callback(responses[1])

    def _handleReserve(self, response):
        responses = response.split(" ")
        if responses[0] == "RESERVED":
            job_id = responses[1]
            self._expectDataSize = int(responses[2])
            self.setRawMode()
        elif responses[0] == "DEADLINE_SOON":
            self._waitResponseState = False
            self._d.errback(LookupError("Deadline soon"))

    def _clearBuffer(self):
        self._buffer = ""

    def rawDataReceived(self, data):
        self._buffer += data
        length = len(self._buffer)
        if length >= self._expectDataSize:
            #self.__log.debug("done collect job body (date = %r)", self._buffer)
            #print("Done: %r" % self._buffer)
            #
            self._d.callback(self._buffer)
            #
            self._clearBuffer()
            self.setLineMode()
            #
            self._waitResponseState = False

    def release(self, job_id):
        assert not self._waitResponseState
        self._waitResponseState = True
        #
        self._cmd = "release"
        #

    def touch(self, job_id):
        assert not self._waitResponseState
        self._waitResponseState = True
        #
        self._cmd = "touch"
        #
        self.sendLine("touch {job_id}".format(job_id=job_id))

    def stats(self):
        assert not self._waitResponseState
        self._waitResponseState = True
        #
        self._cmd = "stats"
        #
        self.sendLine("stats")

    def stats_job(self, job_id):
        assert not self._waitResponseState
        self._waitResponseState = True
        #
        self._cmd = "stats-job"
        #
        self.sendLine("stats-job {job_id}".format(job_id=job_id))

