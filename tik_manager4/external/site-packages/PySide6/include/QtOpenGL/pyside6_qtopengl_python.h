// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only


#ifndef SBK_QTOPENGL_PYTHON_H
#define SBK_QTOPENGL_PYTHON_H

#include <sbkpython.h>
#include <sbkmodule.h>
#include <sbkconverter.h>
// Module Includes
#include <pyside6_qtcore_python.h>
#include <pyside6_qtgui_python.h>

// Bound library includes
#include <QtOpenGL/qopenglbuffer.h>
#include <QtOpenGL/qopengldebug.h>
#include <QtOpenGL/qopenglframebufferobject.h>
#include <QtOpenGL/qopenglshaderprogram.h>
#include <QtOpenGL/qopengltexture.h>
#include <QtOpenGL/qopengltextureblitter.h>
#include <QtOpenGL/qopenglvertexarrayobject.h>
#include <QtOpenGL/qopenglwindow.h>

QT_BEGIN_NAMESPACE
class QAbstractOpenGLFunctions;
class QOpenGLFramebufferObjectFormat;
class QOpenGLFunctions_1_0;
class QOpenGLFunctions_1_1;
class QOpenGLFunctions_1_2;
class QOpenGLFunctions_1_3;
class QOpenGLFunctions_1_4;
class QOpenGLFunctions_1_5;
class QOpenGLFunctions_2_0;
class QOpenGLFunctions_2_1;
class QOpenGLFunctions_3_0;
class QOpenGLFunctions_3_1;
class QOpenGLFunctions_3_2_Compatibility;
class QOpenGLFunctions_3_2_Core;
class QOpenGLFunctions_3_3_Compatibility;
class QOpenGLFunctions_3_3_Core;
class QOpenGLFunctions_4_0_Compatibility;
class QOpenGLFunctions_4_0_Core;
class QOpenGLFunctions_4_1_Compatibility;
class QOpenGLFunctions_4_1_Core;
class QOpenGLFunctions_4_2_Compatibility;
class QOpenGLFunctions_4_2_Core;
class QOpenGLFunctions_4_3_Compatibility;
class QOpenGLFunctions_4_3_Core;
class QOpenGLFunctions_4_4_Compatibility;
class QOpenGLFunctions_4_4_Core;
class QOpenGLFunctions_4_5_Compatibility;
class QOpenGLFunctions_4_5_Core;
class QOpenGLPaintDevice;
class QOpenGLPixelTransferOptions;
class QOpenGLShaderProgram;
class QOpenGLTimeMonitor;
class QOpenGLTimerQuery;
class QOpenGLVersionFunctionsFactory;
class QOpenGLVersionProfile;
QT_END_NAMESPACE

