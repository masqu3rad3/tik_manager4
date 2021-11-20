#!/usr/bin/env python
# -*- coding: utf-8 -*-

def encode(data):
    try: return unicode(data).encode("utf-8")
    except NameError: return data


def decode(data):
    try: return unicode(data).decode("utf-8")
    except NameError:
        if type(data) == bytes:
            return data.decode("utf-8")
        else:
            return data






