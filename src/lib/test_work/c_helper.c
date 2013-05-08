/*------------------------------------------------------------------------------
 THIS FILE IS PART OF Rafiki Macro Library
 I do not know SHIT about C!! (if anyone could fix this, I would be very glad!)
--------------------------------------------------------------------------------*/

#include <stdio.h>
//To compile: gcc -shared -O3 -ffast-math -Wl,-soname,sample -o sample.dll sample.c

//------- EXPORTS ------//
void rgb_to_lab(int,int,int, float*, float*, float*);
bool find_color(?)

//------ STRUCTS ------//
typedef struct {
    int x;
    int y;
} Point;



typedef struct { //Used by dyn array.
  int *array;
  size_t used;
  size_t size;
} Array;

//------ DYNAMIC ARRAY ------//
void initPointArray(Array *a, size_t initialSize) {
  a->array = (int *)malloc(initialSize * sizeof(int));
  a->used = 0;
  a->size = initialSize;
}

void PointArrayAdd(Array *a, int element) {
  if (a->used == a->size) {
    a->size *= 2;
    a->array = (int *)realloc(a->array, a->size * sizeof(int));
  }
  a->array[a->used++] = element;
}

void freePointArray(Array *a) {
  free(a->array);
  a->array = NULL;
  a->used = a->size = 0;
}
//------ END OF DYNAMIC ARRAY ------//


/********************************** COLORMATH!! ***********************************/
//-----------------------
void RGB_to_XYZ(int R, int G, int B, /*out:*/ float* X, float* Y, float* Z) {
    /*
    Convert from RGB to XYZ
    */
    float var_R = R / 255.0f;
    float var_G = G / 255.0f;
    float var_B = B / 255.0f;

    if(var_R > 0.04045) var_R = pow(((var_R + 0.055f) / 1.055f), 2.4f);
    else var_R = var_R/12.92f;

    if(var_G > 0.04045) var_G = pow(((var_G + 0.055f) / 1.055f), 2.4f);
    else var_G = var_G/12.92f;
        
    if(var_B > 0.04045) var_B = pow(((var_B + 0.055f) / 1.055f), 2.4f);
    else var_B = var_B/12.92f;

    var_R = var_R*100;
    var_G = var_G*100;
    var_B = var_B*100;

    //Observer. = 2 deg, Illuminant = D65
    *X = var_R * 0.4124f + var_G * 0.3576f + var_B * 0.1805f;
    *Y = var_R * 0.2126f + var_G * 0.7152f + var_B * 0.0722f;
    *Z = var_R * 0.0193f + var_G * 0.1192f + var_B * 0.9505f;
}

//-----------------------
void XYZ_to_LAB(float X,float Y,float Z,  /*out:*/  float* L, float* a, float* b) {
    /*
    Convert from XYZ to CIE-L*a*b*
    */
    float ref_X =  95.047f;
    float ref_Y = 100.000f;
    float ref_Z = 108.883f;
    
    float var_X = X / ref_X;
    float var_Y = Y / ref_Y;
    float var_Z = Z / ref_Z;

    if(var_X > 0.008856f) { var_X = pow(var_X, 0.3334f); } /* 1/3.0f = 0.333333333334; */
    else { var_X = (7.787f*var_X) + (16/116); }
    
    if(var_Y > 0.008856f) { var_Y = pow(var_Y, 0.3334f); }
    else { var_Y = (7.787f*var_Y) + (16/116); }
    
    if(var_Z > 0.008856f) { var_Z = pow(var_Z, 0.3334f); }
    else { var_Z = (7.787f*var_Z) + (16/116); }

    *L = (116.0f * var_Y) - 16;
    *a = 500.0f * (var_X - var_Y);
    *b = 200.0f * (var_Y - var_Z);
}

//-----------------------
void rgb_to_lab(int R, int G, int B, float* OL, float* Oa, float* Ob) {
    float X,Y,Z;
    float L,a,b;
    RGB_to_XYZ(R,G,B, &X,&Y,&Z);
    XYZ_to_LAB(X,Y,Z, &L,&a,&b);
    *OL = L;
    *Oa = a;
    *Ob = b;
}


/********************************** COLORFINDING ***********************************/
bool find_color(int *pts, unsigned char color[3], int minx,int miny,int maxx,int maxy,  
                int tol, unsigned char *buffer, int colorMode) 
{
    Array arr;
    float L,a,b;
    if (colorMode == 1) or (colorMode == 2) {
        rgb_to_lab(color[0], color[1], color[2], &L,&a,&b)
        float color1[] = {L,a,b}
    }
    
    initPointArray(&arr, 0);
    unsigned char color2[3]
    int x,y, i;
    for (x = minx; x < maxx; x++) {
       for (y = miny; y < maxy; y++) {
          color2[0] = buffer[i++];
          color2[1] = buffer[i++];
          color2[2] = buffer[i++];
          if (compare(color1, color2, tol)) {
             Point R;
             R.x = x;
             R.y = y;
             PointArrayAdd(&arr, R);
          }
       }
    }
    pts = arr;
    if sizeof(pts)>0 {
      return false;
    } else {
      return true;
    }
    
}



























