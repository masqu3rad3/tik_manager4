# This Python file uses the following encoding: utf-8
#############################################################################
##
## Copyright (C) 2020 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of Qt for Python.
##
## $QT_BEGIN_LICENSE:LGPL$
## Commercial License Usage
## Licensees holding valid commercial Qt licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Qt Company. For licensing terms
## and conditions see https://www.qt.io/terms-conditions. For further
## information use the contact form at https://www.qt.io/contact-us.
##
## GNU Lesser General Public License Usage
## Alternatively, this file may be used under the terms of the GNU Lesser
## General Public License version 3 as published by the Free Software
## Foundation and appearing in the file LICENSE.LGPL3 included in the
## packaging of this file. Please review the following information to
## ensure the GNU Lesser General Public License version 3 requirements
## will be met: https://www.gnu.org/licenses/lgpl-3.0.html.
##
## GNU General Public License Usage
## Alternatively, this file may be used under the terms of the GNU
## General Public License version 2.0 or (at your option) the GNU General
## Public license version 3 or any later version approved by the KDE Free
## Qt Foundation. The licenses are as published by the Free Software
## Foundation and appearing in the file LICENSE.GPL2 and LICENSE.GPL3
## included in the packaging of this file. Please review the following
## information to ensure the GNU General Public License requirements will
## be met: https://www.gnu.org/licenses/gpl-2.0.html and
## https://www.gnu.org/licenses/gpl-3.0.html.
##
## $QT_END_LICENSE$
##
#############################################################################

"""
This file contains the exact signatures for all functions in module
PySide2.QtWebEngineCore, except for defaults which are replaced by "...".
"""

# Module PySide2.QtWebEngineCore
import PySide2
try:
    import typing
except ImportError:
    from PySide2.support.signature import typing
from PySide2.support.signature.mapping import (
    Virtual, Missing, Invalid, Default, Instance)

class Object(object): pass

import shiboken2 as Shiboken
Shiboken.Object = Object

import PySide2.QtCore
import PySide2.QtWebEngineCore


class QWebEngineCookieStore(PySide2.QtCore.QObject):
    def deleteAllCookies(self): ...
    def deleteSessionCookies(self): ...
    def loadAllCookies(self): ...


class QWebEngineHttpRequest(Shiboken.Object):
    Get                      : QWebEngineHttpRequest = ... # 0x0
    Post                     : QWebEngineHttpRequest = ... # 0x1

    class Method(object):
        Get                      : QWebEngineHttpRequest.Method = ... # 0x0
        Post                     : QWebEngineHttpRequest.Method = ... # 0x1

    @typing.overload
    def __init__(self, other:PySide2.QtWebEngineCore.QWebEngineHttpRequest): ...
    @typing.overload
    def __init__(self, url:PySide2.QtCore.QUrl=..., method:PySide2.QtWebEngineCore.QWebEngineHttpRequest.Method=...): ...

    def hasHeader(self, headerName:PySide2.QtCore.QByteArray) -> bool: ...
    def header(self, headerName:PySide2.QtCore.QByteArray) -> PySide2.QtCore.QByteArray: ...
    def headers(self) -> typing.List: ...
    def method(self) -> PySide2.QtWebEngineCore.QWebEngineHttpRequest.Method: ...
    def postData(self) -> PySide2.QtCore.QByteArray: ...
    @staticmethod
    def postRequest(url:PySide2.QtCore.QUrl, postData:typing.Dict) -> PySide2.QtWebEngineCore.QWebEngineHttpRequest: ...
    def setHeader(self, headerName:PySide2.QtCore.QByteArray, value:PySide2.QtCore.QByteArray): ...
    def setMethod(self, method:PySide2.QtWebEngineCore.QWebEngineHttpRequest.Method): ...
    def setPostData(self, postData:PySide2.QtCore.QByteArray): ...
    def setUrl(self, url:PySide2.QtCore.QUrl): ...
    def swap(self, other:PySide2.QtWebEngineCore.QWebEngineHttpRequest): ...
    def unsetHeader(self, headerName:PySide2.QtCore.QByteArray): ...
    def url(self) -> PySide2.QtCore.QUrl: ...


