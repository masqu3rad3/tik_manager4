// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only


#ifndef SBK_QTXML_PYTHON_H
#define SBK_QTXML_PYTHON_H

#include <sbkpython.h>
#include <sbkmodule.h>
#include <sbkconverter.h>
// Module Includes
#include <pyside6_qtcore_python.h>

// Bound library includes
#include <QtXml/qdom.h>

QT_BEGIN_NAMESPACE
class QDomAttr;
class QDomCDATASection;
class QDomCharacterData;
class QDomComment;
class QDomDocumentFragment;
class QDomDocumentType;
class QDomElement;
class QDomEntity;
class QDomEntityReference;
class QDomNamedNodeMap;
class QDomNodeList;
class QDomNotation;
class QDomProcessingInstruction;
class QDomText;
QT_END_NAMESPACE

// Type indices
enum [[deprecated]] : int {
    SBK_QDOMATTR_IDX                                         = 0,
    SBK_QDOMCDATASECTION_IDX                                 = 2,
    SBK_QDOMCHARACTERDATA_IDX                                = 4,
    SBK_QDOMCOMMENT_IDX                                      = 6,
    SBK_QDOMDOCUMENT_PARSEOPTION_IDX                         = 10,
    SBK_QFLAGS_QDOMDOCUMENT_PARSEOPTION_IDX                  = 44,
    SBK_QDOMDOCUMENT_IDX                                     = 8,
    SBK_QDOMDOCUMENT_PARSERESULT_IDX                         = 12,
    SBK_QDOMDOCUMENTFRAGMENT_IDX                             = 14,
    SBK_QDOMDOCUMENTTYPE_IDX                                 = 16,
    SBK_QDOMELEMENT_IDX                                      = 18,
    SBK_QDOMENTITY_IDX                                       = 20,
    SBK_QDOMENTITYREFERENCE_IDX                              = 22,
    SBK_QDOMIMPLEMENTATION_INVALIDDATAPOLICY_IDX             = 26,
    SBK_QDOMIMPLEMENTATION_IDX                               = 24,
    SBK_QDOMNAMEDNODEMAP_IDX                                 = 28,
    SBK_QDOMNODE_NODETYPE_IDX                                = 34,
    SBK_QDOMNODE_ENCODINGPOLICY_IDX                          = 32,
    SBK_QDOMNODE_IDX                                         = 30,
    SBK_QDOMNODELIST_IDX                                     = 36,
    SBK_QDOMNOTATION_IDX                                     = 38,
    SBK_QDOMPROCESSINGINSTRUCTION_IDX                        = 40,
    SBK_QDOMTEXT_IDX                                         = 42,
    SBK_QTXML_IDX_COUNT                                      = 46,
};

// Type indices
enum : int {
    SBK_QDomAttr_IDX                                         = 0,
    SBK_QDomCDATASection_IDX                                 = 1,
    SBK_QDomCharacterData_IDX                                = 2,
    SBK_QDomComment_IDX                                      = 3,
    SBK_QDomDocument_ParseOption_IDX                         = 5,
    SBK_QFlags_QDomDocument_ParseOption_IDX                  = 22,
    SBK_QDomDocument_IDX                                     = 4,
    SBK_QDomDocument_ParseResult_IDX                         = 6,
    SBK_QDomDocumentFragment_IDX                             = 7,
    SBK_QDomDocumentType_IDX                                 = 8,
    SBK_QDomElement_IDX                                      = 9,
    SBK_QDomEntity_IDX                                       = 10,
    SBK_QDomEntityReference_IDX                              = 11,
    SBK_QDomImplementation_InvalidDataPolicy_IDX             = 13,
    SBK_QDomImplementation_IDX                               = 12,
    SBK_QDomNamedNodeMap_IDX                                 = 14,
    SBK_QDomNode_NodeType_IDX                                = 17,
    SBK_QDomNode_EncodingPolicy_IDX                          = 16,
    SBK_QDomNode_IDX                                         = 15,
    SBK_QDomNodeList_IDX                                     = 18,
    SBK_QDomNotation_IDX                                     = 19,
    SBK_QDomProcessingInstruction_IDX                        = 20,
    SBK_QDomText_IDX                                         = 21,
    SBK_QtXml_IDX_COUNT                                      = 23,
};

// This variable stores all Python types exported by this module.
extern Shiboken::Module::TypeInitStruct *SbkPySide6_QtXmlTypeStructs;

// This variable stores all Python types exported by this module in a backwards compatible way with identical indexing.
[[deprecated]] extern PyTypeObject **SbkPySide6_QtXmlTypes;

// This variable stores the Python module object exported by this module.
extern PyObject *SbkPySide6_QtXmlModuleObject;

