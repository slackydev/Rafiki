/*------------------------------------------------------------------------------
 THIS FILE IS PART OF Rafiki Macro Library
 I do not know SHIT about C!! (if anyone could fix this, I would be very glad!)
 
 You will find that exported functions is maintained by python, 
 therefor we also got a lot of parameters for thoes functions.
  
 Compilation: gcc -shared -O2 -ffast-math -fPIC -Wl,-soname,c_helper -o c_helper.so c_helper.c
--------------------------------------------------------------------------------*/
#include <stdio.h>
#include <math.h>
#include <stdbool.h> 
#include <stdlib.h>
#include <string.h>

#define min(a,b) (((a)<(b))?(a):(b))
#define max(a,b) (((a)>(b))?(a):(b))

typedef unsigned char byte;

/**
 * 	Export definitions, I don't know if this is needed...
 *  so I guess it is! :)
 */
int* find_colors(int*,byte*,int,int,int,int,int,byte*,int);
//int* find_color(...);
//int* find_colors_spiral(...);
//int* find_color_spiral(...);
//int* find_colored_box(...);
//int* find_colored_boxes(...);
//int* find_DTM(..);
//int* find_DTMs(..);



/*=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\
|=-=-=-=-=-=-=-=-=-=-=-=-=-= COLOR CONVERSION =-=-=-=-=-=-=-=-=-=-=-=-=|
\=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=*/

/**
 *	Convert from RGB to XYZ
 *	@note: It's somewhat slower then expected, some parts can be cached.
 */