class QWebEngineUrlRequestInfo(Shiboken.Object):
    NavigationTypeLink       : QWebEngineUrlRequestInfo = ... # 0x0
    ResourceTypeMainFrame    : QWebEngineUrlRequestInfo = ... # 0x0
    NavigationTypeTyped      : QWebEngineUrlRequestInfo = ... # 0x1
    ResourceTypeSubFrame     : QWebEngineUrlRequestInfo = ... # 0x1
    NavigationTypeFormSubmitted: QWebEngineUrlRequestInfo = ... # 0x2
    ResourceTypeStylesheet   : QWebEngineUrlRequestInfo = ... # 0x2
    NavigationTypeBackForward: QWebEngineUrlRequestInfo = ... # 0x3
    ResourceTypeScript       : QWebEngineUrlRequestInfo = ... # 0x3
    NavigationTypeReload     : QWebEngineUrlRequestInfo = ... # 0x4
    ResourceTypeImage        : QWebEngineUrlRequestInfo = ... # 0x4
    NavigationTypeOther      : QWebEngineUrlRequestInfo = ... # 0x5
    ResourceTypeFontResource : QWebEngineUrlRequestInfo = ... # 0x5
    NavigationTypeRedirect   : QWebEngineUrlRequestInfo = ... # 0x6
    ResourceTypeSubResource  : QWebEngineUrlRequestInfo = ... # 0x6
    ResourceTypeObject       : QWebEngineUrlRequestInfo = ... # 0x7
    ResourceTypeMedia        : QWebEngineUrlRequestInfo = ... # 0x8
    ResourceTypeWorker       : QWebEngineUrlRequestInfo = ... # 0x9
    ResourceTypeSharedWorker : QWebEngineUrlRequestInfo = ... # 0xa
    ResourceTypePrefetch     : QWebEngineUrlRequestInfo = ... # 0xb
    ResourceTypeFavicon      : QWebEngineUrlRequestInfo = ... # 0xc
    ResourceTypeXhr          : QWebEngineUrlRequestInfo = ... # 0xd
    ResourceTypePing         : QWebEngineUrlRequestInfo = ... # 0xe
    ResourceTypeServiceWorker: QWebEngineUrlRequestInfo = ... # 0xf
    ResourceTypeCspReport    : QWebEngineUrlRequestInfo = ... # 0x10
    ResourceTypePluginResource: QWebEngineUrlRequestInfo = ... # 0x11
    ResourceTypeNavigationPreloadMainFrame: QWebEngineUrlRequestInfo = ... # 0x13
    ResourceTypeLast         : QWebEngineUrlRequestInfo = ... # 0x14
    ResourceTypeNavigationPreloadSubFrame: QWebEngineUrlRequestInfo = ... # 0x14
    ResourceTypeUnknown      : QWebEngineUrlRequestInfo = ... # 0xff

    class NavigationType(object):
        NavigationTypeLink       : QWebEngineUrlRequestInfo.NavigationType = ... # 0x0
        NavigationTypeTyped      : QWebEngineUrlRequestInfo.NavigationType = ... # 0x1
        NavigationTypeFormSubmitted: QWebEngineUrlRequestInfo.NavigationType = ... # 0x2
        NavigationTypeBackForward: QWebEngineUrlRequestInfo.NavigationType = ... # 0x3
        NavigationTypeReload     : QWebEngineUrlRequestInfo.NavigationType = ... # 0x4
        NavigationTypeOther      : QWebEngineUrlRequestInfo.NavigationType = ... # 0x5
        NavigationTypeRedirect   : QWebEngineUrlRequestInfo.NavigationType = ... # 0x6

    class ResourceType(object):
        ResourceTypeMainFrame    : QWebEngineUrlRequestInfo.ResourceType = ... # 0x0
        ResourceTypeSubFrame     : QWebEngineUrlRequestInfo.ResourceType = ... # 0x1
        ResourceTypeStylesheet   : QWebEngineUrlRequestInfo.ResourceType = ... # 0x2
        ResourceTypeScript       : QWebEngineUrlRequestInfo.ResourceType = ... # 0x3
        ResourceTypeImage        : QWebEngineUrlRequestInfo.ResourceType = ... # 0x4
        ResourceTypeFontResource : QWebEngineUrlRequestInfo.ResourceType = ... # 0x5
        ResourceTypeSubResource  : QWebEngineUrlRequestInfo.ResourceType = ... # 0x6
        ResourceTypeObject       : QWebEngineUrlRequestInfo.ResourceType = ... # 0x7
        ResourceTypeMedia        : QWebEngineUrlRequestInfo.ResourceType = ... # 0x8
        ResourceTypeWorker       : QWebEngineUrlRequestInfo.ResourceType = ... # 0x9
        ResourceTypeSharedWorker : QWebEngineUrlRequestInfo.ResourceType = ... # 0xa
        ResourceTypePrefetch     : QWebEngineUrlRequestInfo.ResourceType = ... # 0xb
        ResourceTypeFavicon      : QWebEngineUrlRequestInfo.ResourceType = ... # 0xc
        ResourceTypeXhr          : QWebEngineUrlRequestInfo.ResourceType = ... # 0xd
        ResourceTypePing         : QWebEngineUrlRequestInfo.ResourceType = ... # 0xe
        ResourceTypeServiceWorker: QWebEngineUrlRequestInfo.ResourceType = ... # 0xf
        ResourceTypeCspReport    : QWebEngineUrlRequestInfo.ResourceType = ... # 0x10
        ResourceTypePluginResource: QWebEngineUrlRequestInfo.ResourceType = ... # 0x11
        ResourceTypeNavigationPreloadMainFrame: QWebEngineUrlRequestInfo.ResourceType = ... # 0x13
        ResourceTypeLast         : QWebEngineUrlRequestInfo.ResourceType = ... # 0x14
        ResourceTypeNavigationPreloadSubFrame: QWebEngineUrlRequestInfo.ResourceType = ... # 0x14
        ResourceTypeUnknown      : QWebEngineUrlRequestInfo.ResourceType = ... # 0xff
    def block(self, shouldBlock:bool): ...
    def changed(self) -> bool: ...
    def firstPartyUrl(self) -> PySide2.QtCore.QUrl: ...
    def initiator(self) -> PySide2.QtCore.QUrl: ...
    def navigationType(self) -> PySide2.QtWebEngineCore.QWebEngineUrlRequestInfo.NavigationType: ...
    def redirect(self, url:PySide2.QtCore.QUrl): ...
    def requestMethod(self) -> PySide2.QtCore.QByteArray: ...
    def requestUrl(self) -> PySide2.QtCore.QUrl: ...
    def resourceType(self) -> PySide2.QtWebEngineCore.QWebEngineUrlRequestInfo.ResourceType: ...
    def setHttpHeader(self, name:PySide2.QtCore.QByteArray, value:PySide2.QtCore.QByteArray): ...


