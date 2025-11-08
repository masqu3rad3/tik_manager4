// Copyright (C) 2018 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

/*********************************************************************
 * INJECT CODE
 ********************************************************************/

// @snippet gui-declarations
QT_BEGIN_NAMESPACE
void qt_set_sequence_auto_mnemonic(bool);
QT_END_NAMESPACE
// @snippet gui-declarations

// @snippet qaccessible-pysidefactory
// Helper for QAccessible::installFactory() that forwards the calls to
// Python callables.
class PySideAccessibleFactory
{
    PySideAccessibleFactory() = default;
public:
    ~PySideAccessibleFactory();

    static PySideAccessibleFactory *instance() { return m_instance; }
    static PySideAccessibleFactory *ensureInstance();

    static void installFactory(PyObject *f);
    static void cleanup();

    static QAccessibleInterface *factory(const QString &key, QObject *o);

private:
    QAccessibleInterface *callFactories(const QString &key, QObject *o);

    static PySideAccessibleFactory *m_instance;

    QList<PyObject *> m_factoryFunctions;
    QList<PyObject *> m_objects;
};

PySideAccessibleFactory *PySideAccessibleFactory::m_instance = nullptr;

PySideAccessibleFactory::~PySideAccessibleFactory()
{
    QAccessible::removeFactory(PySideAccessibleFactory::factory);
    if (!m_factoryFunctions.isEmpty()) {
        Shiboken::GilState state;
        for (auto *f : m_factoryFunctions)
            Py_DECREF(f);
        for (auto *o : m_objects)
            Py_DECREF(o);
    }
}

PySideAccessibleFactory *PySideAccessibleFactory::ensureInstance()
{
    if (m_instance == nullptr) {
        m_instance = new PySideAccessibleFactory;
        QAccessible::installFactory(PySideAccessibleFactory::factory);
        qAddPostRoutine(PySideAccessibleFactory::cleanup);
    }
    return m_instance;
}

void PySideAccessibleFactory::installFactory(PyObject *f)
{
    if (m_instance != nullptr) {
        Py_INCREF(f);
        m_instance->m_factoryFunctions.append(f);
    }
}

void PySideAccessibleFactory::cleanup()
{
    delete m_instance;
    m_instance = nullptr;
}

QAccessibleInterface *PySideAccessibleFactory::factory(const QString &key, QObject *o)
{
    return m_instance ? m_instance->callFactories(key, o) : nullptr;
}

QAccessibleInterface *PySideAccessibleFactory::callFactories(const QString &key, QObject *o)
{
    Shiboken::GilState state;
    Shiboken::AutoDecRef arglist(PyTuple_New(2));
    PyTuple_SetItem(arglist, 0, %CONVERTTOPYTHON[QString](key));
    PyTuple_SetItem(arglist, 1, %CONVERTTOPYTHON[QObject *](o));

    for (auto *f : m_factoryFunctions) {
        if (PyObject *pyResult = PyObject_CallObject(f, arglist)) {
            if (pyResult != Py_None) {
                m_objects.append(pyResult);
                QAccessibleInterface* result = %CONVERTTOCPP[QAccessibleInterface *](pyResult);
                return result;
            }
            Py_DECREF(pyResult);
        }
    }

    return nullptr;
}
// @snippet qaccessible-pysidefactory

// @snippet qaccessible-installfactory
PySideAccessibleFactory::ensureInstance()->installFactory(%1);
// @snippet qaccessible-installfactory

// @snippet qaction-menu
// %CPPSELF->menu(); // pretend it was called.
QObject *object = %CPPSELF->menu<QObject *>();
%PYARG_0 = %CONVERTTOPYTHON[QObject*](object);
// @snippet qaction-menu

// @snippet qopenglfunctions-glgetv-return-size
// Return the number of return values of the glGetBoolean/Double/Integerv functions
// cf https://registry.khronos.org/OpenGL-Refpages/gl4/html/glGet.xhtml
static int glGetVReturnSize(GLenum pname)
{
    switch (pname) {
    case GL_ALIASED_LINE_WIDTH_RANGE:
    case GL_DEPTH_RANGE:
    case GL_MAX_VIEWPORT_DIMS:
#if !QT_CONFIG(opengles2)
    case GL_POINT_SIZE_RANGE:
    case GL_SMOOTH_LINE_WIDTH_RANGE:
    case GL_VIEWPORT_BOUNDS_RANGE:
#endif
        return 2;
    case GL_BLEND_COLOR:
    case GL_COLOR_CLEAR_VALUE:
    case GL_COLOR_WRITEMASK:
    case GL_SCISSOR_BOX:
    case GL_VIEWPORT:
        return 4;
    case GL_COMPRESSED_TEXTURE_FORMATS:
        return GL_NUM_COMPRESSED_TEXTURE_FORMATS;
    default:
        break;
    }
    return 1;
}
// @snippet qopenglfunctions-glgetv-return-size

// @snippet qopenglextrafunctions-glgeti-v-return-size
// Return the number of return values of the indexed
// glGetBoolean/Double/Integeri_v functions
// cf https://registry.khronos.org/OpenGL-Refpages/gl4/html/glGet.xhtml
static int glGetI_VReturnSize(GLenum pname)
{
    return pname == GL_VIEWPORT ? 4 : 1;
}
// @snippet qopenglextrafunctions-glgeti-v-return-size

// @snippet qopenglfunctions-glgetbooleanv
const int size = glGetVReturnSize(%1);
QVarLengthArray<GLboolean> result(size, GL_FALSE);
%CPPSELF.%FUNCTION_NAME(%ARGUMENT_NAMES, result.data());
if (size == 1) {
    %PYARG_0 = %CONVERTTOPYTHON[bool](result[0]);
} else {
    %PYARG_0 = Shiboken::Numpy::createByteArray1(size, result.constData());
}
// @snippet qopenglfunctions-glgetbooleanv