// Type indices
enum [[deprecated]] : int {
    SBK_QABSTRACTOPENGLFUNCTIONS_IDX                         = 0,
    SBK_QOPENGLBUFFER_TYPE_IDX                               = 20,
    SBK_QOPENGLBUFFER_USAGEPATTERN_IDX                       = 22,
    SBK_QOPENGLBUFFER_ACCESS_IDX                             = 16,
    SBK_QOPENGLBUFFER_RANGEACCESSFLAG_IDX                    = 18,
    SBK_QFLAGS_QOPENGLBUFFER_RANGEACCESSFLAG_IDX             = 2,
    SBK_QOPENGLBUFFER_IDX                                    = 14,
    SBK_QOPENGLDEBUGLOGGER_LOGGINGMODE_IDX                   = 26,
    SBK_QOPENGLDEBUGLOGGER_IDX                               = 24,
    SBK_QOPENGLDEBUGMESSAGE_SOURCE_IDX                       = 32,
    SBK_QFLAGS_QOPENGLDEBUGMESSAGE_SOURCE_IDX                = 6,
    SBK_QOPENGLDEBUGMESSAGE_TYPE_IDX                         = 34,
    SBK_QFLAGS_QOPENGLDEBUGMESSAGE_TYPE_IDX                  = 8,
    SBK_QOPENGLDEBUGMESSAGE_SEVERITY_IDX                     = 30,
    SBK_QFLAGS_QOPENGLDEBUGMESSAGE_SEVERITY_IDX              = 4,
    SBK_QOPENGLDEBUGMESSAGE_IDX                              = 28,
    SBK_QOPENGLFRAMEBUFFEROBJECT_ATTACHMENT_IDX              = 38,
    SBK_QOPENGLFRAMEBUFFEROBJECT_FRAMEBUFFERRESTOREPOLICY_IDX = 40,
    SBK_QOPENGLFRAMEBUFFEROBJECT_IDX                         = 36,
    SBK_QOPENGLFRAMEBUFFEROBJECTFORMAT_IDX                   = 42,
    SBK_QOPENGLFUNCTIONS_1_0_IDX                             = 44,
    SBK_QOPENGLFUNCTIONS_1_1_IDX                             = 46,
    SBK_QOPENGLFUNCTIONS_1_2_IDX                             = 48,
    SBK_QOPENGLFUNCTIONS_1_3_IDX                             = 50,
    SBK_QOPENGLFUNCTIONS_1_4_IDX                             = 52,
    SBK_QOPENGLFUNCTIONS_1_5_IDX                             = 54,
    SBK_QOPENGLFUNCTIONS_2_0_IDX                             = 56,
    SBK_QOPENGLFUNCTIONS_2_1_IDX                             = 58,
    SBK_QOPENGLFUNCTIONS_3_0_IDX                             = 60,
    SBK_QOPENGLFUNCTIONS_3_1_IDX                             = 62,
    SBK_QOPENGLFUNCTIONS_3_2_COMPATIBILITY_IDX               = 64,
    SBK_QOPENGLFUNCTIONS_3_2_CORE_IDX                        = 66,
    SBK_QOPENGLFUNCTIONS_3_3_COMPATIBILITY_IDX               = 68,
    SBK_QOPENGLFUNCTIONS_3_3_CORE_IDX                        = 70,
    SBK_QOPENGLFUNCTIONS_4_0_COMPATIBILITY_IDX               = 72,
    SBK_QOPENGLFUNCTIONS_4_0_CORE_IDX                        = 74,
    SBK_QOPENGLFUNCTIONS_4_1_COMPATIBILITY_IDX               = 76,
    SBK_QOPENGLFUNCTIONS_4_1_CORE_IDX                        = 78,
    SBK_QOPENGLFUNCTIONS_4_2_COMPATIBILITY_IDX               = 80,
    SBK_QOPENGLFUNCTIONS_4_2_CORE_IDX                        = 82,
    SBK_QOPENGLFUNCTIONS_4_3_COMPATIBILITY_IDX               = 84,
    SBK_QOPENGLFUNCTIONS_4_3_CORE_IDX                        = 86,
    SBK_QOPENGLFUNCTIONS_4_4_COMPATIBILITY_IDX               = 88,
    SBK_QOPENGLFUNCTIONS_4_4_CORE_IDX                        = 90,
    SBK_QOPENGLFUNCTIONS_4_5_COMPATIBILITY_IDX               = 92,
    SBK_QOPENGLFUNCTIONS_4_5_CORE_IDX                        = 94,
    SBK_QOPENGLPAINTDEVICE_IDX                               = 96,
    SBK_QOPENGLPIXELTRANSFEROPTIONS_IDX                      = 98,
    SBK_QOPENGLSHADER_SHADERTYPEBIT_IDX                      = 102,
    SBK_QFLAGS_QOPENGLSHADER_SHADERTYPEBIT_IDX               = 10,
    SBK_QOPENGLSHADER_IDX                                    = 100,
    SBK_QOPENGLSHADERPROGRAM_IDX                             = 104,
    SBK_QOPENGLTEXTURE_TARGET_IDX                            = 134,
    SBK_QOPENGLTEXTURE_BINDINGTARGET_IDX                     = 108,
    SBK_QOPENGLTEXTURE_MIPMAPGENERATION_IDX                  = 124,
    SBK_QOPENGLTEXTURE_TEXTUREUNITRESET_IDX                  = 140,
    SBK_QOPENGLTEXTURE_TEXTUREFORMAT_IDX                     = 136,
    SBK_QOPENGLTEXTURE_TEXTUREFORMATCLASS_IDX                = 138,
    SBK_QOPENGLTEXTURE_CUBEMAPFACE_IDX                       = 116,
    SBK_QOPENGLTEXTURE_PIXELFORMAT_IDX                       = 126,
    SBK_QOPENGLTEXTURE_PIXELTYPE_IDX                         = 128,
    SBK_QOPENGLTEXTURE_SWIZZLECOMPONENT_IDX                  = 130,
    SBK_QOPENGLTEXTURE_SWIZZLEVALUE_IDX                      = 132,
    SBK_QOPENGLTEXTURE_WRAPMODE_IDX                          = 142,
    SBK_QOPENGLTEXTURE_COORDINATEDIRECTION_IDX               = 114,
    SBK_QOPENGLTEXTURE_FEATURE_IDX                           = 120,
    SBK_QFLAGS_QOPENGLTEXTURE_FEATURE_IDX                    = 12,
    SBK_QOPENGLTEXTURE_DEPTHSTENCILMODE_IDX                  = 118,
    SBK_QOPENGLTEXTURE_COMPARISONFUNCTION_IDX                = 110,
    SBK_QOPENGLTEXTURE_COMPARISONMODE_IDX                    = 112,
    SBK_QOPENGLTEXTURE_FILTER_IDX                            = 122,
    SBK_QOPENGLTEXTURE_IDX                                   = 106,
    SBK_QOPENGLTEXTUREBLITTER_ORIGIN_IDX                     = 146,
    SBK_QOPENGLTEXTUREBLITTER_IDX                            = 144,
    SBK_QOPENGLTIMEMONITOR_IDX                               = 148,
    SBK_QOPENGLTIMERQUERY_IDX                                = 150,
    SBK_QOPENGLVERSIONFUNCTIONSFACTORY_IDX                   = 152,
    SBK_QOPENGLVERSIONPROFILE_IDX                            = 154,
    SBK_QOPENGLVERTEXARRAYOBJECT_IDX                         = 156,
    SBK_QOPENGLVERTEXARRAYOBJECT_BINDER_IDX                  = 158,
    SBK_QOPENGLWINDOW_UPDATEBEHAVIOR_IDX                     = 162,
    SBK_QOPENGLWINDOW_IDX                                    = 160,
    SBK_QTOPENGL_IDX_COUNT                                   = 164,
};

