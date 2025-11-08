// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only


#ifndef SBK_QTNETWORK_PYTHON_H
#define SBK_QTNETWORK_PYTHON_H

#include <sbkpython.h>
#include <sbkmodule.h>
#include <sbkconverter.h>
// Module Includes
#include <pyside6_qtcore_python.h>

// Bound library includes
#include <QtNetwork/qabstractsocket.h>
#include <QtNetwork/qdnslookup.h>
#include <QtNetwork/qformdatabuilder.h>
#include <QtNetwork/qhostaddress.h>
#include <QtNetwork/qhostinfo.h>
#include <QtNetwork/qhstspolicy.h>
#include <QtNetwork/qhttpheaders.h>
#include <QtNetwork/qhttpmultipart.h>
#include <QtNetwork/qlocalserver.h>
#include <QtNetwork/qlocalsocket.h>
#include <QtNetwork/qnetworkaccessmanager.h>
#include <QtNetwork/qnetworkcookie.h>
#include <QtNetwork/qnetworkinformation.h>
#include <QtNetwork/qnetworkproxy.h>
#include <QtNetwork/qnetworkreply.h>
#include <QtNetwork/qnetworkrequest.h>
#include <QtNetwork/qpassworddigestor.h>
#include <QtNetwork/qssl.h>
#if QT_CONFIG(dtls)
#include <QtNetwork/qdtls.h>
#endif
#if QT_CONFIG(networkinterface)
#include <QtNetwork/qnetworkinterface.h>
#endif
#if QT_CONFIG(ssl)
#include <QtNetwork/qdtls.h>
#include <QtNetwork/qocspresponse.h>
#include <QtNetwork/qsslcertificate.h>
#include <QtNetwork/qsslconfiguration.h>
#include <QtNetwork/qssldiffiehellmanparameters.h>
#include <QtNetwork/qsslerror.h>
#include <QtNetwork/qsslsocket.h>
#endif

QT_BEGIN_NAMESPACE
class QAbstractNetworkCache;
class QAuthenticator;
class QDnsDomainNameRecord;
class QDnsHostAddressRecord;
class QDnsMailExchangeRecord;
class QDnsServiceRecord;
class QDnsTextRecord;
class QFormDataPartBuilder;
class QHttp1Configuration;
class QHttp2Configuration;
class QHttpPart;
class QIPv6Address;
class QNetworkCacheMetaData;
class QNetworkCookieJar;
class QNetworkDatagram;
class QNetworkDiskCache;
class QNetworkProxyFactory;
class QNetworkRequestFactory;
class QOcspResponse;
class QRestAccessManager;
class QRestReply;
class QSslCertificateExtension;
class QSslCipher;
class QSslEllipticCurve;
class QSslKey;
class QSslPreSharedKeyAuthenticator;
class QSslServer;
class QTcpServer;
class QTcpSocket;
class QUdpSocket;
QT_END_NAMESPACE