// @snippet qopenglfunctions-glgetdoublev
const int size = glGetVReturnSize(%1);
QVarLengthArray<GLdouble> result(size, 0);
%CPPSELF.%FUNCTION_NAME(%ARGUMENT_NAMES, result.data());
if (size == 1) {
    %PYARG_0 = %CONVERTTOPYTHON[double](result[0]);
} else {
    %PYARG_0 = Shiboken::Numpy::createDoubleArray1(size, result.constData());
}
// @snippet qopenglfunctions-glgetdoublev

// @snippet qopenglfunctions-glgetfloatv
const int size = glGetVReturnSize(%1);
QVarLengthArray<GLfloat> result(size, 0);
%CPPSELF.%FUNCTION_NAME(%ARGUMENT_NAMES, result.data());
if (size == 1) {
    %PYARG_0 = %CONVERTTOPYTHON[float](result[0]);
} else {
    %PYARG_0 = Shiboken::Numpy::createFloatArray1(size, result.constData());
}
// @snippet qopenglfunctions-glgetfloatv

// @snippet qopenglfunctions-glgetintegerv
const int size = glGetVReturnSize(%1);
QVarLengthArray<GLint> result(size, 0);
%CPPSELF.%FUNCTION_NAME(%ARGUMENT_NAMES, result.data());
if (size == 1) {
    %PYARG_0 = %CONVERTTOPYTHON[int](result[0]);
} else {
    %PYARG_0 = Shiboken::Numpy::createIntArray1(size, result.constData());
}
// @snippet qopenglfunctions-glgetintegerv

// @snippet qopenglextrafunctions-glgetbooleani-v
const int size = glGetI_VReturnSize(%1);
QVarLengthArray<GLboolean> result(size, GL_FALSE);
%CPPSELF.%FUNCTION_NAME(%ARGUMENT_NAMES, result.data());
if (size == 1) {
    %PYARG_0 = %CONVERTTOPYTHON[bool](result[0]);
} else {
    %PYARG_0 = Shiboken::Numpy::createByteArray1(size, result.constData());
}
// @snippet qopenglextrafunctions-glgetbooleani-v

// @snippet qopenglextrafunctions-glgetdoublei-v
const int size = glGetI_VReturnSize(%1);
QVarLengthArray<GLdouble> result(size, 0);
%CPPSELF.%FUNCTION_NAME(%ARGUMENT_NAMES, result.data());
if (size == 1) {
    %PYARG_0 = %CONVERTTOPYTHON[double](result[0]);
} else {
    %PYARG_0 = Shiboken::Numpy::createDoubleArray1(size, result.constData());
}
// @snippet qopenglextrafunctions-glgetdoublei-v

// @snippet qopenglextrafunctions-glgetfloati-v
const int size = glGetI_VReturnSize(%1);
QVarLengthArray<GLfloat> result(size, 0);
%CPPSELF.%FUNCTION_NAME(%ARGUMENT_NAMES, result.data());
if (size == 1) {
    %PYARG_0 = %CONVERTTOPYTHON[float](result[0]);
} else {
    %PYARG_0 = Shiboken::Numpy::createFloatArray1(size, result.constData());
}
// @snippet qopenglextrafunctions-glgetfloati-v

// @snippet qopenglextrafunctions-glgetintegeri-v
const int size = glGetI_VReturnSize(%1);
QVarLengthArray<GLint> result(size, 0);
%CPPSELF.%FUNCTION_NAME(%ARGUMENT_NAMES, result.data());
if (size == 1) {
    %PYARG_0 = %CONVERTTOPYTHON[int](result[0]);
} else {
    %PYARG_0 = Shiboken::Numpy::createIntArray1(size, result.constData());
}
// @snippet qopenglextrafunctions-glgetintegeri-v

// @snippet glgetshadersource
GLsizei bufSize = 4096;
GLsizei length = bufSize - 1;
QByteArray buffer;
for (; length == bufSize - 1; bufSize += 4096) {
    buffer.resize(qsizetype(bufSize));
    %CPPSELF->%FUNCTION_NAME(%1, bufSize, &length, buffer.data());
    if (%CPPSELF->glGetError() != GL_NO_ERROR) {
        buffer.clear();
        break;
    }
}
auto *data = buffer.constData();
%PYARG_0 = %CONVERTTOPYTHON[char *](data);
// @snippet glgetshadersource

// @snippet glshadersource
const QByteArray buffer = %2.toUtf8();
const char *sources[] = {buffer.constData()};
%CPPSELF->%FUNCTION_NAME(%1, 1, sources, nullptr);
// @snippet glshadersource

// @snippet glgetstring-return
%PYARG_0 = %CONVERTTOPYTHON[const char *](%0);
// @snippet glgetstring-return

// @snippet qtransform-quadtoquad
QTransform _result;
if (QTransform::quadToQuad(%1, %2, _result)) {
    %PYARG_0 = %CONVERTTOPYTHON[QTransform](_result);
} else {
    Py_INCREF(Py_None);
    %PYARG_0 = Py_None;
}
// @snippet qtransform-quadtoquad

// @snippet qtransform-quadtosquare
QTransform _result;
if (QTransform::quadToSquare(%1, _result)) {
    %PYARG_0 = %CONVERTTOPYTHON[QTransform](_result);
} else {
    Py_INCREF(Py_None);
    %PYARG_0 = Py_None;
}
// @snippet qtransform-quadtosquare

// @snippet qtransform-squaretoquad
QTransform _result;
if (QTransform::squareToQuad(%1, _result)) {
    %PYARG_0 = %CONVERTTOPYTHON[QTransform](_result);
} else {
    Py_INCREF(Py_None);
    %PYARG_0 = Py_None;
}
// @snippet qtransform-squaretoquad

// @snippet qbitmap-fromdata
auto *buffer = reinterpret_cast<uchar *>(Shiboken::Buffer::getPointer(%PYARG_2));
QBitmap %0 = QBitmap::fromData(%1, buffer, %3);
%PYARG_0 = %CONVERTTOPYTHON[QBitmap](%0);
// @snippet qbitmap-fromdata

