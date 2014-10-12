#include "mip_buf_renderer.h"

#include <assert.h>
#include <stdio.h>

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


#ifndef M_PI
    #define M_PI 3.1415926535897
#endif


// --------------------------------------------------------------------------
// ---- LIFECYCLE -----------------------------------------------------------
// --------------------------------------------------------------------------


MipBufRenderer::MipBufRenderer()
{
}


MipBufRenderer::~MipBufRenderer()
{
}


// --------------------------------------------------------------------------
// ---- METHODS -------------------------------------------------------------
// --------------------------------------------------------------------------


// TODO: use vertex buffers

void MipBufRenderer::render_avg(float start_index, float end_index, float resolution)
{
    MipBuf_t<float>* buf;
    float _start_pixel;
    int   _start_index;
    float _end_pixel;
    int   _end_index;

    m_mip_buf.get_buf(
            start_index, end_index, resolution,
            &buf,
            &_start_pixel, &_start_index,
            &_end_pixel,   &_end_index);

    // have to have at least 2 elements
    if (_end_index - _start_index <= 0)
        return;

    float d = float(_end_pixel - _start_pixel) / (_end_index - _start_index);
    float k = 0.;

    MipBufEntry<float>* e;

    glPushMatrix();
    glTranslatef(_start_pixel, 0., 0.);
    glScalef(d, 1., 1.);

    glBegin(GL_LINE_STRIP);

    for (int i = _start_index; i <= _end_index; i++)
    {
        e = buf->get(i);
        if (!e)
        {
            printf("ERROR: start_index %i end_index %i i %i k %.2f\n", _start_index, _end_index, i, k);
        }
        assert(e);
        glVertex3f(k, e->avg, 0.);
        k++;
    }

    glEnd();
    glPopMatrix();
}


void MipBufRenderer::render_minmax(float start_index, float end_index, float resolution)
{
    MipBuf_t<float>* buf;
    float _start_pixel;
    int   _start_index;
    float _end_pixel;
    int   _end_index;

    m_mip_buf.get_buf(
            start_index, end_index, resolution,
            &buf,
            &_start_pixel, &_start_index,
            &_end_pixel,   &_end_index);

    // have to have at least 2 elements
    if (_end_index - _start_index <= 0)
        return;

    float d = float(_end_pixel - _start_pixel) / (_end_index - _start_index);
    float k = 0.;

    MipBufEntry<float>* e;

    glPushMatrix();
    glTranslatef(_start_pixel, 0., 0.);
    glScalef(d, 1., 1.);

    glBegin(GL_LINES);

    for (int i = _start_index; i <= _end_index; i++)
    {
        e = buf->get(i);
        if (!e)
        {
            printf("ERROR: start_index %i end_index %i i %i k %.2f\n", _start_index, _end_index, i, k);
        }
        assert(e);
        glVertex3f(k, e->minval, 0.);
        glVertex3f(k, e->maxval, 0.);
        k++;
    }

    glEnd();
    glPopMatrix();
}


void MipBufRenderer::append(float avg)
{
    m_mip_buf.append(avg);
}

void MipBufRenderer::append_minmaxavg(float minval, float maxval, float avg)
{
    m_mip_buf.append_minmaxavg(minval, maxval, avg);
}


MipBufEntry<float>* MipBufRenderer::get(int i)
{
    return m_mip_buf.get(i);
}


int MipBufRenderer::size()
{
    return m_mip_buf.m_buf.size();
}


int MipBufRenderer::get_change_counter()
{
    return m_mip_buf.m_buf.get_change_counter();
}


void MipBufRenderer::inc_change_counter()
{
    m_mip_buf.m_buf.inc_change_counter();
}


// --------------------------------------------------------------------------
// ---- PRIVATE -------------------------------------------------------------
// --------------------------------------------------------------------------