// Type indices
enum [[deprecated]] : int {
    SBK_QABSTRACTNETWORKCACHE_IDX                            = 0,
    SBK_QABSTRACTSOCKET_SOCKETTYPE_IDX                       = 16,
    SBK_QABSTRACTSOCKET_NETWORKLAYERPROTOCOL_IDX             = 6,
    SBK_QABSTRACTSOCKET_SOCKETERROR_IDX                      = 10,
    SBK_QABSTRACTSOCKET_SOCKETSTATE_IDX                      = 14,
    SBK_QABSTRACTSOCKET_SOCKETOPTION_IDX                     = 12,
    SBK_QABSTRACTSOCKET_BINDFLAG_IDX                         = 4,
    SBK_QFLAGS_QABSTRACTSOCKET_BINDFLAG_IDX                  = 56,
    SBK_QABSTRACTSOCKET_PAUSEMODE_IDX                        = 8,
    SBK_QFLAGS_QABSTRACTSOCKET_PAUSEMODE_IDX                 = 58,
    SBK_QABSTRACTSOCKET_IDX                                  = 2,
    SBK_QAUTHENTICATOR_IDX                                   = 18,
    SBK_QDNSDOMAINNAMERECORD_IDX                             = 20,
    SBK_QDNSHOSTADDRESSRECORD_IDX                            = 22,
    SBK_QDNSLOOKUP_ERROR_IDX                                 = 26,
    SBK_QDNSLOOKUP_TYPE_IDX                                  = 30,
    SBK_QDNSLOOKUP_PROTOCOL_IDX                              = 28,
    SBK_QDNSLOOKUP_IDX                                       = 24,
    SBK_QDNSMAILEXCHANGERECORD_IDX                           = 32,
    SBK_QDNSSERVICERECORD_IDX                                = 34,
    SBK_QDNSTEXTRECORD_IDX                                   = 36,
    SBK_QDNSTLSASSOCIATIONRECORD_CERTIFICATEUSAGE_IDX        = 40,
    SBK_QDNSTLSASSOCIATIONRECORD_SELECTOR_IDX                = 44,
    SBK_QDNSTLSASSOCIATIONRECORD_MATCHINGTYPE_IDX            = 42,
    SBK_QDNSTLSASSOCIATIONRECORD_IDX                         = 38,
    SBK_QDTLS_HANDSHAKESTATE_IDX                             = 48,
    SBK_QDTLS_IDX                                            = 46,
    SBK_QDTLSCLIENTVERIFIER_IDX                              = 50,
    SBK_QDTLSCLIENTVERIFIER_GENERATORPARAMETERS_IDX          = 52,
    SBK_QFORMDATABUILDER_OPTION_IDX                          = 80,
    SBK_QFLAGS_QFORMDATABUILDER_OPTION_IDX                   = 60,
    SBK_QFORMDATABUILDER_IDX                                 = 78,
    SBK_QFORMDATAPARTBUILDER_IDX                             = 82,
    SBK_QHOSTADDRESS_SPECIALADDRESS_IDX                      = 88,
    SBK_QHOSTADDRESS_CONVERSIONMODEFLAG_IDX                  = 86,
    SBK_QFLAGS_QHOSTADDRESS_CONVERSIONMODEFLAG_IDX           = 62,
    SBK_QHOSTADDRESS_IDX                                     = 84,
    SBK_QHOSTINFO_HOSTINFOERROR_IDX                          = 92,
    SBK_QHOSTINFO_IDX                                        = 90,
    SBK_QHSTSPOLICY_POLICYFLAG_IDX                           = 96,
    SBK_QFLAGS_QHSTSPOLICY_POLICYFLAG_IDX                    = 64,
    SBK_QHSTSPOLICY_IDX                                      = 94,
    SBK_QHTTP1CONFIGURATION_IDX                              = 98,
    SBK_QHTTP2CONFIGURATION_IDX                              = 100,
    SBK_QHTTPHEADERS_WELLKNOWNHEADER_IDX                     = 104,
    SBK_QHTTPHEADERS_IDX                                     = 102,
    SBK_QHTTPMULTIPART_CONTENTTYPE_IDX                       = 108,
    SBK_QHTTPMULTIPART_IDX                                   = 106,
    SBK_QHTTPPART_IDX                                        = 110,
    SBK_QIPV6ADDRESS_IDX                                     = 112,
    SBK_QLOCALSERVER_SOCKETOPTION_IDX                        = 116,
    SBK_QFLAGS_QLOCALSERVER_SOCKETOPTION_IDX                 = 66,
    SBK_QLOCALSERVER_IDX                                     = 114,
    SBK_QLOCALSOCKET_LOCALSOCKETERROR_IDX                    = 120,
    SBK_QLOCALSOCKET_LOCALSOCKETSTATE_IDX                    = 122,
    SBK_QLOCALSOCKET_SOCKETOPTION_IDX                        = 124,
    SBK_QFLAGS_QLOCALSOCKET_SOCKETOPTION_IDX                 = 68,
    SBK_QLOCALSOCKET_IDX                                     = 118,
    SBK_QNETWORKACCESSMANAGER_OPERATION_IDX                  = 128,
    SBK_QNETWORKACCESSMANAGER_IDX                            = 126,
    SBK_QNETWORKADDRESSENTRY_DNSELIGIBILITYSTATUS_IDX        = 132,
    SBK_QNETWORKADDRESSENTRY_IDX                             = 130,
    SBK_QNETWORKCACHEMETADATA_IDX                            = 134,
    SBK_QNETWORKCOOKIE_RAWFORM_IDX                           = 138,
    SBK_QNETWORKCOOKIE_SAMESITE_IDX                          = 140,
    SBK_QNETWORKCOOKIE_IDX                                   = 136,
    SBK_QNETWORKCOOKIEJAR_IDX                                = 142,
    SBK_QNETWORKDATAGRAM_IDX                                 = 144,
    SBK_QNETWORKDISKCACHE_IDX                                = 146,
    SBK_QNETWORKINFORMATION_REACHABILITY_IDX                 = 152,
    SBK_QNETWORKINFORMATION_TRANSPORTMEDIUM_IDX              = 154,
    SBK_QNETWORKINFORMATION_FEATURE_IDX                      = 150,
    SBK_QFLAGS_QNETWORKINFORMATION_FEATURE_IDX               = 70,
    SBK_QNETWORKINFORMATION_IDX                              = 148,
    SBK_QNETWORKINTERFACE_INTERFACEFLAG_IDX                  = 158,
    SBK_QFLAGS_QNETWORKINTERFACE_INTERFACEFLAG_IDX           = 72,
    SBK_QNETWORKINTERFACE_INTERFACETYPE_IDX                  = 160,
    SBK_QNETWORKINTERFACE_IDX                                = 156,
    SBK_QNETWORKPROXY_PROXYTYPE_IDX                          = 166,
    SBK_QNETWORKPROXY_CAPABILITY_IDX                         = 164,
    SBK_QFLAGS_QNETWORKPROXY_CAPABILITY_IDX                  = 74,
    SBK_QNETWORKPROXY_IDX                                    = 162,
    SBK_QNETWORKPROXYFACTORY_IDX                             = 168,
    SBK_QNETWORKPROXYQUERY_QUERYTYPE_IDX                     = 172,
    SBK_QNETWORKPROXYQUERY_IDX                               = 170,
    SBK_QNETWORKREPLY_NETWORKERROR_IDX                       = 176,
    SBK_QNETWORKREPLY_IDX                                    = 174,
    SBK_QNETWORKREQUEST_KNOWNHEADERS_IDX                     = 184,
    SBK_QNETWORKREQUEST_ATTRIBUTE_IDX                        = 180,
    SBK_QNETWORKREQUEST_CACHELOADCONTROL_IDX                 = 182,
    SBK_QNETWORKREQUEST_LOADCONTROL_IDX                      = 186,
    SBK_QNETWORKREQUEST_PRIORITY_IDX                         = 188,
    SBK_QNETWORKREQUEST_REDIRECTPOLICY_IDX                   = 190,
    SBK_QNETWORKREQUEST_TRANSFERTIMEOUTCONSTANT_IDX          = 192,
    SBK_QNETWORKREQUEST_IDX                                  = 178,
    SBK_QNETWORKREQUESTFACTORY_IDX                           = 194,
    SBK_QOCSPRESPONSE_IDX                                    = 198,
    SBK_QTNETWORKQPASSWORDDIGESTOR_IDX                       = 202,
    SBK_QRESTACCESSMANAGER_IDX                               = 204,
    SBK_QRESTREPLY_IDX                                       = 206,
    SBK_QSSL_KEYTYPE_IDX                                     = 222,
    SBK_QSSL_ENCODINGFORMAT_IDX                              = 216,
    SBK_QSSL_KEYALGORITHM_IDX                                = 220,
    SBK_QSSL_ALTERNATIVENAMEENTRYTYPE_IDX                    = 214,
    SBK_QSSL_SSLPROTOCOL_IDX                                 = 226,
    SBK_QSSL_SSLOPTION_IDX                                   = 224,
    SBK_QFLAGS_QSSL_SSLOPTION_IDX                            = 76,
    SBK_QSSL_ALERTLEVEL_IDX                                  = 210,
    SBK_QSSL_ALERTTYPE_IDX                                   = 212,
    SBK_QSSL_IMPLEMENTEDCLASS_IDX                            = 218,
    SBK_QSSL_SUPPORTEDFEATURE_IDX                            = 228,
    SBK_QTNETWORKQSSL_IDX                                    = 208,
    SBK_QSSLCERTIFICATE_SUBJECTINFO_IDX                      = 234,
    SBK_QSSLCERTIFICATE_PATTERNSYNTAX_IDX                    = 232,
    SBK_QSSLCERTIFICATE_IDX                                  = 230,
    SBK_QSSLCERTIFICATEEXTENSION_IDX                         = 236,
    SBK_QSSLCIPHER_IDX                                       = 238,
    SBK_QSSLCONFIGURATION_NEXTPROTOCOLNEGOTIATIONSTATUS_IDX  = 242,
    SBK_QSSLCONFIGURATION_IDX                                = 240,
    SBK_QSSLDIFFIEHELLMANPARAMETERS_ERROR_IDX                = 246,
    SBK_QSSLDIFFIEHELLMANPARAMETERS_IDX                      = 244,
    SBK_QSSLELLIPTICCURVE_IDX                                = 248,
    SBK_QSSLERROR_SSLERROR_IDX                               = 252,
    SBK_QSSLERROR_IDX                                        = 250,
    SBK_QSSLKEY_IDX                                          = 254,
    SBK_QSSLPRESHAREDKEYAUTHENTICATOR_IDX                    = 256,
    SBK_QSSLSERVER_IDX                                       = 258,
    SBK_QSSLSOCKET_SSLMODE_IDX                               = 264,
    SBK_QSSLSOCKET_PEERVERIFYMODE_IDX                        = 262,
    SBK_QSSLSOCKET_IDX                                       = 260,
    SBK_QTCPSERVER_IDX                                       = 266,
    SBK_QTCPSOCKET_IDX                                       = 268,
    SBK_QUDPSOCKET_IDX                                       = 270,
    SBK_QDTLSERROR_IDX                                       = 54,
    SBK_QOCSPCERTIFICATESTATUS_IDX                           = 196,
    SBK_QOCSPREVOCATIONREASON_IDX                            = 200,
    SBK_QTNETWORK_IDX_COUNT                                  = 272,
};