// @snippet qtextline-cursortox
%RETURN_TYPE %0 = %CPPSELF->::%TYPE::%FUNCTION_NAME(&%1, %2);
%PYARG_0 = PyTuple_New(2);
PyTuple_SetItem(%PYARG_0, 0, %CONVERTTOPYTHON[%RETURN_TYPE](%0));
PyTuple_SetItem(%PYARG_0, 1, %CONVERTTOPYTHON[%ARG1_TYPE](%1));
// @snippet qtextline-cursortox

// @snippet qkeysequence-getitem
const Py_ssize_t size = %CPPSELF.count();
if (_i < 0 || _i >= size) {
    Shiboken::Errors::setIndexOutOfBounds(_i, 0, size);
    return nullptr;
}
QKeyCombination item = (*%CPPSELF)[_i];
return %CONVERTTOPYTHON[QKeyCombination](item);
// @snippet qkeysequence-getitem

// @snippet qkeysequence-repr
auto ObTuple_Type = reinterpret_cast<PyObject *>(&PyTuple_Type);
auto ObSelf_Type = reinterpret_cast<PyObject *>(Py_TYPE(%PYSELF));
Shiboken::AutoDecRef surrogate(PyObject_CallFunctionObjArgs(ObTuple_Type, %PYSELF, nullptr));
Shiboken::AutoDecRef argstr(PyObject_Repr(surrogate));
Shiboken::AutoDecRef name(PyObject_GetAttrString(ObSelf_Type, "__name__"));
return PyUnicode_Concat(name, argstr);
// @snippet qkeysequence-repr

// @snippet qpicture-data
%PYARG_0 = Shiboken::Buffer::newObject(%CPPSELF.data(), %CPPSELF.size());
// @snippet qpicture-data

// @snippet qtextblock-setuserdata
const QTextDocument *doc = %CPPSELF.document();
if (doc) {
    Shiboken::AutoDecRef pyDocument(%CONVERTTOPYTHON[QTextDocument *](doc));
    Shiboken::Object::setParent(pyDocument, %PYARG_1);
}
// @snippet qtextblock-setuserdata

// @snippet qtextblock-userdata
const QTextDocument *doc = %CPPSELF.document();
if (doc) {
    Shiboken::AutoDecRef pyDocument(%CONVERTTOPYTHON[QTextDocument *](doc));
    Shiboken::Object::setParent(pyDocument, %PYARG_0);
}
// @snippet qtextblock-userdata

// @snippet qpolygon-reduce
const Py_ssize_t count = %CPPSELF.size();
PyObject *points = PyList_New(count);
for (Py_ssize_t i = 0; i < count; ++i){
    int x, y;
    %CPPSELF.point(i, &x, &y);
    QPoint pt{x, y};
    PyList_SetItem(points, i, %CONVERTTOPYTHON[QPoint](pt));
}
// @snippet qpolygon-reduce

// @snippet qpolygon-operatorlowerlower
// %FUNCTION_NAME()
*%CPPSELF << %1;
%PYARG_0 = %CONVERTTOPYTHON[QPolygon *](%CPPSELF);
// @snippet qpolygon-operatorlowerlower

// @snippet qpixmap
%0 = new %TYPE(QPixmap::fromImage(%1));
// @snippet qpixmap

// @snippet qpixmap-load-xpm
Shiboken::AutoDecRef strList(PySequence_Fast(%PYARG_1, "Invalid sequence."));
Py_ssize_t lineCount = PySequence_Size(strList.object());
for (Py_ssize_t line = 0; line < lineCount; ++line) {
    Shiboken::AutoDecRef _obj(PySequence_GetItem(strList.object(), line));
    if (!Shiboken::String::check(_obj)) {
        PyErr_SetString(PyExc_TypeError, "The argument must be a sequence of strings.");
        break;
    }
}
// PySIDE-1735: Enums are now implemented in Python, so we need to avoid asserts.
if (PyErr_Occurred())
    break;

Shiboken::ArrayPointer<const char*> xpm(lineCount);
for (Py_ssize_t line = 0; line < lineCount; ++line) {
    Shiboken::AutoDecRef _obj(PySequence_GetItem(strList.object(), line));
    xpm[line] = Shiboken::String::toCString(_obj);
}

%0 = new %TYPE(xpm);
// @snippet qpixmap-load-xpm

// @snippet qicon-addpixmap
const auto path = PySide::pyPathToQString(%PYARG_1);
%CPPSELF->addPixmap(path);
// @snippet qicon-addpixmap

// @snippet qclipboard-setpixmap
const auto path = PySide::pyPathToQString(%PYARG_1);
%CPPSELF->setPixmap(QPixmap(path));
// @snippet qclipboard-setpixmap

// @snippet qclipboard-setimage
const auto path = PySide::pyPathToQString(%PYARG_1);
%CPPSELF->setImage(QImage(path));
// @snippet qclipboard-setimage

// @snippet qimage-buffer-constructor
Py_INCREF(%PYARG_1);
auto *ptr = reinterpret_cast<uchar *>(Shiboken::Buffer::getPointer(%PYARG_1));
%0 = new %TYPE(ptr, %ARGS, imageDecrefDataHandler, %PYARG_1);
// @snippet qimage-buffer-constructor

// @snippet qimage-decref-image-data
static void imageDecrefDataHandler(void *data)
{
    // Avoid "Python memory allocator called without holding the GIL"
    auto state = PyGILState_Ensure();
    Py_DECREF(reinterpret_cast<PyObject *>(data));
    PyGILState_Release(state);
}
// @snippet qimage-decref-image-data

// @snippet qimage-constbits
%PYARG_0 = Shiboken::Buffer::newObject(%CPPSELF.%FUNCTION_NAME(), %CPPSELF.sizeInBytes());
// @snippet qimage-constbits

// @snippet qimage-bits
// byteCount() is only available on Qt4.7, so we use bytesPerLine * height
%PYARG_0 = Shiboken::Buffer::newObject(%CPPSELF.%FUNCTION_NAME(), %CPPSELF.bytesPerLine() * %CPPSELF.height(), Shiboken::Buffer::ReadWrite);
// @snippet qimage-bits

