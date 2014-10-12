#ifndef __OPENGL_GRAPHICS_H__
#define __OPENGL_GRAPHICS_H__


#include "circular_4_buf.h"


void g_draw_circle(double x, double y, double z,
                   double radius, int segments);

void g_draw_filled_circle(
                   double x, double y, double z,
                   double radius, int segments);

void g_draw_tail(Circular4Buf* buf, double duration, 
                   float r, float g, float b,
                   float alpha_head, float alpha_tail);

void g_draw_filled_vec_triangle(
                   double x, double y, double z,
                   double dx, double dz,
                   double h, double sideangle,
                   double r, double g, double b, double a);

void g_draw_filled_triangle(
                   double x, double y, double z, 
                   double radius, double direction, double sideangle,
                   double r, double g, double b, double a);

void g_draw_grid(int x_tiles, int y_tiles, double tile_size);


#endif // __OPENGL_GRAPHICS_H__
