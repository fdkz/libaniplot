#include "opengl_graphics.h"


//extern "C"
//{
#if defined(WIN32)
    #include <windows.h>
    #include <GL/gl.h>
    #include <GL/glu.h>
#elif defined(__APPLE__)
    #include <OpenGL/gl.h>
    #include <OpenGL/glu.h>
#else // linux
    #include <GL/gl.h>
    #include <GL/glu.h>
#endif
//}

#include <cmath>


#include "circular_4_buf.h"


#ifndef M_PI
    #define M_PI 3.1415926535897
#endif


void g_draw_circle(double x, double y, double z, double radius, int segments)
{
    double segment_radians = 360. / segments * M_PI / 180.;

    glBegin(GL_LINE_LOOP);
    for (double i = 0; i < segments; ++i)
    {
        double radians = segment_radians * i;
        double dx = radius * sin(radians);
        double dz = radius * cos(radians);
        glVertex3d(x + dx, y, z + dz);
    }
    glEnd();
}


void g_draw_filled_circle(double x, double y, double z, double radius, int segments)
{
    double segment_radians = 360. / segments * M_PI / 180.;

    // TODO: midpoint? one missing segment?

    glBegin(GL_TRIANGLE_FAN);
    for (double i = 0; i < segments; ++i)
    {
        double radians = segment_radians * i;
        double dx = radius * sin(radians);
        double dz = radius * cos(radians);
        glVertex3d(x + dx, y, z + dz);
    }
    glEnd();
}


//
// draw the tail.
// starting from head, going back to t seconds.
// t values inside buf have to be timestamps in seconds.
//
void g_draw_tail(Circular4Buf* buf, double duration,
                   float r, float g, float b,
                   float alpha_head, float alpha_tail)
{
    if (buf->size() < 2) return;

    // DAMN how complicated... how hard can it be?!?

    int     i     = -1;
    coord4* c4    = buf->get(-1);
    double  t     = c4->t;
    double  t_end = t;
    double  a;

    if (t_end - buf->get(-2)->t > duration) return;

    glBegin(GL_LINE_STRIP);

    do
    {
        t = c4->t;
        a = alpha_head + (alpha_tail - alpha_head) * (t_end - t) / duration;
        glColor4d(r, g, b, a);
        glVertex3d(c4->x, c4->y, c4->z);

        i--;
        c4 = buf->get(i);
    }
    while (c4 && t_end - c4->t <= duration);

    assert(i < -2);

    glEnd();
}


void g_draw_filled_vec_triangle(
                   double x, double y, double z,
                   double dx, double dz,
                   double h, double sideangle,
                   double r, double g, double b, double a)
{
    // primitive error-checking
    if (sideangle >= 90.f || sideangle <= -90.f) return;

    double a1 = atan2(dx, dz);
    double a2 = a1 - sideangle * M_PI / 180.;
    double a3 = a1 + sideangle * M_PI / 180.;
    double radius = h / cos(sideangle * M_PI / 180.);

    double x1 = x + radius * sin(a2);
    double z1 = z + radius * cos(a2);
    double x2 = x + radius * sin(a3);
    double z2 = z + radius * cos(a3);

    glBegin(GL_TRIANGLES);
    glVertex3d(x,  y, z);
    glVertex3d(x1, y, z1);
    glVertex3d(x2, y, z2);
    glEnd();

    // antialiased edge

    glColor4d(r, g, b, a);

    glBegin(GL_LINE_LOOP);
    glVertex3d(x,  y, z );
    glVertex3d(x1, y, z1);
    glVertex3d(x2, y, z2);
    glEnd();
}


// r, g, b, a - edge color
void g_draw_filled_triangle(
                   double x, double y, double z,
                   double radius, double direction, double sideangle,
                   double r, double g, double b, double a)
{
    double a1 = direction * M_PI / 180.;
    double a2 = a1 + sideangle * M_PI / 180.;
    double a3 = a1 - sideangle * M_PI / 180.;

    double x1 = x + radius * sin(a1);
    double z1 = z + radius * cos(a1);
    double x2 = x + radius * sin(a2);
    double z2 = z + radius * cos(a2);
    double x3 = x + radius * sin(a3);
    double z3 = z + radius * cos(a3);

    glBegin(GL_TRIANGLES);
    glVertex3d(x1, y, z1);
    glVertex3d(x2, y, z2);
    glVertex3d(x3, y, z3);
    glEnd();

    // antialiased edge

    glColor4d(r, g, b, a);

    glBegin(GL_LINE_LOOP);
    glVertex3d(x1, y, z1);
    glVertex3d(x2, y, z2);
    glVertex3d(x3, y, z3);
    glEnd();
}


void g_draw_grid(int x_tiles, int y_tiles, double tile_size)
{
    glBegin(GL_LINES);

    // x-axis
    for (int i = 0; i < x_tiles + 1; ++i)
    {
        double w2 = x_tiles * tile_size / 2.;
        glVertex3d( i * tile_size - w2, 0.,  w2);
        glVertex3d( i * tile_size - w2, 0., -w2);
    }

    // y-axis
    for (int i = 0; i < y_tiles + 1; ++i)
    {
        double w2 = y_tiles * tile_size / 2.f;
        glVertex3d( -w2, 0., i * tile_size - w2);
        glVertex3d(  w2, 0., i * tile_size - w2);
    }

    glEnd();
}
