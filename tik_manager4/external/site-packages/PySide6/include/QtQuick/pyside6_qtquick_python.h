// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only


#ifndef SBK_QTQUICK_PYTHON_H
#define SBK_QTQUICK_PYTHON_H

#include <sbkpython.h>
#include <sbkmodule.h>
#include <sbkconverter.h>
// Module Includes
#include <pyside6_qtcore_python.h>
#include <pyside6_qtnetwork_python.h>
#include <pyside6_qtgui_python.h>
#include <pyside6_qtopengl_python.h>
#include <pyside6_qtqml_python.h>

// Bound library includes
#include <QtQuick/qquickframebufferobject.h>
#include <QtQuick/qquickitem.h>
#include <QtQuick/qquickopenglutils.h>
#include <QtQuick/qquickpainteditem.h>
#include <QtQuick/qquickrendertarget.h>
#include <QtQuick/qquickrhiitem.h>
#include <QtQuick/qquicktextdocument.h>
#include <QtQuick/qquickview.h>
#include <QtQuick/qquickwindow.h>
#include <QtQuick/qsggeometry.h>
#include <QtQuick/qsgimagenode.h>
#include <QtQuick/qsgmaterial.h>
#include <QtQuick/qsgmaterialshader.h>
#include <QtQuick/qsgnode.h>
#include <QtQuick/qsgrendererinterface.h>
#include <QtQuick/qsgrendernode.h>
#include <QtQuick/qsgsimpletexturenode.h>
#include <QtQuick/qsgtextnode.h>
#include <QtQuick/qsgtexture.h>
#include <qsharedpointer.h>

QT_BEGIN_NAMESPACE
class QQuickAsyncImageProvider;
class QQuickGraphicsConfiguration;
class QQuickGraphicsDevice;
class QQuickImageProvider;
class QQuickImageResponse;
class QQuickItemGrabResult;
class QQuickRenderControl;
class QQuickRhiItemRenderer;
class QQuickTextureFactory;
class QQuickTransform;
class QSGBasicGeometryNode;
class QSGClipNode;
class QSGDynamicTexture;
class QSGFlatColorMaterial;
class QSGGeometryNode;
struct QSGMaterialType;
class QSGNinePatchNode;
class QSGNodeVisitor;
class QSGOpacityNode;
class QSGOpaqueTextureMaterial;
class QSGRectangleNode;
class QSGRootNode;
class QSGSimpleRectNode;
class QSGTextureMaterial;
class QSGTextureProvider;
class QSGTransformNode;
class QSGVertexColorMaterial;
QT_END_NAMESPACE