// @snippet qimage-constscanline
%PYARG_0 = Shiboken::Buffer::newObject(%CPPSELF.%FUNCTION_NAME(%1), %CPPSELF.bytesPerLine());
// @snippet qimage-constscanline

// @snippet qimage-scanline
%PYARG_0 = Shiboken::Buffer::newObject(%CPPSELF.%FUNCTION_NAME(%1), %CPPSELF.bytesPerLine(), Shiboken::Buffer::ReadWrite);
// @snippet qimage-scanline

// @snippet qcolor-setstate
Shiboken::AutoDecRef func(PyObject_GetAttr(%PYSELF, PyTuple_GetItem(%1, 0)));
PyObject *args = PyTuple_GetItem(%1, 1);
%PYARG_0 = PyObject_Call(func, args, nullptr);
// @snippet qcolor-setstate

// @snippet qcolor-reduce
switch (%CPPSELF.spec()) {
    case QColor::Rgb:
    {
        float r, g, b, a;
        %CPPSELF.getRgbF(&r, &g, &b, &a);
        %PYARG_0 = Py_BuildValue("(ON(s(ffff)))", Py_TYPE(%PYSELF), PyTuple_New(0),
                                 "setRgbF", r, g, b, a);
        break;
    }
    case QColor::Hsv:
    {
        float h, s, v, a;
        %CPPSELF.getHsvF(&h, &s, &v, &a);
        %PYARG_0 = Py_BuildValue("(ON(s(ffff)))", Py_TYPE(%PYSELF), PyTuple_New(0),
                                 "setHsvF", h, s, v, a);
        break;
    }
    case QColor::Cmyk:
    {
        float c, m, y, k, a;
        %CPPSELF.getCmykF(&c, &m, &y, &k, &a);
        %PYARG_0 = Py_BuildValue("(ON(s(fffff)))", Py_TYPE(%PYSELF), PyTuple_New(0),
                                 "setCmykF", c, m, y, k, a);
        break;
    }
    case QColor::Hsl:
    {
        float h, s, l, a;
        %CPPSELF.getHslF(&h, &s, &l, &a);
        %PYARG_0 = Py_BuildValue("(ON(s(ffff)))", Py_TYPE(%PYSELF), PyTuple_New(0),
                                 "setHslF", h, s, l, a);
        break;
    }
    default:
    {
        %PYARG_0 = Py_BuildValue("(N(O))", PyObject_Type(%PYSELF), Py_None);
    }
}
// @snippet qcolor-reduce

// @snippet qcolor-totuple
switch (%CPPSELF.spec()) {
  case QColor::Rgb:
  {
        int r, g, b, a;
        %CPPSELF.getRgb(&r, &g, &b, &a);
        %PYARG_0 = Py_BuildValue("iiii", r, g, b, a);
        break;
  }
  case QColor::Hsv:
  {
        int h, s, v, a;
        %CPPSELF.getHsv(&h, &s, &v, &a);
        %PYARG_0 = Py_BuildValue("iiii", h, s, v, a);
        break;
  }
  case QColor::Cmyk:
  {
        int c, m, y, k, a;
        %CPPSELF.getCmyk(&c, &m, &y, &k, &a);
        %PYARG_0 = Py_BuildValue("iiiii", c, m, y, k, a);
        break;
  }
  case QColor::Hsl:
  {
        int h, s, l, a;
        %CPPSELF.getHsl(&h, &s, &l, &a);
        %PYARG_0 = Py_BuildValue("iiii", h, s, l, a);
        break;
  }
  default:
  {
        %PYARG_0 = 0;
  }
}
// @snippet qcolor-totuple

// @snippet qcolor-repr
QString repr;
switch (%CPPSELF.spec()) {
case QColor::Rgb: {
    float r, g, b, a;
    %CPPSELF.getRgbF(&r, &g, &b, &a);
    repr = QString::asprintf("PySide6.QtGui.QColor.fromRgbF(%.6f, %.6f, %.6f, %.6f)",
                             r, g, b, a);
    break;
}
case QColor::Hsv: {
    float h, s, v, a;
    %CPPSELF.getHsvF(&h, &s, &v, &a);
    repr = QString::asprintf("PySide6.QtGui.QColor.fromHsvF(%.6f, %.6f, %.6f, %.6f)",
                             h, s, v, a);
    break;
}
case QColor::Cmyk: {
    float c, m, y, k, a;
    %CPPSELF.getCmykF(&c, &m, &y, &k, &a);
    repr = QString::asprintf("PySide6.QtGui.QColor.fromCmykF(%.6f, %.6f, %.6f, %.6f, %.6f)",
                             c, m, y, k, a);
    break;
}
case QColor::Hsl: {
    float h, s, l, a;
    %CPPSELF.getHslF(&h, &s, &l, &a);
    repr = QString::asprintf("PySide6.QtGui.QColor.fromHslF(%.6f, %.6f, %.6f, %.6f)",
                             h, s, l, a);
    break;
}
default:
    repr = QLatin1StringView("PySide6.QtGui.QColor()");
    break;
}
%PYARG_0 = Shiboken::String::fromCString(qPrintable(repr));
// @snippet qcolor-repr

// @snippet qcolor
if (%1.type() == QVariant::Color)
    %0 = new %TYPE(%1.value<QColor>());
else
    PyErr_SetString(PyExc_TypeError, "QVariant must be holding a QColor");
// @snippet qcolor

// @snippet qfont-tag-from-str-helper
using FontTagOptional = std::optional<QFont::Tag>;
static std::optional<QFont::Tag> qFontTagFromString(PyObject *unicode)
{
    FontTagOptional result;
    if (PyUnicode_GetLength(unicode) == 4)
        result = QFont::Tag::fromString(PySide::pyUnicodeToQString(unicode));
    if (!result.has_value())
        PyErr_SetString(PyExc_TypeError,
                        "QFont::Tag(): The tag name must be exactly 4 characters long.");
    return result;
}
// @snippet qfont-tag-from-str-helper

// @snippet qfont-tag-init-str
const FontTagOptional tagO = qFontTagFromString(%PYARG_1);
if (tagO.has_value())
    %0 = new QFont::Tag(tagO.value());