// Type indices
enum : int {
    SBK_QAbstractNetworkCache_IDX                            = 0,
    SBK_QAbstractSocket_SocketType_IDX                       = 8,
    SBK_QAbstractSocket_NetworkLayerProtocol_IDX             = 3,
    SBK_QAbstractSocket_SocketError_IDX                      = 5,
    SBK_QAbstractSocket_SocketState_IDX                      = 7,
    SBK_QAbstractSocket_SocketOption_IDX                     = 6,
    SBK_QAbstractSocket_BindFlag_IDX                         = 2,
    SBK_QFlags_QAbstractSocket_BindFlag_IDX                  = 28,
    SBK_QAbstractSocket_PauseMode_IDX                        = 4,
    SBK_QFlags_QAbstractSocket_PauseMode_IDX                 = 29,
    SBK_QAbstractSocket_IDX                                  = 1,
    SBK_QAuthenticator_IDX                                   = 9,
    SBK_QDnsDomainNameRecord_IDX                             = 10,
    SBK_QDnsHostAddressRecord_IDX                            = 11,
    SBK_QDnsLookup_Error_IDX                                 = 13,
    SBK_QDnsLookup_Type_IDX                                  = 15,
    SBK_QDnsLookup_Protocol_IDX                              = 14,
    SBK_QDnsLookup_IDX                                       = 12,
    SBK_QDnsMailExchangeRecord_IDX                           = 16,
    SBK_QDnsServiceRecord_IDX                                = 17,
    SBK_QDnsTextRecord_IDX                                   = 18,
    SBK_QDnsTlsAssociationRecord_CertificateUsage_IDX        = 20,
    SBK_QDnsTlsAssociationRecord_Selector_IDX                = 22,
    SBK_QDnsTlsAssociationRecord_MatchingType_IDX            = 21,
    SBK_QDnsTlsAssociationRecord_IDX                         = 19,
    SBK_QDtls_HandshakeState_IDX                             = 24,
    SBK_QDtls_IDX                                            = 23,
    SBK_QDtlsClientVerifier_IDX                              = 25,
    SBK_QDtlsClientVerifier_GeneratorParameters_IDX          = 26,
    SBK_QFormDataBuilder_Option_IDX                          = 40,
    SBK_QFlags_QFormDataBuilder_Option_IDX                   = 30,
    SBK_QFormDataBuilder_IDX                                 = 39,
    SBK_QFormDataPartBuilder_IDX                             = 41,
    SBK_QHostAddress_SpecialAddress_IDX                      = 44,
    SBK_QHostAddress_ConversionModeFlag_IDX                  = 43,
    SBK_QFlags_QHostAddress_ConversionModeFlag_IDX           = 31,
    SBK_QHostAddress_IDX                                     = 42,
    SBK_QHostInfo_HostInfoError_IDX                          = 46,
    SBK_QHostInfo_IDX                                        = 45,
    SBK_QHstsPolicy_PolicyFlag_IDX                           = 48,
    SBK_QFlags_QHstsPolicy_PolicyFlag_IDX                    = 32,
    SBK_QHstsPolicy_IDX                                      = 47,
    SBK_QHttp1Configuration_IDX                              = 49,
    SBK_QHttp2Configuration_IDX                              = 50,
    SBK_QHttpHeaders_WellKnownHeader_IDX                     = 52,
    SBK_QHttpHeaders_IDX                                     = 51,
    SBK_QHttpMultiPart_ContentType_IDX                       = 54,
    SBK_QHttpMultiPart_IDX                                   = 53,
    SBK_QHttpPart_IDX                                        = 55,
    SBK_QIPv6Address_IDX                                     = 56,
    SBK_QLocalServer_SocketOption_IDX                        = 58,
    SBK_QFlags_QLocalServer_SocketOption_IDX                 = 33,
    SBK_QLocalServer_IDX                                     = 57,
    SBK_QLocalSocket_LocalSocketError_IDX                    = 60,
    SBK_QLocalSocket_LocalSocketState_IDX                    = 61,
    SBK_QLocalSocket_SocketOption_IDX                        = 62,
    SBK_QFlags_QLocalSocket_SocketOption_IDX                 = 34,
    SBK_QLocalSocket_IDX                                     = 59,
    SBK_QNetworkAccessManager_Operation_IDX                  = 64,
    SBK_QNetworkAccessManager_IDX                            = 63,
    SBK_QNetworkAddressEntry_DnsEligibilityStatus_IDX        = 66,
    SBK_QNetworkAddressEntry_IDX                             = 65,
    SBK_QNetworkCacheMetaData_IDX                            = 67,
    SBK_QNetworkCookie_RawForm_IDX                           = 69,
    SBK_QNetworkCookie_SameSite_IDX                          = 70,
    SBK_QNetworkCookie_IDX                                   = 68,
    SBK_QNetworkCookieJar_IDX                                = 71,
    SBK_QNetworkDatagram_IDX                                 = 72,
    SBK_QNetworkDiskCache_IDX                                = 73,
    SBK_QNetworkInformation_Reachability_IDX                 = 76,
    SBK_QNetworkInformation_TransportMedium_IDX              = 77,
    SBK_QNetworkInformation_Feature_IDX                      = 75,
    SBK_QFlags_QNetworkInformation_Feature_IDX               = 35,
    SBK_QNetworkInformation_IDX                              = 74,
    SBK_QNetworkInterface_InterfaceFlag_IDX                  = 79,
    SBK_QFlags_QNetworkInterface_InterfaceFlag_IDX           = 36,
    SBK_QNetworkInterface_InterfaceType_IDX                  = 80,
    SBK_QNetworkInterface_IDX                                = 78,
    SBK_QNetworkProxy_ProxyType_IDX                          = 83,
    SBK_QNetworkProxy_Capability_IDX                         = 82,
    SBK_QFlags_QNetworkProxy_Capability_IDX                  = 37,
    SBK_QNetworkProxy_IDX                                    = 81,
    SBK_QNetworkProxyFactory_IDX                             = 84,
    SBK_QNetworkProxyQuery_QueryType_IDX                     = 86,
    SBK_QNetworkProxyQuery_IDX                               = 85,
    SBK_QNetworkReply_NetworkError_IDX                       = 88,
    SBK_QNetworkReply_IDX                                    = 87,
    SBK_QNetworkRequest_KnownHeaders_IDX                     = 92,
    SBK_QNetworkRequest_Attribute_IDX                        = 90,
    SBK_QNetworkRequest_CacheLoadControl_IDX                 = 91,
    SBK_QNetworkRequest_LoadControl_IDX                      = 93,
    SBK_QNetworkRequest_Priority_IDX                         = 94,
    SBK_QNetworkRequest_RedirectPolicy_IDX                   = 95,
    SBK_QNetworkRequest_TransferTimeoutConstant_IDX          = 96,
    SBK_QNetworkRequest_IDX                                  = 89,
    SBK_QNetworkRequestFactory_IDX                           = 97,
    SBK_QOcspResponse_IDX                                    = 99,
    SBK_QtNetworkQPasswordDigestor_IDX                       = 101,
    SBK_QRestAccessManager_IDX                               = 102,
    SBK_QRestReply_IDX                                       = 103,
    SBK_QSsl_KeyType_IDX                                     = 111,
    SBK_QSsl_EncodingFormat_IDX                              = 108,
    SBK_QSsl_KeyAlgorithm_IDX                                = 110,
    SBK_QSsl_AlternativeNameEntryType_IDX                    = 107,
    SBK_QSsl_SslProtocol_IDX                                 = 113,
    SBK_QSsl_SslOption_IDX                                   = 112,
    SBK_QFlags_QSsl_SslOption_IDX                            = 38,
    SBK_QSsl_AlertLevel_IDX                                  = 105,
    SBK_QSsl_AlertType_IDX                                   = 106,
    SBK_QSsl_ImplementedClass_IDX                            = 109,
    SBK_QSsl_SupportedFeature_IDX                            = 114,
    SBK_QtNetworkQSsl_IDX                                    = 104,
    SBK_QSslCertificate_SubjectInfo_IDX                      = 117,
    SBK_QSslCertificate_PatternSyntax_IDX                    = 116,
    SBK_QSslCertificate_IDX                                  = 115,
    SBK_QSslCertificateExtension_IDX                         = 118,
    SBK_QSslCipher_IDX                                       = 119,
    SBK_QSslConfiguration_NextProtocolNegotiationStatus_IDX  = 121,
    SBK_QSslConfiguration_IDX                                = 120,
    SBK_QSslDiffieHellmanParameters_Error_IDX                = 123,
    SBK_QSslDiffieHellmanParameters_IDX                      = 122,
    SBK_QSslEllipticCurve_IDX                                = 124,
    SBK_QSslError_SslError_IDX                               = 126,
    SBK_QSslError_IDX                                        = 125,
    SBK_QSslKey_IDX                                          = 127,
    SBK_QSslPreSharedKeyAuthenticator_IDX                    = 128,
    SBK_QSslServer_IDX                                       = 129,
    SBK_QSslSocket_SslMode_IDX                               = 132,
    SBK_QSslSocket_PeerVerifyMode_IDX                        = 131,
    SBK_QSslSocket_IDX                                       = 130,
    SBK_QTcpServer_IDX                                       = 133,
    SBK_QTcpSocket_IDX                                       = 134,
    SBK_QUdpSocket_IDX                                       = 135,
    SBK_QDtlsError_IDX                                       = 27,
    SBK_QOcspCertificateStatus_IDX                           = 98,
    SBK_QOcspRevocationReason_IDX                            = 100,
    SBK_QtNetwork_IDX_COUNT                                  = 136,
};

