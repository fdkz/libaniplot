#ifndef __MIP_BUF_T_H__
#define __MIP_BUF_T_H__

//
// example:
//
//   8 values appended:
//
//   -------------------------------------------------------------------
//          append()
//             |
//            buf0          buf1          buf2          buf3
//         avg min max   avg min max   avg min max   avg min max
//    0     25  25  25    30  25  35    40  25  60    28   5  60
//    1     35  35  35    50  40  60    16   5  30
//    2     40  40  40    20  10  30
//    3     60  60  60    12   5  19
//    4     10  10  10
//    5     30  30  30
//    6     19  19  19
//    7      5   5   5
//   -------------------------------------------------------------------
//
//   buf1 holds the average of buf0, and so on. 
//
//   buf0, buf1, bufx is chosen by the get_buf method depending on the wanted
//   resolution. get_buf chooses the most optimal buf object, in that it tries
//   to keep one buf entry per pixel. for example if you want to render these
//   eight values on a 4 pixel wide window, then get_buf will return buf1.
//   (note that on a 5 pixel wide window it will return buf0)
//
//   each buf entry has in addition to the appended sample value also minval
//   and maxval. those are not averaged for each next buf level, but instead
//   smallest of the two minval's and largest of maxval's will be selected.
//

#include "math.h"


#include "pool_t.h"


#define MIP_MIN(X,Y) ((X) < (Y) ? (X) : (Y))
#define MIP_MAX(X,Y) ((X) > (Y) ? (X) : (Y))


template<class T>
struct MipBufEntry
{
    MipBufEntry(T _minval, T _maxval, T _avg): minval(_minval), maxval(_maxval), avg(_avg) {}
    T minval;
    T maxval;
    T avg;
};


template<class T>
class MipBuf_t
{
public:
    MipBuf_t();
    ~MipBuf_t();

    void append(T avg);
    void append_minmaxavg(T minval, T maxval, T avg);

    void get_buf(
            float start_index, float end_index, float resolution,
            MipBuf_t** out_buf,
            float* out_start_pixel, int* out_start_index,
            float* out_end_pixel,   int* out_end_index);

    MipBufEntry<T>* get(int i);

    pool_t<MipBufEntry<T> > m_buf;

private:

    MipBuf_t* m_child;
};


// --------------------------------------------------------------------------
// ---- LIFECYCLE -----------------------------------------------------------
// --------------------------------------------------------------------------


template<class T>
MipBuf_t<T>::MipBuf_t(): m_buf(20000, 2000)
{
    m_child = NULL;
}


template<class T>
MipBuf_t<T>::~MipBuf_t()
{
    delete m_child;
}


// --------------------------------------------------------------------------
// ---- METHODS -------------------------------------------------------------
// --------------------------------------------------------------------------


template<class T>
inline void MipBuf_t<T>::append(T avg)
{
    append_minmaxavg(avg, avg, avg);
}


template<class T>
void MipBuf_t<T>::append_minmaxavg(T minval, T maxval, T avg)
{
    MipBufEntry<T>* e = m_buf.append();
    e->minval = minval;
    e->maxval = maxval;
    e->avg    = avg;

    if ((m_buf.size() & 1) == 0)
    {
        if (!m_child)
            m_child = new MipBuf_t<T>();
        MipBufEntry<T>* e1 = m_buf.get(-2);
        MipBufEntry<T>* e2 = m_buf.get(-1);
        // TODO: avg1 + avg2 overflow if unsigned char?
        m_child->append_minmaxavg(MIP_MIN(e1->minval, e2->minval), MIP_MAX(e1->maxval, e2->maxval), (e1->avg + e2->avg) / 2.);
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
void MipBuf_t<T>::get_buf(
        float start_index, float end_index, float resolution,
        MipBuf_t** out_buf,
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
MipBufEntry<T>* MipBuf_t<T>::get(int i)
{
    return m_buf.get(i);
}


#endif // __MIP_BUF_T_H__