// @snippet qfont-tag-init-str

// @snippet qfont-tag-fromString
const FontTagOptional tagO = qFontTagFromString(%PYARG_1);
if (tagO.has_value()) {
    const auto &tag = tagO.value();
    %PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](tag);
}
// @snippet qfont-tag-fromString

// @snippet qfont-tag-fromValue
const FontTagOptional tagO = QFont::Tag::fromValue(PyLong_AsUnsignedLong(%PYARG_1));
if (tagO.has_value()) {
    const auto &tag = tagO.value();
    %PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](tag);
} else {
    PyErr_SetString(PyExc_TypeError, "QFont::Tag::fromValue(): Invalid value passed.");
}
// @snippet qfont-tag-fromValue

// @snippet qfontmetrics-qfontcharfix
if (Shiboken::String::len(%PYARG_1) == 1) {
    const char *str = Shiboken::String::toCString(%PYARG_1);
    const QChar ch(static_cast<unsigned short>(str[0]));
    %RETURN_TYPE %0 = %CPPSELF.%FUNCTION_NAME(ch);
    %PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
} else {
    PyErr_SetString(PyExc_TypeError, "String must have only one character");
}
// @snippet qfontmetrics-qfontcharfix

// @snippet qfontmetricsf-boundingrect
int *array = nullptr;
bool errorOccurred = false;

if (numArgs == 5) {
    array = Shiboken::sequenceToIntArray(%PYARG_5, true);
    if (PyErr_Occurred()) {
        delete [] array;
        errorOccurred = true;
    }
}

if (!errorOccurred) {
    %RETURN_TYPE retval = %CPPSELF.%FUNCTION_NAME(%1, %2, %3, %4, array);

    delete [] array;

    %PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](retval);
}
// @snippet qfontmetricsf-boundingrect

// @snippet qfontmetricsf-size
int *array = nullptr;
bool errorOccurred = false;

if (numArgs == 4) {
    array = Shiboken::sequenceToIntArray(%PYARG_4, true);
    if (PyErr_Occurred()) {
        delete [] array;
        errorOccurred = true;
    }
}

if (!errorOccurred) {
    %RETURN_TYPE retval = %CPPSELF.%FUNCTION_NAME(%1, %2, %3, array);

    delete [] array;

    %PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](retval);
}
// @snippet qfontmetricsf-size

// @snippet qfontmetrics-boundingrect-1
int *array = nullptr;
bool errorOccurred = false;

if (numArgs == 8) {
    array = Shiboken::sequenceToIntArray(%PYARG_8, true);
    if (PyErr_Occurred()) {
        delete [] array;
        errorOccurred = true;
    }
}

if (!errorOccurred) {
    %RETURN_TYPE retval = %CPPSELF.%FUNCTION_NAME(%1, %2, %3, %4, %5, %6, %7, array);

    delete [] array;

    %PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](retval);
}
// @snippet qfontmetrics-boundingrect-1

// @snippet qfontmetrics-boundingrect-2
int *array = nullptr;
bool errorOccurred = false;

if (numArgs == 5) {
    array = Shiboken::sequenceToIntArray(%PYARG_5, true);
    if (PyErr_Occurred()) {
        delete [] array;
        errorOccurred = true;
    }
}

if (!errorOccurred) {
    %RETURN_TYPE retval = %CPPSELF.%FUNCTION_NAME(%1, %2, %3, %4, array);

    delete [] array;

    %PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](retval);
}
// @snippet qfontmetrics-boundingrect-2

// @snippet qfontmetrics-size
int *array = nullptr;
bool errorOccurred = false;

if (numArgs == 4) {
    array = Shiboken::sequenceToIntArray(%PYARG_4, true);
    if (PyErr_Occurred()) {
        delete [] array;
        errorOccurred = true;
    }
}

if (!errorOccurred) {
    %RETURN_TYPE retval = %CPPSELF.%FUNCTION_NAME(%1, %2, %3, array);

    delete [] array;

    %PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](retval);
}
// @snippet qfontmetrics-size

// @snippet qpixmapcache-find
QPixmap p;
if (%CPPSELF.%FUNCTION_NAME(%1, &p)) {
    %PYARG_0 = %CONVERTTOPYTHON[QPixmap](p);
} else {
    %PYARG_0 = Py_None;
    Py_INCREF(%PYARG_0);
}
// @snippet qpixmapcache-find

// @snippet qstandarditem-setchild-1
// Clear parent from the old child
QStandardItem *_i = %CPPSELF->child(%1, %2);
if (_i) {
    PyObject *_pyI = %CONVERTTOPYTHON[QStandardItem *](_i);
    Shiboken::Object::setParent(nullptr, _pyI);
}
// @snippet qstandarditem-setchild-1

// @snippet qstandarditem-setchild-2
// Clear parent from the old child
QStandardItem *_i = %CPPSELF->child(%1);
if (_i) {
    PyObject *_pyI = %CONVERTTOPYTHON[QStandardItem *](_i);
    Shiboken::Object::setParent(nullptr, _pyI);
}
// @snippet qstandarditem-setchild-2

// @snippet qkeyevent-operatornotequal
bool ret = !(&%CPPSELF == %1);
%PYARG_0 = %CONVERTTOPYTHON[bool](ret);
// @snippet qkeyevent-operatornotequal

// @snippet qstandarditemmodel-setitem-1
// Clear parent from the old child
QStandardItem *_i = %CPPSELF->item(%1, %2);
if (_i) {
    PyObject *_pyI = %CONVERTTOPYTHON[QStandardItem *](_i);
    Shiboken::Object::setParent(nullptr, _pyI);
}
// @snippet qstandarditemmodel-setitem-1

// @snippet qstandarditemmodel-setitem-2
// Clear parent from the old child
QStandardItem *_i = %CPPSELF->item(%1);
if (_i) {
    PyObject *_pyI = %CONVERTTOPYTHON[QStandardItem *](_i);
    Shiboken::Object::setParent(nullptr, _pyI);
}
// @snippet qstandarditemmodel-setitem-2

