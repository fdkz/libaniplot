#ifndef __MIP_BUF_SIMPLE_T_H__
#define __MIP_BUF_SIMPLE_T_H__


//
// modified/simplified version of the same file under mip_buf_src. this
// version has no minval/maxval support, and accepts only unsigned char data.
//


#include "math.h"


#include "pool_t.h"


#define MIP_MIN(X,Y) ((X) < (Y) ? (X) : (Y))
#define MIP_MAX(X,Y) ((X) > (Y) ? (X) : (Y))


template<class T>
struct MipBufSimpleEntry
{
    MipBufSimpleEntry(T _avg): avg(_avg) {}
    T avg;
};


template<class T>
class MipBufSimple_t
{
public:
    MipBufSimple_t();
    ~MipBufSimple_t();

    void append(T avg);

    void get_buf(
            float start_index, float end_index, float resolution,
            MipBufSimple_t** out_buf,
            float* out_start_pixel, int* out_start_index,
            float* out_end_pixel,   int* out_end_index);

    MipBufSimpleEntry<T>* get(int i);

    pool_t<MipBufSimpleEntry<T> > m_buf;

private:

    MipBufSimple_t* m_child;
};


// --------------------------------------------------------------------------
// ---- LIFECYCLE -----------------------------------------------------------
// --------------------------------------------------------------------------


template<class T>
MipBufSimple_t<T>::MipBufSimple_t(): m_buf(20000, 2000)
{
    m_child = NULL;
}


template<class T>
MipBufSimple_t<T>::~MipBufSimple_t()
{
    delete m_child;
}


// --------------------------------------------------------------------------
// ---- METHODS -------------------------------------------------------------
// --------------------------------------------------------------------------


template<class T>
void MipBufSimple_t<T>::append(T avg)
{
    MipBufSimpleEntry<T>* e = m_buf.append();
    e->avg = avg;

    if ((m_buf.size() & 1) == 0)
    {
        if (!m_child)
            m_child = new MipBufSimple_t<T>();
        MipBufSimpleEntry<T>* e1 = m_buf.get(-2);
        MipBufSimpleEntry<T>* e2 = m_buf.get(-1);
        unsigned char childavg = ((float)e1->avg + e2->avg) / 2.;
        m_child->append(childavg);
    }
}


// out_start_pixel and start_index always go in pairs,
// as do out_end_pixel and end_index.
//
// "resolution" here is a strange parameter.
// for example if it's 1, out_start_pixel and out_end_pixel will be 0 and 1,
// seemingly taking 2 pixels. but actually the space between pixels 0 and 1 will
// be 1 pixel wide.
//
// start_index and end_index treat the samples as a continuous line. 0..1) is first sample,
// 1..2) is second sample and so on.
// out_start_index and out_end_index are traditional sample indices.
template<class T>
void MipBufSimple_t<T>::get_buf(
        float start_index, float end_index, float resolution,
        MipBufSimple_t** out_buf,
        float* out_start_pixel, int* out_start_index,
        float* out_end_pixel,   int* out_end_index)
{
    // sanity check
    if (end_index <= start_index || resolution <= 0.1)
    {
        *out_buf = this;
        *out_start_pixel = 0;
        *out_start_index = 0;
        *out_end_pixel   = 0;
        *out_end_index   = 0;
    }

    // mathematically not exactly what it says.
    float samples_per_pixel = (end_index - start_index) / resolution;
    float pixels_per_sample = resolution / (end_index - start_index);

    if (samples_per_pixel >= 2. && m_child && (end_index - start_index) >= 4. + 1.)
    {
         // too much resolution. get child buf.
        m_child->get_buf(start_index / 2., end_index / 2., resolution,
                out_buf, out_start_pixel, out_start_index, out_end_pixel, out_end_index);
    }
    else
    {
        int i_start = round(start_index);
        int i_end   = round(end_index) - 1;

        if (i_start < 0)
            i_start = 0;

        if (i_end >= m_buf.size())
            i_end = m_buf.size() - 1;

        *out_start_pixel = (i_start + 0.5 - start_index) * pixels_per_sample;
        *out_end_pixel   = resolution - (end_index - i_end - 0.5) * pixels_per_sample;

        *out_start_index = i_start;
        *out_end_index   = i_end;

        //if (*out_end_pixel <= *out_start_pixel)
        //    printf("ERROR: out_start_pixel %.4f out_end_pixel %.4f start_index %.4f end_index %.4f i_start %i i_end %i mbufsize %i\n",
        //            *out_start_pixel, *out_end_pixel, start_index, end_index, i_start, i_end, m_buf.size());

        *out_buf = this;
    }
}


template<class T>
MipBufSimpleEntry<T>* MipBufSimple_t<T>::get(int i)
{
    return m_buf.get(i);
}


#endif // __MIP_BUF_SIMPLE_T_H__