// Type indices
enum : int {
    SBK_QAbstractOpenGLFunctions_IDX                         = 0,
    SBK_QOpenGLBuffer_Type_IDX                               = 10,
    SBK_QOpenGLBuffer_UsagePattern_IDX                       = 11,
    SBK_QOpenGLBuffer_Access_IDX                             = 8,
    SBK_QOpenGLBuffer_RangeAccessFlag_IDX                    = 9,
    SBK_QFlags_QOpenGLBuffer_RangeAccessFlag_IDX             = 1,
    SBK_QOpenGLBuffer_IDX                                    = 7,
    SBK_QOpenGLDebugLogger_LoggingMode_IDX                   = 13,
    SBK_QOpenGLDebugLogger_IDX                               = 12,
    SBK_QOpenGLDebugMessage_Source_IDX                       = 16,
    SBK_QFlags_QOpenGLDebugMessage_Source_IDX                = 3,
    SBK_QOpenGLDebugMessage_Type_IDX                         = 17,
    SBK_QFlags_QOpenGLDebugMessage_Type_IDX                  = 4,
    SBK_QOpenGLDebugMessage_Severity_IDX                     = 15,
    SBK_QFlags_QOpenGLDebugMessage_Severity_IDX              = 2,
    SBK_QOpenGLDebugMessage_IDX                              = 14,
    SBK_QOpenGLFramebufferObject_Attachment_IDX              = 19,
    SBK_QOpenGLFramebufferObject_FramebufferRestorePolicy_IDX = 20,
    SBK_QOpenGLFramebufferObject_IDX                         = 18,
    SBK_QOpenGLFramebufferObjectFormat_IDX                   = 21,
    SBK_QOpenGLFunctions_1_0_IDX                             = 22,
    SBK_QOpenGLFunctions_1_1_IDX                             = 23,
    SBK_QOpenGLFunctions_1_2_IDX                             = 24,
    SBK_QOpenGLFunctions_1_3_IDX                             = 25,
    SBK_QOpenGLFunctions_1_4_IDX                             = 26,
    SBK_QOpenGLFunctions_1_5_IDX                             = 27,
    SBK_QOpenGLFunctions_2_0_IDX                             = 28,
    SBK_QOpenGLFunctions_2_1_IDX                             = 29,
    SBK_QOpenGLFunctions_3_0_IDX                             = 30,
    SBK_QOpenGLFunctions_3_1_IDX                             = 31,
    SBK_QOpenGLFunctions_3_2_Compatibility_IDX               = 32,
    SBK_QOpenGLFunctions_3_2_Core_IDX                        = 33,
    SBK_QOpenGLFunctions_3_3_Compatibility_IDX               = 34,
    SBK_QOpenGLFunctions_3_3_Core_IDX                        = 35,
    SBK_QOpenGLFunctions_4_0_Compatibility_IDX               = 36,
    SBK_QOpenGLFunctions_4_0_Core_IDX                        = 37,
    SBK_QOpenGLFunctions_4_1_Compatibility_IDX               = 38,
    SBK_QOpenGLFunctions_4_1_Core_IDX                        = 39,
    SBK_QOpenGLFunctions_4_2_Compatibility_IDX               = 40,
    SBK_QOpenGLFunctions_4_2_Core_IDX                        = 41,
    SBK_QOpenGLFunctions_4_3_Compatibility_IDX               = 42,
    SBK_QOpenGLFunctions_4_3_Core_IDX                        = 43,
    SBK_QOpenGLFunctions_4_4_Compatibility_IDX               = 44,
    SBK_QOpenGLFunctions_4_4_Core_IDX                        = 45,
    SBK_QOpenGLFunctions_4_5_Compatibility_IDX               = 46,
    SBK_QOpenGLFunctions_4_5_Core_IDX                        = 47,
    SBK_QOpenGLPaintDevice_IDX                               = 48,
    SBK_QOpenGLPixelTransferOptions_IDX                      = 49,
    SBK_QOpenGLShader_ShaderTypeBit_IDX                      = 51,
    SBK_QFlags_QOpenGLShader_ShaderTypeBit_IDX               = 5,
    SBK_QOpenGLShader_IDX                                    = 50,
    SBK_QOpenGLShaderProgram_IDX                             = 52,
    SBK_QOpenGLTexture_Target_IDX                            = 67,
    SBK_QOpenGLTexture_BindingTarget_IDX                     = 54,
    SBK_QOpenGLTexture_MipMapGeneration_IDX                  = 62,
    SBK_QOpenGLTexture_TextureUnitReset_IDX                  = 70,
    SBK_QOpenGLTexture_TextureFormat_IDX                     = 68,
    SBK_QOpenGLTexture_TextureFormatClass_IDX                = 69,
    SBK_QOpenGLTexture_CubeMapFace_IDX                       = 58,
    SBK_QOpenGLTexture_PixelFormat_IDX                       = 63,
    SBK_QOpenGLTexture_PixelType_IDX                         = 64,
    SBK_QOpenGLTexture_SwizzleComponent_IDX                  = 65,
    SBK_QOpenGLTexture_SwizzleValue_IDX                      = 66,
    SBK_QOpenGLTexture_WrapMode_IDX                          = 71,
    SBK_QOpenGLTexture_CoordinateDirection_IDX               = 57,
    SBK_QOpenGLTexture_Feature_IDX                           = 60,
    SBK_QFlags_QOpenGLTexture_Feature_IDX                    = 6,
    SBK_QOpenGLTexture_DepthStencilMode_IDX                  = 59,
    SBK_QOpenGLTexture_ComparisonFunction_IDX                = 55,
    SBK_QOpenGLTexture_ComparisonMode_IDX                    = 56,
    SBK_QOpenGLTexture_Filter_IDX                            = 61,
    SBK_QOpenGLTexture_IDX                                   = 53,
    SBK_QOpenGLTextureBlitter_Origin_IDX                     = 73,
    SBK_QOpenGLTextureBlitter_IDX                            = 72,
    SBK_QOpenGLTimeMonitor_IDX                               = 74,
    SBK_QOpenGLTimerQuery_IDX                                = 75,
    SBK_QOpenGLVersionFunctionsFactory_IDX                   = 76,
    SBK_QOpenGLVersionProfile_IDX                            = 77,
    SBK_QOpenGLVertexArrayObject_IDX                         = 78,
    SBK_QOpenGLVertexArrayObject_Binder_IDX                  = 79,
    SBK_QOpenGLWindow_UpdateBehavior_IDX                     = 81,
    SBK_QOpenGLWindow_IDX                                    = 80,
    SBK_QtOpenGL_IDX_COUNT                                   = 82,
};