// Type indices
enum [[deprecated]] : int {
    SBK_QQUICKASYNCIMAGEPROVIDER_IDX                         = 32,
    SBK_QQUICKFRAMEBUFFEROBJECT_IDX                          = 34,
    SBK_QQUICKFRAMEBUFFEROBJECT_RENDERER_IDX                 = 36,
    SBK_QQUICKGRAPHICSCONFIGURATION_IDX                      = 38,
    SBK_QQUICKGRAPHICSDEVICE_IDX                             = 40,
    SBK_QQUICKIMAGEPROVIDER_IDX                              = 42,
    SBK_QQUICKIMAGERESPONSE_IDX                              = 44,
    SBK_QQUICKITEM_FLAG_IDX                                  = 48,
    SBK_QFLAGS_QQUICKITEM_FLAG_IDX                           = 0,
    SBK_QQUICKITEM_ITEMCHANGE_IDX                            = 50,
    SBK_QQUICKITEM_TRANSFORMORIGIN_IDX                       = 52,
    SBK_QQUICKITEM_IDX                                       = 46,
    SBK_QQUICKITEM_UPDATEPAINTNODEDATA_IDX                   = 54,
    SBK_QQUICKITEMGRABRESULT_IDX                             = 56,
    SBK_QTQUICKQQUICKOPENGLUTILS_IDX                         = 58,
    SBK_QQUICKPAINTEDITEM_RENDERTARGET_IDX                   = 64,
    SBK_QQUICKPAINTEDITEM_PERFORMANCEHINT_IDX                = 62,
    SBK_QFLAGS_QQUICKPAINTEDITEM_PERFORMANCEHINT_IDX         = 2,
    SBK_QQUICKPAINTEDITEM_IDX                                = 60,
    SBK_QQUICKRENDERCONTROL_IDX                              = 66,
    SBK_QQUICKRENDERTARGET_FLAG_IDX                          = 70,
    SBK_QFLAGS_QQUICKRENDERTARGET_FLAG_IDX                   = 4,
    SBK_QQUICKRENDERTARGET_IDX                               = 68,
    SBK_QQUICKRHIITEM_TEXTUREFORMAT_IDX                      = 74,
    SBK_QQUICKRHIITEM_IDX                                    = 72,
    SBK_QQUICKRHIITEMRENDERER_IDX                            = 76,
    SBK_QQUICKTEXTDOCUMENT_STATUS_IDX                        = 80,
    SBK_QQUICKTEXTDOCUMENT_IDX                               = 78,
    SBK_QQUICKTEXTUREFACTORY_IDX                             = 82,
    SBK_QQUICKTRANSFORM_IDX                                  = 84,
    SBK_QQUICKVIEW_RESIZEMODE_IDX                            = 88,
    SBK_QQUICKVIEW_STATUS_IDX                                = 90,
    SBK_QQUICKVIEW_IDX                                       = 86,
    SBK_QQUICKWINDOW_CREATETEXTUREOPTION_IDX                 = 94,
    SBK_QFLAGS_QQUICKWINDOW_CREATETEXTUREOPTION_IDX          = 6,
    SBK_QQUICKWINDOW_RENDERSTAGE_IDX                         = 98,
    SBK_QQUICKWINDOW_SCENEGRAPHERROR_IDX                     = 100,
    SBK_QQUICKWINDOW_TEXTRENDERTYPE_IDX                      = 102,
    SBK_QQUICKWINDOW_IDX                                     = 92,
    SBK_QQUICKWINDOW_GRAPHICSSTATEINFO_IDX                   = 96,
    SBK_QSGBASICGEOMETRYNODE_IDX                             = 104,
    SBK_QSGCLIPNODE_IDX                                      = 106,
    SBK_QSGDYNAMICTEXTURE_IDX                                = 108,
    SBK_QSGFLATCOLORMATERIAL_IDX                             = 110,
    SBK_QSGGEOMETRY_ATTRIBUTETYPE_IDX                        = 118,
    SBK_QSGGEOMETRY_DATAPATTERN_IDX                          = 122,
    SBK_QSGGEOMETRY_DRAWINGMODE_IDX                          = 124,
    SBK_QSGGEOMETRY_TYPE_IDX                                 = 130,
    SBK_QSGGEOMETRY_IDX                                      = 112,
    SBK_QSGGEOMETRY_ATTRIBUTE_IDX                            = 114,
    SBK_QSGGEOMETRY_ATTRIBUTESET_IDX                         = 116,
    SBK_QSGGEOMETRY_COLOREDPOINT2D_IDX                       = 120,
    SBK_QSGGEOMETRY_POINT2D_IDX                              = 126,
    SBK_QSGGEOMETRY_TEXTUREDPOINT2D_IDX                      = 128,
    SBK_QSGGEOMETRYNODE_IDX                                  = 132,
    SBK_QSGIMAGENODE_TEXTURECOORDINATESTRANSFORMFLAG_IDX     = 136,
    SBK_QFLAGS_QSGIMAGENODE_TEXTURECOORDINATESTRANSFORMFLAG_IDX = 8,
    SBK_QSGIMAGENODE_IDX                                     = 134,
    SBK_QSGMATERIAL_FLAG_IDX                                 = 140,
    SBK_QFLAGS_QSGMATERIAL_FLAG_IDX                          = 10,
    SBK_QSGMATERIAL_IDX                                      = 138,
    SBK_QSGMATERIALSHADER_FLAG_IDX                           = 144,
    SBK_QFLAGS_QSGMATERIALSHADER_FLAG_IDX                    = 12,
    SBK_QSGMATERIALSHADER_STAGE_IDX                          = 162,
    SBK_QSGMATERIALSHADER_IDX                                = 142,
    SBK_QSGMATERIALSHADER_GRAPHICSPIPELINESTATE_BLENDFACTOR_IDX = 148,
    SBK_QSGMATERIALSHADER_GRAPHICSPIPELINESTATE_BLENDOP_IDX  = 150,
    SBK_QSGMATERIALSHADER_GRAPHICSPIPELINESTATE_COLORMASKCOMPONENT_IDX = 152,
    SBK_QFLAGS_QSGMATERIALSHADER_GRAPHICSPIPELINESTATE_COLORMASKCOMPONENT_IDX = 14,
    SBK_QSGMATERIALSHADER_GRAPHICSPIPELINESTATE_CULLMODE_IDX = 154,
    SBK_QSGMATERIALSHADER_GRAPHICSPIPELINESTATE_POLYGONMODE_IDX = 156,
    SBK_QSGMATERIALSHADER_GRAPHICSPIPELINESTATE_IDX          = 146,
    SBK_QSGMATERIALSHADER_RENDERSTATE_DIRTYSTATE_IDX         = 160,
    SBK_QFLAGS_QSGMATERIALSHADER_RENDERSTATE_DIRTYSTATE_IDX  = 16,
    SBK_QSGMATERIALSHADER_RENDERSTATE_IDX                    = 158,
    SBK_QSGMATERIALTYPE_IDX                                  = 164,
    SBK_QSGNINEPATCHNODE_IDX                                 = 166,
    SBK_QSGNODE_NODETYPE_IDX                                 = 174,
    SBK_QSGNODE_FLAG_IDX                                     = 172,
    SBK_QFLAGS_QSGNODE_FLAG_IDX                              = 20,
    SBK_QSGNODE_DIRTYSTATEBIT_IDX                            = 170,
    SBK_QFLAGS_QSGNODE_DIRTYSTATEBIT_IDX                     = 18,
    SBK_QSGNODE_IDX                                          = 168,
    SBK_QSGNODEVISITOR_IDX                                   = 176,
    SBK_QSGOPACITYNODE_IDX                                   = 178,
    SBK_QSGOPAQUETEXTUREMATERIAL_IDX                         = 180,
    SBK_QSGRECTANGLENODE_IDX                                 = 182,
    SBK_QSGRENDERNODE_STATEFLAG_IDX                          = 190,
    SBK_QFLAGS_QSGRENDERNODE_STATEFLAG_IDX                   = 24,
    SBK_QSGRENDERNODE_RENDERINGFLAG_IDX                      = 188,
    SBK_QFLAGS_QSGRENDERNODE_RENDERINGFLAG_IDX               = 22,
    SBK_QSGRENDERNODE_IDX                                    = 184,
    SBK_QSGRENDERNODE_RENDERSTATE_IDX                        = 186,
    SBK_QSGRENDERERINTERFACE_GRAPHICSAPI_IDX                 = 194,
    SBK_QSGRENDERERINTERFACE_RESOURCE_IDX                    = 198,
    SBK_QSGRENDERERINTERFACE_SHADERTYPE_IDX                  = 204,
    SBK_QSGRENDERERINTERFACE_SHADERCOMPILATIONTYPE_IDX       = 200,
    SBK_QFLAGS_QSGRENDERERINTERFACE_SHADERCOMPILATIONTYPE_IDX = 26,
    SBK_QSGRENDERERINTERFACE_SHADERSOURCETYPE_IDX            = 202,
    SBK_QFLAGS_QSGRENDERERINTERFACE_SHADERSOURCETYPE_IDX     = 28,
    SBK_QSGRENDERERINTERFACE_RENDERMODE_IDX                  = 196,
    SBK_QSGRENDERERINTERFACE_IDX                             = 192,
    SBK_QSGROOTNODE_IDX                                      = 206,
    SBK_QSGSIMPLERECTNODE_IDX                                = 208,
    SBK_QSGSIMPLETEXTURENODE_TEXTURECOORDINATESTRANSFORMFLAG_IDX = 212,
    SBK_QFLAGS_QSGSIMPLETEXTURENODE_TEXTURECOORDINATESTRANSFORMFLAG_IDX = 30,
    SBK_QSGSIMPLETEXTURENODE_IDX                             = 210,
    SBK_QSGTEXTNODE_TEXTSTYLE_IDX                            = 218,
    SBK_QSGTEXTNODE_RENDERTYPE_IDX                           = 216,
    SBK_QSGTEXTNODE_IDX                                      = 214,
    SBK_QSGTEXTURE_WRAPMODE_IDX                              = 226,
    SBK_QSGTEXTURE_FILTERING_IDX                             = 224,
    SBK_QSGTEXTURE_ANISOTROPYLEVEL_IDX                       = 222,
    SBK_QSGTEXTURE_IDX                                       = 220,
    SBK_QSGTEXTUREMATERIAL_IDX                               = 228,
    SBK_QSGTEXTUREPROVIDER_IDX                               = 230,
    SBK_QSGTRANSFORMNODE_IDX                                 = 232,
    SBK_QSGVERTEXCOLORMATERIAL_IDX                           = 234,
    SBK_QSHAREDPOINTER_QQUICKITEMGRABRESULT_IDX              = 238, // QSharedPointer<QQuickItemGrabResult>
    SBK_QSHAREDPOINTER_CONSTQQUICKITEMGRABRESULT_IDX         = 238, // (const)
    SBK_QTQUICK_IDX_COUNT                                    = 240,
};

