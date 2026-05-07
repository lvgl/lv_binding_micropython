#ifndef FREETYPE_H
#define FREETYPE_H

typedef struct FT_LibraryRec_ * FT_Library;
typedef struct FT_FaceRec_ *    FT_Face;
typedef struct FT_GlyphRec_ *   FT_Glyph;
typedef struct FT_SizeRec_ *    FT_Size;
typedef void *                  FTC_FaceID;
typedef int                     FT_Error;
typedef long                    FT_Pos;
typedef unsigned int            FT_UInt;
typedef int                     FT_Int;
typedef long                    FT_Long;
typedef unsigned long           FT_ULong;
typedef short                   FT_Short;
typedef unsigned short          FT_UShort;
typedef signed long             FT_Fixed;
typedef signed long             FT_F26Dot6;

typedef struct { FT_Pos x; FT_Pos y; } FT_Vector;
typedef struct { FT_Pos xMin, yMin, xMax, yMax; } FT_BBox;

#endif