// This variable stores all Python types exported by this module.
extern Shiboken::Module::TypeInitStruct *SbkPySide6_QtNetworkTypeStructs;

// This variable stores all Python types exported by this module in a backwards compatible way with identical indexing.
[[deprecated]] extern PyTypeObject **SbkPySide6_QtNetworkTypes;

// This variable stores the Python module object exported by this module.
extern PyObject *SbkPySide6_QtNetworkModuleObject;

// This variable stores all type converters exported by this module.
extern SbkConverter **SbkPySide6_QtNetworkTypeConverters;

// Converter indices
enum [[deprecated]] : int {
    SBK_QTNETWORK_QLIST_INT_IDX                              = 0, // QList<int>
    SBK_QTNETWORK_QLIST_QSSLCERTIFICATE_IDX                  = 2, // QList<QSslCertificate>
    SBK_QTNETWORK_QLIST_QBYTEARRAY_IDX                       = 4, // QList<QByteArray>
    SBK_QTNETWORK_QMAP_QBYTEARRAY_QVARIANT_IDX               = 6, // QMap<QByteArray,QVariant>
    SBK_QTNETWORK_QLIST_QSSLCIPHER_IDX                       = 8, // QList<QSslCipher>
    SBK_QTNETWORK_QLIST_QSSLELLIPTICCURVE_IDX                = 10, // QList<QSslEllipticCurve>
    SBK_QTNETWORK_QLIST_QNETWORKPROXY_IDX                    = 12, // QList<QNetworkProxy>
    SBK_QTNETWORK_QLIST_QNETWORKADDRESSENTRY_IDX             = 14, // QList<QNetworkAddressEntry>
    SBK_QTNETWORK_QLIST_QHOSTADDRESS_IDX                     = 16, // QList<QHostAddress>
    SBK_QTNETWORK_QLIST_QNETWORKINTERFACE_IDX                = 18, // QList<QNetworkInterface>
    SBK_QTNETWORK_QHASH_QNETWORKREQUEST_ATTRIBUTE_QVARIANT_IDX = 20, // QHash<QNetworkRequest::Attribute,QVariant>
    SBK_QTNETWORK_STD_PAIR_QBYTEARRAY_QBYTEARRAY_IDX         = 22, // std::pair<QByteArray,QByteArray>
    SBK_QTNETWORK_QLIST_STD_PAIR_QBYTEARRAY_QBYTEARRAY_IDX   = 24, // QList<std::pair<QByteArray,QByteArray>>
    SBK_QTNETWORK_QMULTIHASH_QBYTEARRAY_QBYTEARRAY_IDX       = 26, // QMultiHash<QByteArray,QByteArray>
    SBK_QTNETWORK_QMULTIMAP_QBYTEARRAY_QBYTEARRAY_IDX        = 28, // QMultiMap<QByteArray,QByteArray>
    SBK_QTNETWORK_QHASH_QSTRING_QVARIANT_IDX                 = 30, // QHash<QString,QVariant>
    SBK_QTNETWORK_QMAP_QSTRING_QVARIANT_IDX                  = 32, // QMap<QString,QVariant>
    SBK_QTNETWORK_QLIST_QNETWORKCOOKIE_IDX                   = 34, // QList<QNetworkCookie>
    SBK_QTNETWORK_QLIST_QHSTSPOLICY_IDX                      = 36, // QList<QHstsPolicy>
    SBK_QTNETWORK_QLIST_QSSLERROR_IDX                        = 38, // QList<QSslError>
    SBK_QTNETWORK_QLIST_QDNSDOMAINNAMERECORD_IDX             = 40, // QList<QDnsDomainNameRecord>
    SBK_QTNETWORK_QLIST_QDNSHOSTADDRESSRECORD_IDX            = 42, // QList<QDnsHostAddressRecord>
    SBK_QTNETWORK_QLIST_QDNSMAILEXCHANGERECORD_IDX           = 44, // QList<QDnsMailExchangeRecord>
    SBK_QTNETWORK_QLIST_QDNSSERVICERECORD_IDX                = 46, // QList<QDnsServiceRecord>
    SBK_QTNETWORK_QLIST_QDNSTEXTRECORD_IDX                   = 48, // QList<QDnsTextRecord>
    SBK_QTNETWORK_QLIST_QDNSTLSASSOCIATIONRECORD_IDX         = 50, // QList<QDnsTlsAssociationRecord>
    SBK_QTNETWORK_STD_PAIR_QHOSTADDRESS_INT_IDX              = 52, // std::pair<QHostAddress,int>
    SBK_QTNETWORK_QLIST_QSTRING_IDX                          = 54, // QList<QString>
    SBK_QTNETWORK_QLIST_QSSL_IMPLEMENTEDCLASS_IDX            = 56, // QList<QSsl::ImplementedClass>
    SBK_QTNETWORK_QLIST_QOCSPRESPONSE_IDX                    = 58, // QList<QOcspResponse>
    SBK_QTNETWORK_QLIST_QSSL_SUPPORTEDFEATURE_IDX            = 60, // QList<QSsl::SupportedFeature>
    SBK_QTNETWORK_QLIST_QSSL_SSLPROTOCOL_IDX                 = 62, // QList<QSsl::SslProtocol>
    SBK_QTNETWORK_QLIST_QSSLCERTIFICATEEXTENSION_IDX         = 64, // QList<QSslCertificateExtension>
    SBK_QTNETWORK_QMULTIMAP_QSSL_ALTERNATIVENAMEENTRYTYPE_QSTRING_IDX = 66, // QMultiMap<QSsl::AlternativeNameEntryType,QString>
    SBK_QTNETWORK_QLIST_QVARIANT_IDX                         = 68, // QList<QVariant>
    SBK_QTNETWORK_CONVERTERS_IDX_COUNT                       = 70,
};

