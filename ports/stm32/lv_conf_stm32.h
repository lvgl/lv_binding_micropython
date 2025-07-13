/**
 * @file lv_conf.h
 * Configuration file for v9.3.0
 */

#include "../../lv_conf.h"


#undef LV_USE_ANIMIMG    
#define LV_USE_ANIMIMG    0

#undef LV_USE_ARCLABEL  
#define LV_USE_ARCLABEL  0

#undef LV_USE_CALENDAR   
#define LV_USE_CALENDAR   0

#undef LV_USE_CHECKBOX   
#define LV_USE_CHECKBOX   0

#undef LV_USE_IMAGEBUTTON     
#define LV_USE_IMAGEBUTTON     0

#undef LV_USE_KEYBOARD   
#define LV_USE_KEYBOARD   0

#undef LV_USE_LED        
#define LV_USE_LED        0

#undef LV_USE_MSGBOX     
#define LV_USE_MSGBOX     0

#undef LV_USE_ROLLER        
#define LV_USE_ROLLER     0   /**< Requires: lv_label */

#undef LV_USE_SPAN       
#define LV_USE_SPAN       0

#undef LV_USE_TABLE      
#define LV_USE_TABLE      0

#undef LV_USE_TABVIEW    
#define LV_USE_TABVIEW    0

#undef LV_USE_WIN        
#define LV_USE_WIN        0

#undef LV_USE_3DTEXTURE  
#define LV_USE_3DTEXTURE  0


/** LODEPNG decoder library */
#undef LV_USE_LODEPNG 
#define LV_USE_LODEPNG 0

/** PNG decoder(libpng) library */
#undef LV_USE_LIBPNG 
#define LV_USE_LIBPNG 0

/** JPG + split JPG decoder library.
 *  Split JPG is a custom format optimized for embedded systems. */
#undef LV_USE_TJPGD 
#define LV_USE_TJPGD 0

/** libjpeg-turbo decoder library.
 *  - Supports complete JPEG specifications and high-performance JPEG decoding. */
#undef LV_USE_LIBJPEG_TURBO 
#define LV_USE_LIBJPEG_TURBO 0

/** GIF decoder library */
#undef LV_USE_GIF 
#define LV_USE_GIF 0

/** Barcode code library */
#undef LV_USE_BARCODE 
#define LV_USE_BARCODE 0

/** 1: Enable API to take snapshot for object */
#undef LV_USE_SNAPSHOT 
#define LV_USE_SNAPSHOT 0