// This variable stores all Python types exported by this module.
extern Shiboken::Module::TypeInitStruct *SbkPySide6_QtOpenGLTypeStructs;

// This variable stores all Python types exported by this module in a backwards compatible way with identical indexing.
[[deprecated]] extern PyTypeObject **SbkPySide6_QtOpenGLTypes;

// This variable stores the Python module object exported by this module.
extern PyObject *SbkPySide6_QtOpenGLModuleObject;

// This variable stores all type converters exported by this module.
extern SbkConverter **SbkPySide6_QtOpenGLTypeConverters;

// Converter indices
enum [[deprecated]] : int {
    SBK_QTOPENGL_QLIST_INT_IDX                               = 0, // QList<int>
    SBK_QTOPENGL_STD_PAIR_INT_INT_IDX                        = 2, // std::pair<int,int>
    SBK_QTOPENGL_STD_PAIR_FLOAT_FLOAT_IDX                    = 4, // std::pair<float,float>
    SBK_QTOPENGL_STD_PAIR_QOPENGLTEXTURE_FILTER_QOPENGLTEXTURE_FILTER_IDX = 6, // std::pair<QOpenGLTexture::Filter,QOpenGLTexture::Filter>
    SBK_QTOPENGL_QLIST_QSIZE_IDX                             = 8, // QList<QSize>
    SBK_QTOPENGL_QLIST_UNSIGNEDINT_IDX                       = 10, // QList<unsigned int>
    SBK_QTOPENGL_QLIST_UINT64_T_IDX                          = 12, // QList<uint64_t>
    SBK_QTOPENGL_QLIST_FLOAT_IDX                             = 14, // QList<float>
    SBK_QTOPENGL_QLIST_QOPENGLSHADERPTR_IDX                  = 16, // QList<QOpenGLShader*>
    SBK_QTOPENGL_QLIST_QOPENGLDEBUGMESSAGE_IDX               = 18, // QList<QOpenGLDebugMessage>
    SBK_QTOPENGL_QLIST_QVARIANT_IDX                          = 20, // QList<QVariant>
    SBK_QTOPENGL_QLIST_QSTRING_IDX                           = 22, // QList<QString>
    SBK_QTOPENGL_QMAP_QSTRING_QVARIANT_IDX                   = 24, // QMap<QString,QVariant>
    SBK_QTOPENGL_CONVERTERS_IDX_COUNT                        = 26,
};