// Type indices
enum : int {
    SBK_QQuickAsyncImageProvider_IDX                         = 16,
    SBK_QQuickFramebufferObject_IDX                          = 17,
    SBK_QQuickFramebufferObject_Renderer_IDX                 = 18,
    SBK_QQuickGraphicsConfiguration_IDX                      = 19,
    SBK_QQuickGraphicsDevice_IDX                             = 20,
    SBK_QQuickImageProvider_IDX                              = 21,
    SBK_QQuickImageResponse_IDX                              = 22,
    SBK_QQuickItem_Flag_IDX                                  = 24,
    SBK_QFlags_QQuickItem_Flag_IDX                           = 0,
    SBK_QQuickItem_ItemChange_IDX                            = 25,
    SBK_QQuickItem_TransformOrigin_IDX                       = 26,
    SBK_QQuickItem_IDX                                       = 23,
    SBK_QQuickItem_UpdatePaintNodeData_IDX                   = 27,
    SBK_QQuickItemGrabResult_IDX                             = 28,
    SBK_QtQuickQQuickOpenGLUtils_IDX                         = 29,
    SBK_QQuickPaintedItem_RenderTarget_IDX                   = 32,
    SBK_QQuickPaintedItem_PerformanceHint_IDX                = 31,
    SBK_QFlags_QQuickPaintedItem_PerformanceHint_IDX         = 1,
    SBK_QQuickPaintedItem_IDX                                = 30,
    SBK_QQuickRenderControl_IDX                              = 33,
    SBK_QQuickRenderTarget_Flag_IDX                          = 35,
    SBK_QFlags_QQuickRenderTarget_Flag_IDX                   = 2,
    SBK_QQuickRenderTarget_IDX                               = 34,
    SBK_QQuickRhiItem_TextureFormat_IDX                      = 37,
    SBK_QQuickRhiItem_IDX                                    = 36,
    SBK_QQuickRhiItemRenderer_IDX                            = 38,
    SBK_QQuickTextDocument_Status_IDX                        = 40,
    SBK_QQuickTextDocument_IDX                               = 39,
    SBK_QQuickTextureFactory_IDX                             = 41,
    SBK_QQuickTransform_IDX                                  = 42,
    SBK_QQuickView_ResizeMode_IDX                            = 44,
    SBK_QQuickView_Status_IDX                                = 45,
    SBK_QQuickView_IDX                                       = 43,
    SBK_QQuickWindow_CreateTextureOption_IDX                 = 47,
    SBK_QFlags_QQuickWindow_CreateTextureOption_IDX          = 3,
    SBK_QQuickWindow_RenderStage_IDX                         = 49,
    SBK_QQuickWindow_SceneGraphError_IDX                     = 50,
    SBK_QQuickWindow_TextRenderType_IDX                      = 51,
    SBK_QQuickWindow_IDX                                     = 46,
    SBK_QQuickWindow_GraphicsStateInfo_IDX                   = 48,
    SBK_QSGBasicGeometryNode_IDX                             = 52,
    SBK_QSGClipNode_IDX                                      = 53,
    SBK_QSGDynamicTexture_IDX                                = 54,
    SBK_QSGFlatColorMaterial_IDX                             = 55,
    SBK_QSGGeometry_AttributeType_IDX                        = 59,
    SBK_QSGGeometry_DataPattern_IDX                          = 61,
    SBK_QSGGeometry_DrawingMode_IDX                          = 62,
    SBK_QSGGeometry_Type_IDX                                 = 65,
    SBK_QSGGeometry_IDX                                      = 56,
    SBK_QSGGeometry_Attribute_IDX                            = 57,
    SBK_QSGGeometry_AttributeSet_IDX                         = 58,
    SBK_QSGGeometry_ColoredPoint2D_IDX                       = 60,
    SBK_QSGGeometry_Point2D_IDX                              = 63,
    SBK_QSGGeometry_TexturedPoint2D_IDX                      = 64,
    SBK_QSGGeometryNode_IDX                                  = 66,
    SBK_QSGImageNode_TextureCoordinatesTransformFlag_IDX     = 68,
    SBK_QFlags_QSGImageNode_TextureCoordinatesTransformFlag_IDX = 4,
    SBK_QSGImageNode_IDX                                     = 67,
    SBK_QSGMaterial_Flag_IDX                                 = 70,
    SBK_QFlags_QSGMaterial_Flag_IDX                          = 5,
    SBK_QSGMaterial_IDX                                      = 69,
    SBK_QSGMaterialShader_Flag_IDX                           = 72,
    SBK_QFlags_QSGMaterialShader_Flag_IDX                    = 6,
    SBK_QSGMaterialShader_Stage_IDX                          = 81,
    SBK_QSGMaterialShader_IDX                                = 71,
    SBK_QSGMaterialShader_GraphicsPipelineState_BlendFactor_IDX = 74,
    SBK_QSGMaterialShader_GraphicsPipelineState_BlendOp_IDX  = 75,
    SBK_QSGMaterialShader_GraphicsPipelineState_ColorMaskComponent_IDX = 76,
    SBK_QFlags_QSGMaterialShader_GraphicsPipelineState_ColorMaskComponent_IDX = 7,
    SBK_QSGMaterialShader_GraphicsPipelineState_CullMode_IDX = 77,
    SBK_QSGMaterialShader_GraphicsPipelineState_PolygonMode_IDX = 78,
    SBK_QSGMaterialShader_GraphicsPipelineState_IDX          = 73,
    SBK_QSGMaterialShader_RenderState_DirtyState_IDX         = 80,
    SBK_QFlags_QSGMaterialShader_RenderState_DirtyState_IDX  = 8,
    SBK_QSGMaterialShader_RenderState_IDX                    = 79,
    SBK_QSGMaterialType_IDX                                  = 82,
    SBK_QSGNinePatchNode_IDX                                 = 83,
    SBK_QSGNode_NodeType_IDX                                 = 87,
    SBK_QSGNode_Flag_IDX                                     = 86,
    SBK_QFlags_QSGNode_Flag_IDX                              = 10,
    SBK_QSGNode_DirtyStateBit_IDX                            = 85,
    SBK_QFlags_QSGNode_DirtyStateBit_IDX                     = 9,
    SBK_QSGNode_IDX                                          = 84,
    SBK_QSGNodeVisitor_IDX                                   = 88,
    SBK_QSGOpacityNode_IDX                                   = 89,
    SBK_QSGOpaqueTextureMaterial_IDX                         = 90,
    SBK_QSGRectangleNode_IDX                                 = 91,
    SBK_QSGRenderNode_StateFlag_IDX                          = 95,
    SBK_QFlags_QSGRenderNode_StateFlag_IDX                   = 12,
    SBK_QSGRenderNode_RenderingFlag_IDX                      = 94,
    SBK_QFlags_QSGRenderNode_RenderingFlag_IDX               = 11,
    SBK_QSGRenderNode_IDX                                    = 92,
    SBK_QSGRenderNode_RenderState_IDX                        = 93,
    SBK_QSGRendererInterface_GraphicsApi_IDX                 = 97,
    SBK_QSGRendererInterface_Resource_IDX                    = 99,
    SBK_QSGRendererInterface_ShaderType_IDX                  = 102,
    SBK_QSGRendererInterface_ShaderCompilationType_IDX       = 100,
    SBK_QFlags_QSGRendererInterface_ShaderCompilationType_IDX = 13,
    SBK_QSGRendererInterface_ShaderSourceType_IDX            = 101,
    SBK_QFlags_QSGRendererInterface_ShaderSourceType_IDX     = 14,
    SBK_QSGRendererInterface_RenderMode_IDX                  = 98,
    SBK_QSGRendererInterface_IDX                             = 96,
    SBK_QSGRootNode_IDX                                      = 103,
    SBK_QSGSimpleRectNode_IDX                                = 104,
    SBK_QSGSimpleTextureNode_TextureCoordinatesTransformFlag_IDX = 106,
    SBK_QFlags_QSGSimpleTextureNode_TextureCoordinatesTransformFlag_IDX = 15,
    SBK_QSGSimpleTextureNode_IDX                             = 105,
    SBK_QSGTextNode_TextStyle_IDX                            = 109,
    SBK_QSGTextNode_RenderType_IDX                           = 108,
    SBK_QSGTextNode_IDX                                      = 107,
    SBK_QSGTexture_WrapMode_IDX                              = 113,
    SBK_QSGTexture_Filtering_IDX                             = 112,
    SBK_QSGTexture_AnisotropyLevel_IDX                       = 111,
    SBK_QSGTexture_IDX                                       = 110,
    SBK_QSGTextureMaterial_IDX                               = 114,
    SBK_QSGTextureProvider_IDX                               = 115,
    SBK_QSGTransformNode_IDX                                 = 116,
    SBK_QSGVertexColorMaterial_IDX                           = 117,
    SBK_QSharedPointer_QQuickItemGrabResult_IDX              = 119, // QSharedPointer<QQuickItemGrabResult>
    SBK_QSharedPointer_constQQuickItemGrabResult_IDX         = 119, // (const)
    SBK_QtQuick_IDX_COUNT                                    = 120,
};

