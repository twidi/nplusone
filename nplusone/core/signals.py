# -*- coding: utf-8 -*-

import functools
import contextlib

import blinker


load = blinker.Signal()
lazy_load = blinker.Signal()
eager_load = blinker.Signal()
touch = blinker.Signal()


get_worker = lambda *a, **kw: blinker.ANY


def signalify(signal, func, parser=None, **context):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        signal.send(
            get_worker(),
            args=args,
            kwargs=kwargs,
            context=context,
            parser=parser,
        )
        return func(*args, **kwargs)
    return wrapped


def designalify(signal, func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        with ignore(signal):
            return func(*args, **kwargs)
    return wrapped


@contextlib.contextmanager
def ignore(signal, sender=None):
    sender = sender or get_worker()
    receivers = list(signal.receivers_for(sender))
    for receiver in receivers:
        signal.disconnect(receiver, sender=sender)
    try:
        yield
    finally:
        for receiver in receivers:
            signal.connect(receiver, sender=sender)