static inline void rgb_to_xyz(byte R, byte G, byte B, float* X, float* Y, float* Z) 
{
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

/**
 *	Convert from XYZ to CIE-L*a*b*
 *	@note: It's somewhat slower then expected...
 */
static inline void xyz_to_lab(float X,float Y,float Z, float* L, float* a, float* b) 
{   
    float var_X = X / 95.047f;
    float var_Y = Y / 100.000f;
    float var_Z = Z / 108.883f;

    if(var_X > 0.008856f) { var_X = pow(var_X, 1/3.0f); }
    else { var_X = (7.787f*var_X) + (16/116.0f); }
    
    if(var_Y > 0.008856f) { var_Y = pow(var_Y, 1/3.0f); }
    else { var_Y = (7.787f*var_Y) + (16/116.0f); }
    
    if(var_Z > 0.008856f) { var_Z = pow(var_Z, 1/3.0f); }
    else { var_Z = (7.787f*var_Z) + (16/116.0f); }

    *L = (116.0f * var_Y) - 16;
    *a = 500.0f * (var_X - var_Y);
    *b = 200.0f * (var_Y - var_Z);
}

/**
 *	Convert from RGB to LAB
 *	@note: It's somewhat slower then expected...
 */
static inline void rgb_to_lab(byte R, byte G, byte B, float* OL, float* Oa, float* Ob) 
{
    float X,Y,Z;
    float L,a,b;
    rgb_to_xyz(R,G,B, &X,&Y,&Z);
    xyz_to_lab(X,Y,Z, &L,&a,&b);
    *OL = L;
    *Oa = a;
    *Ob = b;
}

/**
 *	Convert from RGB to HSB/HSL
 *	@note: there seems to be some mistakes... Can't say for sure..
 */
static void rgb_to_hsl(byte R, byte G, byte B, float* H, float* S, float* L) 
{
    float CMax,CMin,Delta, var_H, var_S, var_L;
    float vR = (R / 255.0f);
    float vG = (G / 255.0f);
    float vB = (B / 255.0f);

    CMax = max(vR, max(vG, vB));      // Max. value of RGB
    CMin = min(vR, min(vG, vB));      // Min. value of RGB
    Delta = CMax - CMin;              // Delta RGB value

    var_L = (CMax + CMin) / 2;
    if (Delta == 0) {                 // Achromatic
        var_H = 0;
        var_S = 0;
    } else {                          // Calculate the chroma...
        if (var_L > 0.5f) { var_S = Delta / (2 - CMax - CMin); }
        else { var_S = Delta / (CMax + CMin); }

        if (vR == CMax) { 
            if(vG >= vB) var_H = (vG-vB) / Delta + 6;
            else var_H = (vG-vB) / Delta;
        }    
        else if (vG == CMax) { var_H = (vB-vR) / Delta + 2; }
        else if (vB == CMax) { var_H = (vR-vG) / Delta + 4; }
        var_H /= 6;
    }
    
    *H = var_H * 100;
    *S = var_S * 100;
    *L = var_L * 100;
}


/*=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\
|=-=-=-=-=-=-=-=-=-=-=-=-=  FINDER FUNCTIONS  =-=-=-=-=-=-=-=-=-=-=-=-=|
\=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=*/

/**
 *	Convert a color to the given colormode!
 *	@todo: ??
 */
static bool to_mode(byte *in, float *out, int cmode) 
{
	float a,b,c;
	
	if((cmode == 0) || (cmode == 1)) {
		out[0] = in[0];
		out[1] = in[1];
		out[2] = in[2];
		return true;
		
	} else if(cmode == 2) {
		rgb_to_hsl(in[0], in[1], in[2], &a,&b,&c);
		out[0] = a;
		out[1] = b;
		out[2] = c;
		return true;
		
	} else if(cmode == 3) {
		rgb_to_lab(in[0], in[1], in[2], &a,&b,&c);
		out[0] = a;
		out[1] = b;
		out[2] = c;
		return true;
	}
	
}

/**
 *	compare two colors, with the given colorspace
 *	@params: 
 *  	color1 = a color of RGB, Lab, or hsl
 *  	rgb    = color of RGB
 *  	tolerance = max differance between param 1 and 2.
 *  	cmode = what colorspace...
 */
static bool compare(float *color1, byte *rgb, int tolerance, int cmode) 
{
    float A,B,C, h,s,l,a,b;
	
    if(cmode == 0) {
        return (abs(rgb[0] - color1[0]) <= tolerance &&
                abs(rgb[1] - color1[1]) <= tolerance &&
                abs(rgb[2] - color1[2]) <= tolerance);
    } 
    else if(cmode == 1) {
        A = color1[0] - rgb[0];
        B = color1[1] - rgb[1];
        C = color1[2] - rgb[2];
        return sqrt(A*A + B*B + C*C) <= tolerance;
    } 
    else if(cmode == 2) {
        rgb_to_hsl(rgb[0], rgb[1], rgb[2], &h,&s,&l);
        if(h > color1[0])
            A = min(h - color1[0], abs(h - (color1[0] + 100)));
        else
            A = min(color1[0] - h, abs(color1[0] - (h + 100)));
        B = color1[1] - s;
        C = color1[2] - l;
        return sqrt(A*A + B*B + C*C) <= tolerance;
    }
    else if(cmode == 3) {
        rgb_to_lab(rgb[0], rgb[1], rgb[2], &l,&a,&b);
        A = color1[0] - l;
        B = color1[1] - a;
        C = color1[2] - b;
        return sqrt(A*A + B*B + C*C) <= tolerance;
    }
}


/**
 *	Find all pixels with similar color to `byte *color`
 *	@todo: It's working, but might need som adjusting...
 */
int* find_colors(int *size, byte *color, 
				int minx, int miny, int maxx, int maxy, int tol, 
				byte *buffer, int colormode) 
{
    int *pts = NULL;
    
    int x,y, i=0, j=0;
    float L,a,b;
    byte color2[3];
    float color1[3];
    
    to_mode(color, color1, colormode);

    for (y = miny; y < maxy; y++) {
        for (x = minx; x < maxx; x++) {
            color2[0] = buffer[i++];
            color2[1] = buffer[i++];
            color2[2] = buffer[i++];
            
            if(compare(color1, color2, tol, colormode)) {
                pts = realloc(pts, sizeof(int) * j+2);
                pts[j++] = x;
                pts[j++] = y;
            }
        }
    }
    
    *size = j;
    return pts;
}

/**
 *	Find first pixel with similar color to `byte *color`
 *	@todo: It's working, but might need som adjusting...
 */
/*
int* find_color(byte *color, int minx, int miny, int maxx, int maxy, 
				int tol, byte *buffer, int colormode) 
{
    int *pts = NULL;
    pts = realloc(pts, sizeof(int) * 2);
    
    int x,y, i=0, j=0;
    float L,a,b;
    byte color2[3];
    float color1[3];
    
    to_mode(color, color1, colormode);

    for (y = miny; y < maxy; y++) {
        for (x = minx; x < maxx; x++) {
            color2[0] = buffer[i++];
            color2[1] = buffer[i++];
            color2[2] = buffer[i++];
            
            if(compare(color1, color2, tol, colormode)) {
                pts[0] = x;
                pts[1] = y;
                goto finish;
            }
        }
    }
    
    finish:
    return pts;
}*/

//int* find_colors_spiral(...);
/*

int* find_colors_spiral(int X, int Y){
    int x,y,dx,dy;
    x = y = dx = 0;
    dy = -1;
    int t = max(X,Y);
    int maxI = t*t;
    for(int i =0; i < maxI; i++){
        if ((-X/2 <= x) && (x <= X/2) && (-Y/2 <= y) && (y <= Y/2)){
            // DO STUFF...
        }
        if( (x == y) || ((x < 0) && (x == -y)) || ((x > 0) && (x == 1-y))){
            t = dx;
            dx = -dy;
            dy = t;
        }
        x += dx;
        y += dy;
    }
}

*/
//int* find_color_spiral(...);






