// This variable stores all Python types exported by this module.
extern Shiboken::Module::TypeInitStruct *SbkPySide6_QtQuickTypeStructs;

// This variable stores all Python types exported by this module in a backwards compatible way with identical indexing.
[[deprecated]] extern PyTypeObject **SbkPySide6_QtQuickTypes;

// This variable stores the Python module object exported by this module.
extern PyObject *SbkPySide6_QtQuickModuleObject;

// This variable stores all type converters exported by this module.
extern SbkConverter **SbkPySide6_QtQuickTypeConverters;

// Converter indices
enum [[deprecated]] : int {
    SBK_QTQUICK_QLIST_INT_IDX                                = 0, // QList<int>
    SBK_QTQUICK_QLIST_QSGGEOMETRY_POINT2D_IDX                = 2, // QList<QSGGeometry::Point2D>
    SBK_QTQUICK_QLIST_QBYTEARRAY_IDX                         = 4, // QList<QByteArray>
    SBK_QTQUICK_QLIST_QQUICKITEMPTR_IDX                      = 6, // QList<QQuickItem*>
    SBK_QTQUICK_QLIST_QQMLERROR_IDX                          = 8, // QList<QQmlError>
    SBK_QTQUICK_QMAP_QSTRING_QVARIANT_IDX                    = 10, // QMap<QString,QVariant>
    SBK_QTQUICK_QLIST_QVARIANT_IDX                           = 12, // QList<QVariant>
    SBK_QTQUICK_QLIST_QSTRING_IDX                            = 14, // QList<QString>
    SBK_QTQUICK_CONVERTERS_IDX_COUNT                         = 16,
};