// This variable stores all type converters exported by this module.
extern SbkConverter **SbkPySide6_QtXmlTypeConverters;

// Converter indices
enum [[deprecated]] : int {
    SBK_QTXML_QLIST_INT_IDX                                  = 0, // QList<int>
    SBK_QTXML_QLIST_QVARIANT_IDX                             = 2, // QList<QVariant>
    SBK_QTXML_QLIST_QSTRING_IDX                              = 4, // QList<QString>
    SBK_QTXML_QMAP_QSTRING_QVARIANT_IDX                      = 6, // QMap<QString,QVariant>
    SBK_QTXML_CONVERTERS_IDX_COUNT                           = 8,
};

// Converter indices
enum : int {
    SBK_QtXml_QList_int_IDX                                  = 0, // QList<int>
    SBK_QtXml_QList_QVariant_IDX                             = 1, // QList<QVariant>
    SBK_QtXml_QList_QString_IDX                              = 2, // QList<QString>
    SBK_QtXml_QMap_QString_QVariant_IDX                      = 3, // QMap<QString,QVariant>
    SBK_QtXml_CONVERTERS_IDX_COUNT                           = 4,
};
// Macros for type check

QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
namespace Shiboken
{

// PyType functions, to get the PyObjectType for a type T
template<> inline PyTypeObject *SbkType< ::QDomAttr >() { return Shiboken::Module::get(SbkPySide6_QtXmlTypeStructs[SBK_QDomAttr_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDomCDATASection >() { return Shiboken::Module::get(SbkPySide6_QtXmlTypeStructs[SBK_QDomCDATASection_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDomCharacterData >() { return Shiboken::Module::get(SbkPySide6_QtXmlTypeStructs[SBK_QDomCharacterData_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDomComment >() { return Shiboken::Module::get(SbkPySide6_QtXmlTypeStructs[SBK_QDomComment_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDomDocument::ParseOption >() { return Shiboken::Module::get(SbkPySide6_QtXmlTypeStructs[SBK_QDomDocument_ParseOption_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QDomDocument::ParseOption> >() { return Shiboken::Module::get(SbkPySide6_QtXmlTypeStructs[SBK_QFlags_QDomDocument_ParseOption_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDomDocument >() { return Shiboken::Module::get(SbkPySide6_QtXmlTypeStructs[SBK_QDomDocument_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDomDocument::ParseResult >() { return Shiboken::Module::get(SbkPySide6_QtXmlTypeStructs[SBK_QDomDocument_ParseResult_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDomDocumentFragment >() { return Shiboken::Module::get(SbkPySide6_QtXmlTypeStructs[SBK_QDomDocumentFragment_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDomDocumentType >() { return Shiboken::Module::get(SbkPySide6_QtXmlTypeStructs[SBK_QDomDocumentType_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDomElement >() { return Shiboken::Module::get(SbkPySide6_QtXmlTypeStructs[SBK_QDomElement_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDomEntity >() { return Shiboken::Module::get(SbkPySide6_QtXmlTypeStructs[SBK_QDomEntity_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDomEntityReference >() { return Shiboken::Module::get(SbkPySide6_QtXmlTypeStructs[SBK_QDomEntityReference_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDomImplementation::InvalidDataPolicy >() { return Shiboken::Module::get(SbkPySide6_QtXmlTypeStructs[SBK_QDomImplementation_InvalidDataPolicy_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDomImplementation >() { return Shiboken::Module::get(SbkPySide6_QtXmlTypeStructs[SBK_QDomImplementation_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDomNamedNodeMap >() { return Shiboken::Module::get(SbkPySide6_QtXmlTypeStructs[SBK_QDomNamedNodeMap_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDomNode::NodeType >() { return Shiboken::Module::get(SbkPySide6_QtXmlTypeStructs[SBK_QDomNode_NodeType_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDomNode::EncodingPolicy >() { return Shiboken::Module::get(SbkPySide6_QtXmlTypeStructs[SBK_QDomNode_EncodingPolicy_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDomNode >() { return Shiboken::Module::get(SbkPySide6_QtXmlTypeStructs[SBK_QDomNode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDomNodeList >() { return Shiboken::Module::get(SbkPySide6_QtXmlTypeStructs[SBK_QDomNodeList_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDomNotation >() { return Shiboken::Module::get(SbkPySide6_QtXmlTypeStructs[SBK_QDomNotation_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDomProcessingInstruction >() { return Shiboken::Module::get(SbkPySide6_QtXmlTypeStructs[SBK_QDomProcessingInstruction_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDomText >() { return Shiboken::Module::get(SbkPySide6_QtXmlTypeStructs[SBK_QDomText_IDX]); }

} // namespace Shiboken

QT_WARNING_POP
#endif // SBK_QTXML_PYTHON_H