class QWebEngineUrlRequestInterceptor(PySide2.QtCore.QObject):

    def __init__(self, p:typing.Optional[PySide2.QtCore.QObject]=...): ...

    def interceptRequest(self, info:PySide2.QtWebEngineCore.QWebEngineUrlRequestInfo): ...


class QWebEngineUrlRequestJob(PySide2.QtCore.QObject):
    NoError                  : QWebEngineUrlRequestJob = ... # 0x0
    UrlNotFound              : QWebEngineUrlRequestJob = ... # 0x1
    UrlInvalid               : QWebEngineUrlRequestJob = ... # 0x2
    RequestAborted           : QWebEngineUrlRequestJob = ... # 0x3
    RequestDenied            : QWebEngineUrlRequestJob = ... # 0x4
    RequestFailed            : QWebEngineUrlRequestJob = ... # 0x5

    class Error(object):
        NoError                  : QWebEngineUrlRequestJob.Error = ... # 0x0
        UrlNotFound              : QWebEngineUrlRequestJob.Error = ... # 0x1
        UrlInvalid               : QWebEngineUrlRequestJob.Error = ... # 0x2
        RequestAborted           : QWebEngineUrlRequestJob.Error = ... # 0x3
        RequestDenied            : QWebEngineUrlRequestJob.Error = ... # 0x4
        RequestFailed            : QWebEngineUrlRequestJob.Error = ... # 0x5
    def fail(self, error:PySide2.QtWebEngineCore.QWebEngineUrlRequestJob.Error): ...
    def initiator(self) -> PySide2.QtCore.QUrl: ...
    def redirect(self, url:PySide2.QtCore.QUrl): ...
    def reply(self, contentType:PySide2.QtCore.QByteArray, device:PySide2.QtCore.QIODevice): ...
    def requestHeaders(self) -> typing.Dict: ...
    def requestMethod(self) -> PySide2.QtCore.QByteArray: ...
    def requestUrl(self) -> PySide2.QtCore.QUrl: ...