// Converter indices
enum : int {
    SBK_QtQuick_QList_int_IDX                                = 0, // QList<int>
    SBK_QtQuick_QList_QSGGeometry_Point2D_IDX                = 1, // QList<QSGGeometry::Point2D>
    SBK_QtQuick_QList_QByteArray_IDX                         = 2, // QList<QByteArray>
    SBK_QtQuick_QList_QQuickItemPTR_IDX                      = 3, // QList<QQuickItem*>
    SBK_QtQuick_QList_QQmlError_IDX                          = 4, // QList<QQmlError>
    SBK_QtQuick_QMap_QString_QVariant_IDX                    = 5, // QMap<QString,QVariant>
    SBK_QtQuick_QList_QVariant_IDX                           = 6, // QList<QVariant>
    SBK_QtQuick_QList_QString_IDX                            = 7, // QList<QString>
    SBK_QtQuick_CONVERTERS_IDX_COUNT                         = 8,
};
// Macros for type check

QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
namespace Shiboken
{

// PyType functions, to get the PyObjectType for a type T
template<> inline PyTypeObject *SbkType< ::QQuickAsyncImageProvider >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QQuickAsyncImageProvider_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQuickFramebufferObject >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QQuickFramebufferObject_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQuickFramebufferObject::Renderer >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QQuickFramebufferObject_Renderer_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQuickGraphicsConfiguration >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QQuickGraphicsConfiguration_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQuickGraphicsDevice >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QQuickGraphicsDevice_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQuickImageProvider >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QQuickImageProvider_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQuickImageResponse >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QQuickImageResponse_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQuickItem::Flag >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QQuickItem_Flag_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QQuickItem::Flag> >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QFlags_QQuickItem_Flag_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQuickItem::ItemChange >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QQuickItem_ItemChange_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQuickItem::TransformOrigin >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QQuickItem_TransformOrigin_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQuickItem >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QQuickItem_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQuickItem::UpdatePaintNodeData >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QQuickItem_UpdatePaintNodeData_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQuickItemGrabResult >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QQuickItemGrabResult_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQuickPaintedItem::RenderTarget >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QQuickPaintedItem_RenderTarget_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQuickPaintedItem::PerformanceHint >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QQuickPaintedItem_PerformanceHint_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QQuickPaintedItem::PerformanceHint> >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QFlags_QQuickPaintedItem_PerformanceHint_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQuickPaintedItem >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QQuickPaintedItem_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQuickRenderControl >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QQuickRenderControl_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQuickRenderTarget::Flag >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QQuickRenderTarget_Flag_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QQuickRenderTarget::Flag> >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QFlags_QQuickRenderTarget_Flag_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQuickRenderTarget >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QQuickRenderTarget_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQuickRhiItem::TextureFormat >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QQuickRhiItem_TextureFormat_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQuickRhiItem >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QQuickRhiItem_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQuickRhiItemRenderer >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QQuickRhiItemRenderer_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQuickTextDocument::Status >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QQuickTextDocument_Status_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQuickTextDocument >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QQuickTextDocument_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQuickTextureFactory >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QQuickTextureFactory_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQuickTransform >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QQuickTransform_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQuickView::ResizeMode >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QQuickView_ResizeMode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQuickView::Status >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QQuickView_Status_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQuickView >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QQuickView_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQuickWindow::CreateTextureOption >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QQuickWindow_CreateTextureOption_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QQuickWindow::CreateTextureOption> >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QFlags_QQuickWindow_CreateTextureOption_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQuickWindow::RenderStage >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QQuickWindow_RenderStage_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQuickWindow::SceneGraphError >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QQuickWindow_SceneGraphError_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQuickWindow::TextRenderType >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QQuickWindow_TextRenderType_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQuickWindow >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QQuickWindow_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQuickWindow::GraphicsStateInfo >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QQuickWindow_GraphicsStateInfo_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGBasicGeometryNode >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGBasicGeometryNode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGClipNode >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGClipNode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGDynamicTexture >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGDynamicTexture_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGFlatColorMaterial >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGFlatColorMaterial_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGGeometry::AttributeType >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGGeometry_AttributeType_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGGeometry::DataPattern >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGGeometry_DataPattern_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGGeometry::DrawingMode >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGGeometry_DrawingMode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGGeometry::Type >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGGeometry_Type_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGGeometry >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGGeometry_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGGeometry::Attribute >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGGeometry_Attribute_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGGeometry::AttributeSet >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGGeometry_AttributeSet_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGGeometry::ColoredPoint2D >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGGeometry_ColoredPoint2D_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGGeometry::Point2D >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGGeometry_Point2D_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGGeometry::TexturedPoint2D >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGGeometry_TexturedPoint2D_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGGeometryNode >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGGeometryNode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGImageNode::TextureCoordinatesTransformFlag >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGImageNode_TextureCoordinatesTransformFlag_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QSGImageNode::TextureCoordinatesTransformFlag> >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QFlags_QSGImageNode_TextureCoordinatesTransformFlag_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGImageNode >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGImageNode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGMaterial::Flag >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGMaterial_Flag_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QSGMaterial::Flag> >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QFlags_QSGMaterial_Flag_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGMaterial >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGMaterial_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGMaterialShader::Flag >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGMaterialShader_Flag_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QSGMaterialShader::Flag> >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QFlags_QSGMaterialShader_Flag_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGMaterialShader::Stage >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGMaterialShader_Stage_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGMaterialShader >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGMaterialShader_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGMaterialShader::GraphicsPipelineState::BlendFactor >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGMaterialShader_GraphicsPipelineState_BlendFactor_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGMaterialShader::GraphicsPipelineState::BlendOp >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGMaterialShader_GraphicsPipelineState_BlendOp_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGMaterialShader::GraphicsPipelineState::ColorMaskComponent >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGMaterialShader_GraphicsPipelineState_ColorMaskComponent_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QSGMaterialShader::GraphicsPipelineState::ColorMaskComponent> >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QFlags_QSGMaterialShader_GraphicsPipelineState_ColorMaskComponent_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGMaterialShader::GraphicsPipelineState::CullMode >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGMaterialShader_GraphicsPipelineState_CullMode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGMaterialShader::GraphicsPipelineState::PolygonMode >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGMaterialShader_GraphicsPipelineState_PolygonMode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGMaterialShader::GraphicsPipelineState >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGMaterialShader_GraphicsPipelineState_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGMaterialShader::RenderState::DirtyState >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGMaterialShader_RenderState_DirtyState_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QSGMaterialShader::RenderState::DirtyState> >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QFlags_QSGMaterialShader_RenderState_DirtyState_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGMaterialShader::RenderState >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGMaterialShader_RenderState_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGMaterialType >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGMaterialType_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGNinePatchNode >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGNinePatchNode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGNode::NodeType >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGNode_NodeType_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGNode::Flag >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGNode_Flag_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QSGNode::Flag> >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QFlags_QSGNode_Flag_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGNode::DirtyStateBit >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGNode_DirtyStateBit_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QSGNode::DirtyStateBit> >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QFlags_QSGNode_DirtyStateBit_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGNode >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGNode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGNodeVisitor >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGNodeVisitor_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGOpacityNode >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGOpacityNode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGOpaqueTextureMaterial >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGOpaqueTextureMaterial_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGRectangleNode >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGRectangleNode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGRenderNode::StateFlag >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGRenderNode_StateFlag_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QSGRenderNode::StateFlag> >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QFlags_QSGRenderNode_StateFlag_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGRenderNode::RenderingFlag >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGRenderNode_RenderingFlag_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QSGRenderNode::RenderingFlag> >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QFlags_QSGRenderNode_RenderingFlag_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGRenderNode >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGRenderNode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGRenderNode::RenderState >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGRenderNode_RenderState_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGRendererInterface::GraphicsApi >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGRendererInterface_GraphicsApi_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGRendererInterface::Resource >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGRendererInterface_Resource_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGRendererInterface::ShaderType >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGRendererInterface_ShaderType_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGRendererInterface::ShaderCompilationType >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGRendererInterface_ShaderCompilationType_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QSGRendererInterface::ShaderCompilationType> >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QFlags_QSGRendererInterface_ShaderCompilationType_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGRendererInterface::ShaderSourceType >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGRendererInterface_ShaderSourceType_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QSGRendererInterface::ShaderSourceType> >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QFlags_QSGRendererInterface_ShaderSourceType_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGRendererInterface::RenderMode >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGRendererInterface_RenderMode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGRendererInterface >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGRendererInterface_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGRootNode >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGRootNode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGSimpleRectNode >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGSimpleRectNode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGSimpleTextureNode::TextureCoordinatesTransformFlag >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGSimpleTextureNode_TextureCoordinatesTransformFlag_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QSGSimpleTextureNode::TextureCoordinatesTransformFlag> >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QFlags_QSGSimpleTextureNode_TextureCoordinatesTransformFlag_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGSimpleTextureNode >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGSimpleTextureNode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGTextNode::TextStyle >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGTextNode_TextStyle_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGTextNode::RenderType >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGTextNode_RenderType_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGTextNode >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGTextNode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGTexture::WrapMode >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGTexture_WrapMode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGTexture::Filtering >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGTexture_Filtering_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGTexture::AnisotropyLevel >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGTexture_AnisotropyLevel_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGTexture >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGTexture_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGTextureMaterial >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGTextureMaterial_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGTextureProvider >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGTextureProvider_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGTransformNode >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGTransformNode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSGVertexColorMaterial >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSGVertexColorMaterial_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSharedPointer<QQuickItemGrabResult> >() { return Shiboken::Module::get(SbkPySide6_QtQuickTypeStructs[SBK_QSharedPointer_QQuickItemGrabResult_IDX]); }

} // namespace Shiboken

QT_WARNING_POP
#endif // SBK_QTQUICK_PYTHON_H

