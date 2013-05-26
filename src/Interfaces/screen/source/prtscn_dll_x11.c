#include <stdio.h>
#include <X11/X.h>
#include <X11/Xlib.h>
//Compile hint: gcc -shared -O3 -lX11 -fPIC -Wl,-soname,cprtscn_x11 -o cprtscn_x11.so cprtscn_x11.c

Display *display;

void getScreen(const int, const int, const int, const int, unsigned char *);
void getScreen(const int xx,const int yy,const int W, const int H, /*out*/ unsigned char * data) 
{
	display = XOpenDisplay(NULL);
	Window root = DefaultRootWindow(display);

	XImage *image = XGetImage(display,root, xx,yy, W,H, AllPlanes, ZPixmap);
	XCloseDisplay(display);
	
	unsigned char *ptr = image->data;
	unsigned char *rgb;
	int bpl = image->bytes_per_line;
	int x, y, i = 0;
	
	for (y = 0; y < H; y++) {
		for (x = 0; x < W; x++) {
			rgb = ptr + (y * bpl + 4 * x);
			
			data[i++] = rgb[2];
			data[i++] = rgb[1];
			data[i++] = rgb[0];
		}
	}

	XFree(image);
}