class QWebEngineUrlScheme(Shiboken.Object):
    PortUnspecified          : QWebEngineUrlScheme = ... # -0x1
    SecureScheme             : QWebEngineUrlScheme = ... # 0x1
    LocalScheme              : QWebEngineUrlScheme = ... # 0x2
    LocalAccessAllowed       : QWebEngineUrlScheme = ... # 0x4
    NoAccessAllowed          : QWebEngineUrlScheme = ... # 0x8
    ServiceWorkersAllowed    : QWebEngineUrlScheme = ... # 0x10
    ViewSourceAllowed        : QWebEngineUrlScheme = ... # 0x20
    ContentSecurityPolicyIgnored: QWebEngineUrlScheme = ... # 0x40
    CorsEnabled              : QWebEngineUrlScheme = ... # 0x80

    class Flag(object):
        SecureScheme             : QWebEngineUrlScheme.Flag = ... # 0x1
        LocalScheme              : QWebEngineUrlScheme.Flag = ... # 0x2
        LocalAccessAllowed       : QWebEngineUrlScheme.Flag = ... # 0x4
        NoAccessAllowed          : QWebEngineUrlScheme.Flag = ... # 0x8
        ServiceWorkersAllowed    : QWebEngineUrlScheme.Flag = ... # 0x10
        ViewSourceAllowed        : QWebEngineUrlScheme.Flag = ... # 0x20
        ContentSecurityPolicyIgnored: QWebEngineUrlScheme.Flag = ... # 0x40
        CorsEnabled              : QWebEngineUrlScheme.Flag = ... # 0x80

    class Flags(object): ...

    class SpecialPort(object):
        PortUnspecified          : QWebEngineUrlScheme.SpecialPort = ... # -0x1

    class Syntax(object):
        HostPortAndUserInformation: QWebEngineUrlScheme.Syntax = ... # 0x0
        HostAndPort              : QWebEngineUrlScheme.Syntax = ... # 0x1
        Host                     : QWebEngineUrlScheme.Syntax = ... # 0x2
        Path                     : QWebEngineUrlScheme.Syntax = ... # 0x3

    @typing.overload
    def __init__(self): ...
    @typing.overload
    def __init__(self, name:PySide2.QtCore.QByteArray): ...
    @typing.overload
    def __init__(self, that:PySide2.QtWebEngineCore.QWebEngineUrlScheme): ...

    def __copy__(self): ...
    def defaultPort(self) -> int: ...
    def flags(self) -> PySide2.QtWebEngineCore.QWebEngineUrlScheme.Flags: ...
    def name(self) -> PySide2.QtCore.QByteArray: ...
    @staticmethod
    def registerScheme(scheme:PySide2.QtWebEngineCore.QWebEngineUrlScheme): ...
    @staticmethod
    def schemeByName(name:PySide2.QtCore.QByteArray) -> PySide2.QtWebEngineCore.QWebEngineUrlScheme: ...
    def setDefaultPort(self, newValue:int): ...
    def setFlags(self, newValue:PySide2.QtWebEngineCore.QWebEngineUrlScheme.Flags): ...
    def setName(self, newValue:PySide2.QtCore.QByteArray): ...
    def setSyntax(self, newValue:PySide2.QtWebEngineCore.QWebEngineUrlScheme.Syntax): ...
    def syntax(self) -> PySide2.QtWebEngineCore.QWebEngineUrlScheme.Syntax: ...


class QWebEngineUrlSchemeHandler(PySide2.QtCore.QObject):

    def __init__(self, parent:typing.Optional[PySide2.QtCore.QObject]=...): ...

    def requestStarted(self, arg__1:PySide2.QtWebEngineCore.QWebEngineUrlRequestJob): ...

# eof