// Converter indices
enum : int {
    SBK_QtNetwork_QList_int_IDX                              = 0, // QList<int>
    SBK_QtNetwork_QList_QSslCertificate_IDX                  = 1, // QList<QSslCertificate>
    SBK_QtNetwork_QList_QByteArray_IDX                       = 2, // QList<QByteArray>
    SBK_QtNetwork_QMap_QByteArray_QVariant_IDX               = 3, // QMap<QByteArray,QVariant>
    SBK_QtNetwork_QList_QSslCipher_IDX                       = 4, // QList<QSslCipher>
    SBK_QtNetwork_QList_QSslEllipticCurve_IDX                = 5, // QList<QSslEllipticCurve>
    SBK_QtNetwork_QList_QNetworkProxy_IDX                    = 6, // QList<QNetworkProxy>
    SBK_QtNetwork_QList_QNetworkAddressEntry_IDX             = 7, // QList<QNetworkAddressEntry>
    SBK_QtNetwork_QList_QHostAddress_IDX                     = 8, // QList<QHostAddress>
    SBK_QtNetwork_QList_QNetworkInterface_IDX                = 9, // QList<QNetworkInterface>
    SBK_QtNetwork_QHash_QNetworkRequest_Attribute_QVariant_IDX = 10, // QHash<QNetworkRequest::Attribute,QVariant>
    SBK_QtNetwork_std_pair_QByteArray_QByteArray_IDX         = 11, // std::pair<QByteArray,QByteArray>
    SBK_QtNetwork_QList_std_pair_QByteArray_QByteArray_IDX   = 12, // QList<std::pair<QByteArray,QByteArray>>
    SBK_QtNetwork_QMultiHash_QByteArray_QByteArray_IDX       = 13, // QMultiHash<QByteArray,QByteArray>
    SBK_QtNetwork_QMultiMap_QByteArray_QByteArray_IDX        = 14, // QMultiMap<QByteArray,QByteArray>
    SBK_QtNetwork_QHash_QString_QVariant_IDX                 = 15, // QHash<QString,QVariant>
    SBK_QtNetwork_QMap_QString_QVariant_IDX                  = 16, // QMap<QString,QVariant>
    SBK_QtNetwork_QList_QNetworkCookie_IDX                   = 17, // QList<QNetworkCookie>
    SBK_QtNetwork_QList_QHstsPolicy_IDX                      = 18, // QList<QHstsPolicy>
    SBK_QtNetwork_QList_QSslError_IDX                        = 19, // QList<QSslError>
    SBK_QtNetwork_QList_QDnsDomainNameRecord_IDX             = 20, // QList<QDnsDomainNameRecord>
    SBK_QtNetwork_QList_QDnsHostAddressRecord_IDX            = 21, // QList<QDnsHostAddressRecord>
    SBK_QtNetwork_QList_QDnsMailExchangeRecord_IDX           = 22, // QList<QDnsMailExchangeRecord>
    SBK_QtNetwork_QList_QDnsServiceRecord_IDX                = 23, // QList<QDnsServiceRecord>
    SBK_QtNetwork_QList_QDnsTextRecord_IDX                   = 24, // QList<QDnsTextRecord>
    SBK_QtNetwork_QList_QDnsTlsAssociationRecord_IDX         = 25, // QList<QDnsTlsAssociationRecord>
    SBK_QtNetwork_std_pair_QHostAddress_int_IDX              = 26, // std::pair<QHostAddress,int>
    SBK_QtNetwork_QList_QString_IDX                          = 27, // QList<QString>
    SBK_QtNetwork_QList_QSsl_ImplementedClass_IDX            = 28, // QList<QSsl::ImplementedClass>
    SBK_QtNetwork_QList_QOcspResponse_IDX                    = 29, // QList<QOcspResponse>
    SBK_QtNetwork_QList_QSsl_SupportedFeature_IDX            = 30, // QList<QSsl::SupportedFeature>
    SBK_QtNetwork_QList_QSsl_SslProtocol_IDX                 = 31, // QList<QSsl::SslProtocol>
    SBK_QtNetwork_QList_QSslCertificateExtension_IDX         = 32, // QList<QSslCertificateExtension>
    SBK_QtNetwork_QMultiMap_QSsl_AlternativeNameEntryType_QString_IDX = 33, // QMultiMap<QSsl::AlternativeNameEntryType,QString>
    SBK_QtNetwork_QList_QVariant_IDX                         = 34, // QList<QVariant>
    SBK_QtNetwork_CONVERTERS_IDX_COUNT                       = 35,
};
// Macros for type check

QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
namespace Shiboken
{

// PyType functions, to get the PyObjectType for a type T
#if QT_CONFIG(ssl)
template<> inline PyTypeObject *SbkType< ::QDtlsError >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QDtlsError_IDX]); }
#endif
#if QT_CONFIG(ssl)
template<> inline PyTypeObject *SbkType< ::QOcspCertificateStatus >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QOcspCertificateStatus_IDX]); }
#endif
#if QT_CONFIG(ssl)
template<> inline PyTypeObject *SbkType< ::QOcspRevocationReason >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QOcspRevocationReason_IDX]); }
#endif
template<> inline PyTypeObject *SbkType< ::QAbstractNetworkCache >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QAbstractNetworkCache_IDX]); }
template<> inline PyTypeObject *SbkType< ::QAbstractSocket::SocketType >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QAbstractSocket_SocketType_IDX]); }
template<> inline PyTypeObject *SbkType< ::QAbstractSocket::NetworkLayerProtocol >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QAbstractSocket_NetworkLayerProtocol_IDX]); }
template<> inline PyTypeObject *SbkType< ::QAbstractSocket::SocketError >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QAbstractSocket_SocketError_IDX]); }
template<> inline PyTypeObject *SbkType< ::QAbstractSocket::SocketState >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QAbstractSocket_SocketState_IDX]); }
template<> inline PyTypeObject *SbkType< ::QAbstractSocket::SocketOption >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QAbstractSocket_SocketOption_IDX]); }
template<> inline PyTypeObject *SbkType< ::QAbstractSocket::BindFlag >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QAbstractSocket_BindFlag_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QAbstractSocket::BindFlag> >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QFlags_QAbstractSocket_BindFlag_IDX]); }
template<> inline PyTypeObject *SbkType< ::QAbstractSocket::PauseMode >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QAbstractSocket_PauseMode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QAbstractSocket::PauseMode> >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QFlags_QAbstractSocket_PauseMode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QAbstractSocket >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QAbstractSocket_IDX]); }
template<> inline PyTypeObject *SbkType< ::QAuthenticator >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QAuthenticator_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDnsDomainNameRecord >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QDnsDomainNameRecord_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDnsHostAddressRecord >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QDnsHostAddressRecord_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDnsLookup::Error >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QDnsLookup_Error_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDnsLookup::Type >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QDnsLookup_Type_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDnsLookup::Protocol >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QDnsLookup_Protocol_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDnsLookup >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QDnsLookup_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDnsMailExchangeRecord >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QDnsMailExchangeRecord_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDnsServiceRecord >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QDnsServiceRecord_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDnsTextRecord >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QDnsTextRecord_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDnsTlsAssociationRecord::CertificateUsage >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QDnsTlsAssociationRecord_CertificateUsage_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDnsTlsAssociationRecord::Selector >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QDnsTlsAssociationRecord_Selector_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDnsTlsAssociationRecord::MatchingType >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QDnsTlsAssociationRecord_MatchingType_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDnsTlsAssociationRecord >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QDnsTlsAssociationRecord_IDX]); }
#if QT_CONFIG(dtls)
template<> inline PyTypeObject *SbkType< ::QDtls::HandshakeState >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QDtls_HandshakeState_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDtls >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QDtls_IDX]); }
#endif
#if QT_CONFIG(dtls)
template<> inline PyTypeObject *SbkType< ::QDtlsClientVerifier >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QDtlsClientVerifier_IDX]); }
#endif
#if QT_CONFIG(dtls)
template<> inline PyTypeObject *SbkType< ::QDtlsClientVerifier::GeneratorParameters >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QDtlsClientVerifier_GeneratorParameters_IDX]); }
#endif
template<> inline PyTypeObject *SbkType< ::QFormDataBuilder::Option >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QFormDataBuilder_Option_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QFormDataBuilder::Option> >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QFlags_QFormDataBuilder_Option_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFormDataBuilder >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QFormDataBuilder_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFormDataPartBuilder >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QFormDataPartBuilder_IDX]); }
template<> inline PyTypeObject *SbkType< ::QHostAddress::SpecialAddress >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QHostAddress_SpecialAddress_IDX]); }
template<> inline PyTypeObject *SbkType< ::QHostAddress::ConversionModeFlag >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QHostAddress_ConversionModeFlag_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QHostAddress::ConversionModeFlag> >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QFlags_QHostAddress_ConversionModeFlag_IDX]); }
template<> inline PyTypeObject *SbkType< ::QHostAddress >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QHostAddress_IDX]); }
template<> inline PyTypeObject *SbkType< ::QHostInfo::HostInfoError >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QHostInfo_HostInfoError_IDX]); }
template<> inline PyTypeObject *SbkType< ::QHostInfo >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QHostInfo_IDX]); }
template<> inline PyTypeObject *SbkType< ::QHstsPolicy::PolicyFlag >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QHstsPolicy_PolicyFlag_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QHstsPolicy::PolicyFlag> >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QFlags_QHstsPolicy_PolicyFlag_IDX]); }
template<> inline PyTypeObject *SbkType< ::QHstsPolicy >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QHstsPolicy_IDX]); }
template<> inline PyTypeObject *SbkType< ::QHttp1Configuration >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QHttp1Configuration_IDX]); }
template<> inline PyTypeObject *SbkType< ::QHttp2Configuration >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QHttp2Configuration_IDX]); }
template<> inline PyTypeObject *SbkType< ::QHttpHeaders::WellKnownHeader >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QHttpHeaders_WellKnownHeader_IDX]); }
template<> inline PyTypeObject *SbkType< ::QHttpHeaders >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QHttpHeaders_IDX]); }
template<> inline PyTypeObject *SbkType< ::QHttpMultiPart::ContentType >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QHttpMultiPart_ContentType_IDX]); }
template<> inline PyTypeObject *SbkType< ::QHttpMultiPart >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QHttpMultiPart_IDX]); }
template<> inline PyTypeObject *SbkType< ::QHttpPart >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QHttpPart_IDX]); }
template<> inline PyTypeObject *SbkType< ::QIPv6Address >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QIPv6Address_IDX]); }
template<> inline PyTypeObject *SbkType< ::QLocalServer::SocketOption >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QLocalServer_SocketOption_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QLocalServer::SocketOption> >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QFlags_QLocalServer_SocketOption_IDX]); }
template<> inline PyTypeObject *SbkType< ::QLocalServer >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QLocalServer_IDX]); }
template<> inline PyTypeObject *SbkType< ::QLocalSocket::LocalSocketError >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QLocalSocket_LocalSocketError_IDX]); }
template<> inline PyTypeObject *SbkType< ::QLocalSocket::LocalSocketState >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QLocalSocket_LocalSocketState_IDX]); }
template<> inline PyTypeObject *SbkType< ::QLocalSocket::SocketOption >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QLocalSocket_SocketOption_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QLocalSocket::SocketOption> >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QFlags_QLocalSocket_SocketOption_IDX]); }
template<> inline PyTypeObject *SbkType< ::QLocalSocket >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QLocalSocket_IDX]); }
template<> inline PyTypeObject *SbkType< ::QNetworkAccessManager::Operation >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QNetworkAccessManager_Operation_IDX]); }
template<> inline PyTypeObject *SbkType< ::QNetworkAccessManager >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QNetworkAccessManager_IDX]); }
#if QT_CONFIG(networkinterface)
template<> inline PyTypeObject *SbkType< ::QNetworkAddressEntry::DnsEligibilityStatus >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QNetworkAddressEntry_DnsEligibilityStatus_IDX]); }
template<> inline PyTypeObject *SbkType< ::QNetworkAddressEntry >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QNetworkAddressEntry_IDX]); }
#endif
template<> inline PyTypeObject *SbkType< ::QNetworkCacheMetaData >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QNetworkCacheMetaData_IDX]); }
template<> inline PyTypeObject *SbkType< ::QNetworkCookie::RawForm >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QNetworkCookie_RawForm_IDX]); }
template<> inline PyTypeObject *SbkType< ::QNetworkCookie::SameSite >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QNetworkCookie_SameSite_IDX]); }
template<> inline PyTypeObject *SbkType< ::QNetworkCookie >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QNetworkCookie_IDX]); }
template<> inline PyTypeObject *SbkType< ::QNetworkCookieJar >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QNetworkCookieJar_IDX]); }
template<> inline PyTypeObject *SbkType< ::QNetworkDatagram >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QNetworkDatagram_IDX]); }
template<> inline PyTypeObject *SbkType< ::QNetworkDiskCache >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QNetworkDiskCache_IDX]); }
template<> inline PyTypeObject *SbkType< ::QNetworkInformation::Reachability >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QNetworkInformation_Reachability_IDX]); }
template<> inline PyTypeObject *SbkType< ::QNetworkInformation::TransportMedium >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QNetworkInformation_TransportMedium_IDX]); }
template<> inline PyTypeObject *SbkType< ::QNetworkInformation::Feature >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QNetworkInformation_Feature_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QNetworkInformation::Feature> >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QFlags_QNetworkInformation_Feature_IDX]); }
template<> inline PyTypeObject *SbkType< ::QNetworkInformation >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QNetworkInformation_IDX]); }
#if QT_CONFIG(networkinterface)
template<> inline PyTypeObject *SbkType< ::QNetworkInterface::InterfaceFlag >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QNetworkInterface_InterfaceFlag_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QNetworkInterface::InterfaceFlag> >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QFlags_QNetworkInterface_InterfaceFlag_IDX]); }
template<> inline PyTypeObject *SbkType< ::QNetworkInterface::InterfaceType >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QNetworkInterface_InterfaceType_IDX]); }
template<> inline PyTypeObject *SbkType< ::QNetworkInterface >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QNetworkInterface_IDX]); }
#endif
template<> inline PyTypeObject *SbkType< ::QNetworkProxy::ProxyType >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QNetworkProxy_ProxyType_IDX]); }
template<> inline PyTypeObject *SbkType< ::QNetworkProxy::Capability >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QNetworkProxy_Capability_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QNetworkProxy::Capability> >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QFlags_QNetworkProxy_Capability_IDX]); }
template<> inline PyTypeObject *SbkType< ::QNetworkProxy >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QNetworkProxy_IDX]); }
template<> inline PyTypeObject *SbkType< ::QNetworkProxyFactory >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QNetworkProxyFactory_IDX]); }
template<> inline PyTypeObject *SbkType< ::QNetworkProxyQuery::QueryType >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QNetworkProxyQuery_QueryType_IDX]); }
template<> inline PyTypeObject *SbkType< ::QNetworkProxyQuery >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QNetworkProxyQuery_IDX]); }
template<> inline PyTypeObject *SbkType< ::QNetworkReply::NetworkError >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QNetworkReply_NetworkError_IDX]); }
template<> inline PyTypeObject *SbkType< ::QNetworkReply >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QNetworkReply_IDX]); }
template<> inline PyTypeObject *SbkType< ::QNetworkRequest::KnownHeaders >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QNetworkRequest_KnownHeaders_IDX]); }
template<> inline PyTypeObject *SbkType< ::QNetworkRequest::Attribute >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QNetworkRequest_Attribute_IDX]); }
template<> inline PyTypeObject *SbkType< ::QNetworkRequest::CacheLoadControl >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QNetworkRequest_CacheLoadControl_IDX]); }
template<> inline PyTypeObject *SbkType< ::QNetworkRequest::LoadControl >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QNetworkRequest_LoadControl_IDX]); }
template<> inline PyTypeObject *SbkType< ::QNetworkRequest::Priority >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QNetworkRequest_Priority_IDX]); }
template<> inline PyTypeObject *SbkType< ::QNetworkRequest::RedirectPolicy >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QNetworkRequest_RedirectPolicy_IDX]); }
template<> inline PyTypeObject *SbkType< ::QNetworkRequest::TransferTimeoutConstant >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QNetworkRequest_TransferTimeoutConstant_IDX]); }
template<> inline PyTypeObject *SbkType< ::QNetworkRequest >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QNetworkRequest_IDX]); }
template<> inline PyTypeObject *SbkType< ::QNetworkRequestFactory >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QNetworkRequestFactory_IDX]); }
#if QT_CONFIG(ssl)
template<> inline PyTypeObject *SbkType< ::QOcspResponse >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QOcspResponse_IDX]); }
#endif
template<> inline PyTypeObject *SbkType< ::QRestAccessManager >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QRestAccessManager_IDX]); }
template<> inline PyTypeObject *SbkType< ::QRestReply >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QRestReply_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSsl::KeyType >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QSsl_KeyType_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSsl::EncodingFormat >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QSsl_EncodingFormat_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSsl::KeyAlgorithm >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QSsl_KeyAlgorithm_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSsl::AlternativeNameEntryType >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QSsl_AlternativeNameEntryType_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSsl::SslProtocol >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QSsl_SslProtocol_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSsl::SslOption >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QSsl_SslOption_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QSsl::SslOption> >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QFlags_QSsl_SslOption_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSsl::AlertLevel >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QSsl_AlertLevel_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSsl::AlertType >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QSsl_AlertType_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSsl::ImplementedClass >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QSsl_ImplementedClass_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSsl::SupportedFeature >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QSsl_SupportedFeature_IDX]); }
#if QT_CONFIG(ssl)
template<> inline PyTypeObject *SbkType< ::QSslCertificate::SubjectInfo >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QSslCertificate_SubjectInfo_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSslCertificate::PatternSyntax >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QSslCertificate_PatternSyntax_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSslCertificate >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QSslCertificate_IDX]); }
#endif
#if QT_CONFIG(ssl)
template<> inline PyTypeObject *SbkType< ::QSslCertificateExtension >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QSslCertificateExtension_IDX]); }
#endif
#if QT_CONFIG(ssl)
template<> inline PyTypeObject *SbkType< ::QSslCipher >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QSslCipher_IDX]); }
#endif
#if QT_CONFIG(ssl)
template<> inline PyTypeObject *SbkType< ::QSslConfiguration::NextProtocolNegotiationStatus >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QSslConfiguration_NextProtocolNegotiationStatus_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSslConfiguration >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QSslConfiguration_IDX]); }
#endif
#if QT_CONFIG(ssl)
template<> inline PyTypeObject *SbkType< ::QSslDiffieHellmanParameters::Error >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QSslDiffieHellmanParameters_Error_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSslDiffieHellmanParameters >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QSslDiffieHellmanParameters_IDX]); }
#endif
#if QT_CONFIG(ssl)
template<> inline PyTypeObject *SbkType< ::QSslEllipticCurve >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QSslEllipticCurve_IDX]); }
#endif
#if QT_CONFIG(ssl)
template<> inline PyTypeObject *SbkType< ::QSslError::SslError >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QSslError_SslError_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSslError >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QSslError_IDX]); }
#endif
template<> inline PyTypeObject *SbkType< ::QSslKey >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QSslKey_IDX]); }
#if QT_CONFIG(ssl)
template<> inline PyTypeObject *SbkType< ::QSslPreSharedKeyAuthenticator >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QSslPreSharedKeyAuthenticator_IDX]); }
#endif
#if QT_CONFIG(ssl)
template<> inline PyTypeObject *SbkType< ::QSslServer >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QSslServer_IDX]); }
#endif
#if QT_CONFIG(ssl)
template<> inline PyTypeObject *SbkType< ::QSslSocket::SslMode >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QSslSocket_SslMode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSslSocket::PeerVerifyMode >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QSslSocket_PeerVerifyMode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSslSocket >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QSslSocket_IDX]); }
#endif
template<> inline PyTypeObject *SbkType< ::QTcpServer >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QTcpServer_IDX]); }
template<> inline PyTypeObject *SbkType< ::QTcpSocket >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QTcpSocket_IDX]); }
template<> inline PyTypeObject *SbkType< ::QUdpSocket >() { return Shiboken::Module::get(SbkPySide6_QtNetworkTypeStructs[SBK_QUdpSocket_IDX]); }

} // namespace Shiboken

QT_WARNING_POP
#endif // SBK_QTNETWORK_PYTHON_H