// @snippet qstandarditemmodel-setverticalheaderitem
// Clear parent from the old child
QStandardItem *_i = %CPPSELF->verticalHeaderItem(%1);
if (_i) {
    PyObject *_pyI = %CONVERTTOPYTHON[QStandardItem *](_i);
    Shiboken::Object::setParent(nullptr, _pyI);
}
// @snippet qstandarditemmodel-setverticalheaderitem

// @snippet qstandarditemmodel-clear
Shiboken::BindingManager &bm = Shiboken::BindingManager::instance();
SbkObject *pyRoot = bm.retrieveWrapper(%CPPSELF.invisibleRootItem());
if (pyRoot) {
  Shiboken::Object::destroy(pyRoot, %CPPSELF.invisibleRootItem());
}

for (int r=0, r_max = %CPPSELF.rowCount(); r < r_max; r++) {
  QList<QStandardItem *> ri = %CPPSELF.takeRow(0);

  PyObject *pyResult = %CONVERTTOPYTHON[QList<QStandardItem * >](ri);
  Shiboken::Object::setParent(Py_None, pyResult);
  Py_XDECREF(pyResult);
}
// @snippet qstandarditemmodel-clear

// @snippet qclipboard-text
%BEGIN_ALLOW_THREADS
%RETURN_TYPE retval_ = %CPPSELF.%FUNCTION_NAME(%1, %2);
%END_ALLOW_THREADS
%PYARG_0 = PyTuple_New(2);
PyTuple_SetItem(%PYARG_0, 0, %CONVERTTOPYTHON[%RETURN_TYPE](retval_));
PyTuple_SetItem(%PYARG_0, 1, %CONVERTTOPYTHON[%ARG1_TYPE](%1));
// @snippet qclipboard-text

// @snippet qpainter-drawpointsnp-numpy-x-y
const auto points = PySide::Numpy::xyDataToQPointFList(%PYARG_1, %PYARG_2);
%CPPSELF.drawPoints(points);
// @snippet qpainter-drawpointsnp-numpy-x-y

// @snippet qpainter-drawpolygon
%CPPSELF.%FUNCTION_NAME(%1.constData(), %1.size(), %2);
// @snippet qpainter-drawpolygon

// @snippet qpainter-enter
Py_INCREF(%PYSELF);
pyResult = %PYSELF;
// @snippet qpainter-enter

// @snippet qpainter-exit
%CPPSELF.end();
// @snippet qpainter-exit

// @snippet qmatrix4x4
// PYSIDE-795: All PySequences can be made iterable with PySequence_Fast.
Shiboken::AutoDecRef seq(PySequence_Fast(%PYARG_1, "Can't turn into sequence"));
if (PySequence_Size(seq) == 16) {
    float values[16];
    for (Py_ssize_t i = 0; i < 16; ++i) {
        Shiboken::AutoDecRef pv(PySequence_GetItem(seq.object(), i));
        values[i] = PyFloat_AsDouble(pv);
    }

    %0 = new %TYPE(values[0], values[1], values[2], values[3],
                   values[4], values[5], values[6], values[7],
                   values[8], values[9], values[10], values[11],
                   values[12], values[13], values[14], values[15]);
}
// @snippet qmatrix4x4

// @snippet qmatrix4x4-copydatato
float values[16];
%CPPSELF.%FUNCTION_NAME(values);
%PYARG_0 = PyTuple_New(16);
for (Py_ssize_t i = 0; i < 16; ++i) {
  PyObject *v = PyFloat_FromDouble(values[i]);
  PyTuple_SetItem(%PYARG_0, i, v);
}
// @snippet qmatrix4x4-copydatato

// @snippet qmatrix4x4-mgetitem
if (PySequence_Check(_key)) {
    Shiboken::AutoDecRef key(PySequence_Fast(_key, "Invalid matrix index."));
    if (PySequence_Size(key.object()) == 2) {
        Shiboken::AutoDecRef posx(PySequence_GetItem(key.object(), 0));
        Shiboken::AutoDecRef posy(PySequence_GetItem(key.object(), 1));
        Py_ssize_t x = PyLong_AsSsize_t(posx);
        Py_ssize_t y = PyLong_AsSsize_t(posy);
        float ret = (*%CPPSELF)(x,y);
        return %CONVERTTOPYTHON[float](ret);
    }
}
PyErr_SetString(PyExc_IndexError, "Invalid matrix index.");
return 0;
// @snippet qmatrix4x4-mgetitem

// @snippet qguiapplication-init
static void QGuiApplicationConstructor(PyObject *self, PyObject *pyargv, QGuiApplicationWrapper **cptr)
{
    static int argc;
    static char **argv;
    PyObject *stringlist = PyTuple_GetItem(pyargv, 0);
    if (Shiboken::listToArgcArgv(stringlist, &argc, &argv, "PySideApp")) {
        *cptr = new QGuiApplicationWrapper(argc, argv, 0);
        Shiboken::Object::releaseOwnership(reinterpret_cast<SbkObject *>(self));
        PySide::registerCleanupFunction(&PySide::destroyQCoreApplication);
    }
}
// @snippet qguiapplication-init

// @snippet qguiapplication-1
QGuiApplicationConstructor(%PYSELF, args, &%0);
// @snippet qguiapplication-1

// @snippet qguiapplication-2
PyObject *empty = PyTuple_New(2);
if (!PyTuple_SetItem(empty, 0, PyList_New(0))) {
    QGuiApplicationConstructor(%PYSELF, empty, &%0);
}
// @snippet qguiapplication-2

// @snippet qguiapplication-setoverridecursor
auto *cppResult = new QtGuiHelper::QOverrideCursorGuard();
%PYARG_0 = %CONVERTTOPYTHON[QtGuiHelper::QOverrideCursorGuard*](cppResult);
Shiboken::Object::getOwnership(%PYARG_0); // Ensure the guard is removed
// @snippet qguiapplication-setoverridecursor

