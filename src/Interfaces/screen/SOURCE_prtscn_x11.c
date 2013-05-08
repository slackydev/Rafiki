#include <stdio.h>
#include <X11/X.h>
#include <X11/Xlib.h>
//Compile hint: gcc -shared -O3 -lX11 -fPIC -Wl,-soname,prtscn_x11 -o prtscn_x11.so SOURCE_prtscn_x11.c

Display *display;

void getScreen(const int, const int, const int, const int, unsigned char *);
void getScreen(const int xx,const int yy,const int W, const int H, /*out*/ unsigned char * data) 
{
   display = XOpenDisplay(NULL);
   Window root = DefaultRootWindow(display);

   XImage *image = XGetImage(display,root, xx,yy, W,H, AllPlanes, ZPixmap);
   XCloseDisplay(display);
   
   unsigned long red_mask = image->red_mask;
   unsigned long green_mask = image->green_mask;
   unsigned long blue_mask = image->blue_mask;
   int x, y;
   for (x = 0; x < W; x++) {
      for (y = 0; y < H; y++) {
         unsigned long pixel = XGetPixel(image,x,y);
         int ii = (x + W * y) * 3;

         unsigned char blue = pixel & blue_mask;
         unsigned char green = (pixel & green_mask) >> 8;
         unsigned char red = (pixel & red_mask) >> 16;

         data[ii + 2] = blue;
         data[ii + 1] = green;
         data[ii + 0] = red;
      }
   }

   XFree(image);
}
