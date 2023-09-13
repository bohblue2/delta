import zmq


cdef class ZeromqClient:
    cdef str _name
    cdef object _context
    cdef object _subscriber
    cdef object _internal_publisher
    cdef object _external_publisher

    def __init__(
            self,
            subscriber_url: str,
            internal_publisher_url: str,
            external_publisher_url: str,
            high_water_mark: int = 10**5,
            name: str = 'default',
            context: object = zmq.Context(),
    ):
        self._name = name
        self._context = context
        self._subscriber = self._context.socket(zmq.SUB)
        self._subscriber.set(zmq.SUBSCRIBE, b"")
        self._subscriber.set(zmq.RCVHWM, high_water_mark)
        self._subscriber.set(zmq.SNDHWM, high_water_mark)
        self._subscriber.bind(subscriber_url)

        self._internal_publisher = self._context.socket(zmq.PUB)
        self._internal_publisher.bind(internal_publisher_url)
        self._internal_publisher.set(zmq.RCVHWM, high_water_mark)
        self._internal_publisher.set(zmq.SNDHWM, high_water_mark)
        self._external_publisher = self._context.socket(zmq.PUB)
        self._external_publisher.bind(external_publisher_url)

    @property
    def subscriber(self):
        return self._subscriber

    cpdef bytes subscribe(self, int flags=0):
        return self._subscriber.recv(flags=flags, copy=False).bytes \
            if flags else self._subscriber.recv(copy=False).bytes

    cpdef void publish(self, bytes msg):
        self._internal_publisher.send(msg, copy=False)
        self._external_publisher.send(msg, copy=False)

    cpdef void close(self):
        self._internal_publisher.close()
        self._external_publisher.close()
        self._subscriber.close()
        self._context.term()

cdef class ZmqBroker:
    cdef list _clients
    cdef int _timeout
    cdef object _write

    cdef dict _handlers
    cdef object _poller

    def __init__(
            self,
            clients: list[ZeromqClient],
            timeout: int
    ):
        self._clients = clients
        self._timeout = timeout

        self._handlers = {}
        self._poller = zmq.Poller()
        for client in clients:
            self._poller.register(
                client.subscriber,
                zmq.POLLIN
            )

    cpdef bytes proxy(self):
        cdef bytes raw_msg
        cdef str sock_name
        cdef object handler

        socks = dict(self._poller.poll(timeout=self._timeout))
        for client in self._clients:
            if socks.get(client.subscriber, None) == zmq.POLLIN:
                raw_msg = client.subscribe()
                client.publish(raw_msg)
                if client in self._handlers:
                    handler = self._handlers[client]
                    handler(raw_msg)
                return raw_msg

    cpdef void add_handler(self, client: ZeromqClient, handler: callable):
        self._handlers[client] = handler