// @snippet qguiapplication-nativeInterface
bool hasNativeApp = false;
#if QT_CONFIG(xcb)
if (auto *x11App = %CPPSELF.nativeInterface<QNativeInterface::QX11Application>()) {
    hasNativeApp = true;
    %PYARG_0 = %CONVERTTOPYTHON[QNativeInterface::QX11Application*](x11App);
}
#endif
if (!hasNativeApp) {
    Py_INCREF(Py_None);
    %PYARG_0 = Py_None;
}
// @snippet qguiapplication-nativeInterface

// @snippet qscreen-grabWindow
WId id = %1;
%RETURN_TYPE retval = %CPPSELF.%FUNCTION_NAME(id, %2, %3, %4, %5);
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](retval);
// @snippet qscreen-grabWindow

// @snippet qscreen-nativeInterface
bool hasNativeScreen = false;
#ifdef Q_OS_WIN
if (auto *winScreen = %CPPSELF.nativeInterface<QNativeInterface::QWindowsScreen>()) {
    hasNativeScreen = true;
    %PYARG_0 = %CONVERTTOPYTHON[QNativeInterface::QWindowsScreen*](winScreen);
}
#endif
if (!hasNativeScreen) {
    Py_INCREF(Py_None);
    %PYARG_0 = Py_None;
}
// @snippet qscreen-nativeInterface

// @snippet qx11application-resource-ptr
 auto *resource = %CPPSELF.%FUNCTION_NAME();
%PYARG_0 = PyLong_FromVoidPtr(resource);
// @snippet qx11application-resource-ptr

// @snippet qwindow-fromWinId
WId id = %1;
%RETURN_TYPE retval = %CPPSELF.%FUNCTION_NAME(id);
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](retval);
// @snippet qwindow-fromWinId

// @snippet set-qtkey-shortcut
%CPPSELF.%FUNCTION_NAME(QKeyCombination(%1));
// @snippet set-qtkey-shortcut

// @snippet qshortcut-1
%0 = new %TYPE(%1, %2);
// @snippet qshortcut-1

// @snippet qshortcut-2
Shiboken::AutoDecRef result(PyObject_CallMethod(%PYSELF, "connect", "OsO",
                                                %PYSELF, SIGNAL(activated()), %PYARG_3)
                            );
if (!result.isNull())
    Shiboken::Object::setParent(%PYARG_2, %PYSELF);
// @snippet qshortcut-2

// @snippet qguiapplication-exec
if (PyErr_WarnEx(PyExc_DeprecationWarning,
                 "'exec_' will be removed in the future. "
                 "Use 'exec' instead.",
                 1)) {
    return nullptr;
}
%BEGIN_ALLOW_THREADS
int cppResult = %CPPSELF.exec();
%END_ALLOW_THREADS
%PYARG_0 = %CONVERTTOPYTHON[int](cppResult);
// @snippet qguiapplication-exec

// @snippet qdrag-exec-arg1
if (PyErr_WarnEx(PyExc_DeprecationWarning,
                 "'exec_' will be removed in the future. "
                 "Use 'exec' instead.",
                 1)) {
    return nullptr;
}
%BEGIN_ALLOW_THREADS
int cppResult = %CPPSELF.exec(%1);
%END_ALLOW_THREADS
%PYARG_0 = %CONVERTTOPYTHON[int](cppResult);
// @snippet qdrag-exec-arg1

// @snippet qdrag-exec-arg2
if (PyErr_WarnEx(PyExc_DeprecationWarning,
                 "'exec_' will be removed in the future. "
                 "Use 'exec' instead.",
                 1)) {
    return nullptr;
}
%BEGIN_ALLOW_THREADS
int cppResult;
if (numArgs == 2)
    cppResult = %CPPSELF.exec(%1, %2);
else if (numArgs == 1)
    cppResult = %CPPSELF.exec(%1);
else
    cppResult = %CPPSELF.exec();
%END_ALLOW_THREADS
%PYARG_0 = %CONVERTTOPYTHON[int](cppResult);
// @snippet qdrag-exec-arg2

// @snippet qquaternion-getaxisandangle-vector3d-float
QVector3D outVec{};
float angle{};
%CPPSELF.%FUNCTION_NAME(&outVec, &angle);
%PYARG_0 = PyTuple_New(2);
PyTuple_SetItem(%PYARG_0, 0, %CONVERTTOPYTHON[QVector3D](outVec));
PyTuple_SetItem(%PYARG_0, 1, %CONVERTTOPYTHON[float](angle));
// @snippet qquaternion-getaxisandangle-vector3d-float

// @snippet qquaternion-geteulerangles
float pitch{}, yaw{}, roll{};
%CPPSELF.%FUNCTION_NAME(&pitch, &yaw, &roll);
%PYARG_0 = PyTuple_New(3);
PyTuple_SetItem(%PYARG_0, 0, %CONVERTTOPYTHON[float](pitch));
PyTuple_SetItem(%PYARG_0, 1, %CONVERTTOPYTHON[float](yaw));
PyTuple_SetItem(%PYARG_0, 2, %CONVERTTOPYTHON[float](roll));
// @snippet qquaternion-geteulerangles

// @snippet qregion-len
return %CPPSELF.rectCount();
// @snippet qregion-len

// @snippet qregion-getitem
const Py_ssize_t size = %CPPSELF.rectCount();
if (_i < 0 || _i >= size) {
    Shiboken::Errors::setIndexOutOfBounds(_i, 0, size);
    return nullptr;
}

const QRect cppResult = *(%CPPSELF.cbegin() + _i);
return %CONVERTTOPYTHON[QRect](cppResult);
// @snippet qregion-getitem

// Some RHI functions take a std::initializer_list<>. Add functions
// to convert from list.

// @snippet qrhi-initializer-list
%CPPSELF.%FUNCTION_NAME(%1.cbegin(), %1.cend());
// @snippet qrhi-initializer-list

// @snippet qrhi-commandbuffer-setvertexinput
%CPPSELF.%FUNCTION_NAME(%1, %2.size(), %2.constData(), %3, %4, %5);
// @snippet qrhi-commandbuffer-setvertexinput