// Converter indices
enum : int {
    SBK_QtOpenGL_QList_int_IDX                               = 0, // QList<int>
    SBK_QtOpenGL_std_pair_int_int_IDX                        = 1, // std::pair<int,int>
    SBK_QtOpenGL_std_pair_float_float_IDX                    = 2, // std::pair<float,float>
    SBK_QtOpenGL_std_pair_QOpenGLTexture_Filter_QOpenGLTexture_Filter_IDX = 3, // std::pair<QOpenGLTexture::Filter,QOpenGLTexture::Filter>
    SBK_QtOpenGL_QList_QSize_IDX                             = 4, // QList<QSize>
    SBK_QtOpenGL_QList_unsignedint_IDX                       = 5, // QList<unsigned int>
    SBK_QtOpenGL_QList_uint64_t_IDX                          = 6, // QList<uint64_t>
    SBK_QtOpenGL_QList_float_IDX                             = 7, // QList<float>
    SBK_QtOpenGL_QList_QOpenGLShaderPTR_IDX                  = 8, // QList<QOpenGLShader*>
    SBK_QtOpenGL_QList_QOpenGLDebugMessage_IDX               = 9, // QList<QOpenGLDebugMessage>
    SBK_QtOpenGL_QList_QVariant_IDX                          = 10, // QList<QVariant>
    SBK_QtOpenGL_QList_QString_IDX                           = 11, // QList<QString>
    SBK_QtOpenGL_QMap_QString_QVariant_IDX                   = 12, // QMap<QString,QVariant>
    SBK_QtOpenGL_CONVERTERS_IDX_COUNT                        = 13,
};
// Macros for type check

QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
namespace Shiboken
{

// PyType functions, to get the PyObjectType for a type T
template<> inline PyTypeObject *SbkType< ::QAbstractOpenGLFunctions >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QAbstractOpenGLFunctions_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLBuffer::Type >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLBuffer_Type_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLBuffer::UsagePattern >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLBuffer_UsagePattern_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLBuffer::Access >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLBuffer_Access_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLBuffer::RangeAccessFlag >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLBuffer_RangeAccessFlag_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QOpenGLBuffer::RangeAccessFlag> >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QFlags_QOpenGLBuffer_RangeAccessFlag_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLBuffer >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLBuffer_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLDebugLogger::LoggingMode >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLDebugLogger_LoggingMode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLDebugLogger >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLDebugLogger_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLDebugMessage::Source >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLDebugMessage_Source_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QOpenGLDebugMessage::Source> >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QFlags_QOpenGLDebugMessage_Source_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLDebugMessage::Type >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLDebugMessage_Type_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QOpenGLDebugMessage::Type> >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QFlags_QOpenGLDebugMessage_Type_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLDebugMessage::Severity >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLDebugMessage_Severity_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QOpenGLDebugMessage::Severity> >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QFlags_QOpenGLDebugMessage_Severity_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLDebugMessage >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLDebugMessage_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLFramebufferObject::Attachment >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLFramebufferObject_Attachment_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLFramebufferObject::FramebufferRestorePolicy >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLFramebufferObject_FramebufferRestorePolicy_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLFramebufferObject >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLFramebufferObject_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLFramebufferObjectFormat >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLFramebufferObjectFormat_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLFunctions_1_0 >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLFunctions_1_0_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLFunctions_1_1 >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLFunctions_1_1_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLFunctions_1_2 >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLFunctions_1_2_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLFunctions_1_3 >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLFunctions_1_3_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLFunctions_1_4 >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLFunctions_1_4_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLFunctions_1_5 >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLFunctions_1_5_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLFunctions_2_0 >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLFunctions_2_0_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLFunctions_2_1 >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLFunctions_2_1_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLFunctions_3_0 >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLFunctions_3_0_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLFunctions_3_1 >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLFunctions_3_1_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLFunctions_3_2_Compatibility >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLFunctions_3_2_Compatibility_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLFunctions_3_2_Core >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLFunctions_3_2_Core_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLFunctions_3_3_Compatibility >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLFunctions_3_3_Compatibility_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLFunctions_3_3_Core >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLFunctions_3_3_Core_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLFunctions_4_0_Compatibility >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLFunctions_4_0_Compatibility_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLFunctions_4_0_Core >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLFunctions_4_0_Core_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLFunctions_4_1_Compatibility >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLFunctions_4_1_Compatibility_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLFunctions_4_1_Core >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLFunctions_4_1_Core_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLFunctions_4_2_Compatibility >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLFunctions_4_2_Compatibility_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLFunctions_4_2_Core >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLFunctions_4_2_Core_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLFunctions_4_3_Compatibility >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLFunctions_4_3_Compatibility_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLFunctions_4_3_Core >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLFunctions_4_3_Core_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLFunctions_4_4_Compatibility >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLFunctions_4_4_Compatibility_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLFunctions_4_4_Core >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLFunctions_4_4_Core_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLFunctions_4_5_Compatibility >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLFunctions_4_5_Compatibility_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLFunctions_4_5_Core >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLFunctions_4_5_Core_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLPaintDevice >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLPaintDevice_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLPixelTransferOptions >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLPixelTransferOptions_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLShader::ShaderTypeBit >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLShader_ShaderTypeBit_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QOpenGLShader::ShaderTypeBit> >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QFlags_QOpenGLShader_ShaderTypeBit_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLShader >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLShader_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLShaderProgram >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLShaderProgram_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLTexture::Target >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLTexture_Target_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLTexture::BindingTarget >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLTexture_BindingTarget_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLTexture::MipMapGeneration >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLTexture_MipMapGeneration_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLTexture::TextureUnitReset >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLTexture_TextureUnitReset_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLTexture::TextureFormat >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLTexture_TextureFormat_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLTexture::TextureFormatClass >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLTexture_TextureFormatClass_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLTexture::CubeMapFace >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLTexture_CubeMapFace_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLTexture::PixelFormat >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLTexture_PixelFormat_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLTexture::PixelType >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLTexture_PixelType_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLTexture::SwizzleComponent >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLTexture_SwizzleComponent_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLTexture::SwizzleValue >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLTexture_SwizzleValue_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLTexture::WrapMode >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLTexture_WrapMode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLTexture::CoordinateDirection >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLTexture_CoordinateDirection_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLTexture::Feature >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLTexture_Feature_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QOpenGLTexture::Feature> >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QFlags_QOpenGLTexture_Feature_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLTexture::DepthStencilMode >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLTexture_DepthStencilMode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLTexture::ComparisonFunction >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLTexture_ComparisonFunction_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLTexture::ComparisonMode >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLTexture_ComparisonMode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLTexture::Filter >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLTexture_Filter_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLTexture >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLTexture_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLTextureBlitter::Origin >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLTextureBlitter_Origin_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLTextureBlitter >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLTextureBlitter_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLTimeMonitor >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLTimeMonitor_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLTimerQuery >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLTimerQuery_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLVersionFunctionsFactory >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLVersionFunctionsFactory_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLVersionProfile >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLVersionProfile_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLVertexArrayObject >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLVertexArrayObject_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLVertexArrayObject::Binder >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLVertexArrayObject_Binder_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLWindow::UpdateBehavior >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLWindow_UpdateBehavior_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLWindow >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLTypeStructs[SBK_QOpenGLWindow_IDX]); }

} // namespace Shiboken

QT_WARNING_POP
#endif // SBK_QTOPENGL_PYTHON_H