// @snippet qpainterstateguard-restore
%CPPSELF.restore();
// @snippet qpainterstateguard-restore

// @snippet qmatrix-repr-code
QByteArray format(Py_TYPE(%PYSELF)->tp_name);
format += QByteArrayLiteral("((");
%MATRIX_TYPE data[%MATRIX_SIZE];
%CPPSELF.copyDataTo(data);
for (int i = 0; i < %MATRIX_SIZE; ++i) {
    if (i > 0)
        format += ", ";
    format += QByteArray::number(data[i]);
}
format += "))";

%PYARG_0 = Shiboken::String::fromStringAndSize(format, format.size());
// @snippet qmatrix-repr-code

// @snippet qmatrix-reduce-code
%MATRIX_TYPE data[%MATRIX_SIZE];
%CPPSELF.copyDataTo(data);
QList<%MATRIX_TYPE> cppArgs(data, data + %MATRIX_SIZE);
PyObject *type = PyObject_Type(%PYSELF);
PyObject *args = Py_BuildValue("(N)",
                               %CONVERTTOPYTHON[QList<%MATRIX_TYPE>](cppArgs));
%PYARG_0 = Py_BuildValue("(NN)", type, args);
// @snippet qmatrix-reduce-code

// @snippet qmatrix-data-function
PyObject *pyData = PyTuple_New(%MATRIX_SIZE);
if (const float *data = %CPPSELF.constData()) {
    for (int i = 0; i < %MATRIX_SIZE; ++i)
        PyTuple_SetItem(pyData, i, %CONVERTTOPYTHON[float](data[i]));
}
return pyData;
// @snippet qmatrix-data-function

// @snippet qmatrix-constructor
// PYSIDE-795: All PySequences can be made iterable with PySequence_Fast.
Shiboken::AutoDecRef seq(PySequence_Fast(%PYARG_1, "Can't turn into sequence"));
if (PySequence_Size(seq) == %SIZE) {
    Shiboken::AutoDecRef fast(PySequence_Fast(seq,
                                              "Failed to parse sequence on %TYPE constructor."));
    float values[%SIZE];
    for (int i = 0; i < %SIZE; ++i) {
        Shiboken::AutoDecRef pv(PySequence_GetItem(fast.object(), i));
        values[i] = %CONVERTTOCPP[float](pv);
    }
    %0 = new %TYPE(values);
}
// @snippet qmatrix-constructor

// @snippet validator-conversionrule
QValidator::State %out;

if (PySequence_Check(%PYARG_0)) {
    Shiboken::AutoDecRef seq(PySequence_Fast(%PYARG_0, 0));
    const Py_ssize_t size = PySequence_Size(seq.object());

    if (size > 1) {
        Shiboken::AutoDecRef _obj1(PySequence_GetItem(seq.object(), 1));
        if (%ISCONVERTIBLE[QString](_obj1))
            %1 = %CONVERTTOCPP[QString](_obj1);
        else
            qWarning("%TYPE::%FUNCTION_NAME: Second tuple element is not convertible to unicode.");
    }

    if (size > 2) {
        Shiboken::AutoDecRef _obj2(PySequence_GetItem(seq.object(), 2));
        if (%ISCONVERTIBLE[int](_obj2))
            %2 = %CONVERTTOCPP[int](_obj2);
        else
            qWarning("%TYPE::%FUNCTION_NAME: Second tuple element is not convertible to int.");
    }
    Shiboken::AutoDecRef _sobj(PySequence_GetItem(seq.object(), 0));

    %PYARG_0.reset(_sobj);
    Py_INCREF(%PYARG_0); // we need to incref, because "%PYARG_0 = ..." will decref the tuple and the tuple will be decrefed again at the end of this scope.
}

// check return value
if (%ISCONVERTIBLE[QValidator::State](%PYARG_0)) {
    %out = %CONVERTTOCPP[QValidator::State](%PYARG_0);
} else {
    PyErr_Format(PyExc_TypeError, "Invalid return value in function %s, expected %s, got %s.",
                 "QValidator.validate",
                 "PySide6.QtGui.QValidator.State, (PySide6.QtGui.QValidator.State,), (PySide6.QtGui.QValidator.State, unicode) or (PySide6.QtGui.QValidator.State, unicode, int)",
                 Py_TYPE(pyResult)->tp_name);
    return QValidator::State();
}
// @snippet validator-conversionrule

// @snippet fix_margins_return
PyObject *obj = %PYARG_0.object();
bool ok = false;
if (PySequence_Check(obj) != 0 && PySequence_Size(obj) == 4) {
    Shiboken::AutoDecRef m0(PySequence_GetItem(obj, 0));
    Shiboken::AutoDecRef m1(PySequence_GetItem(obj, 1));
    Shiboken::AutoDecRef m2(PySequence_GetItem(obj, 2));
    Shiboken::AutoDecRef m3(PySequence_GetItem(obj, 3));
    ok = PyNumber_Check(m0) != 0 && PyNumber_Check(m1) != 0
         && PyNumber_Check(m2) && PyNumber_Check(m3) != 0;
    if (ok) {
        *%1 = %CONVERTTOCPP[$TYPE](m0);
        *%2 = %CONVERTTOCPP[$TYPE](m1);
        *%3 = %CONVERTTOCPP[$TYPE](m2);
        *%4 = %CONVERTTOCPP[$TYPE](m3);
    }
}
if (!ok) {
    PyErr_SetString(PyExc_TypeError, "Sequence of 4 numbers expected");
    %1 = %2 = %3 = %4 = 0;
}
// @snippet fix_margins_return

/*********************************************************************
 * CONVERSIONS
 ********************************************************************/

// @snippet conversion-pylong
%out = reinterpret_cast<%OUTTYPE>(PyLong_AsVoidPtr(%in));
// @snippet conversion-pylong

/*********************************************************************
 * NATIVE TO TARGET CONVERSIONS
 ********************************************************************/

// @snippet return-pylong-voidptr
return PyLong_FromVoidPtr(reinterpret_cast<void *>(%in));
// @snippet return-pylong-voidptr
