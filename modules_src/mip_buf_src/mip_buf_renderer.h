#ifndef __MIP_BUF_RENDERER_H__
#define __MIP_BUF_RENDERER_H__


#include "mip_buf_t.h"


// MipBuf and renderer combined.
// wrapper class to simplify python integration.

class MipBufRenderer
{
public:
    MipBufRenderer();
    ~MipBufRenderer();

    // end_index NOT one past last. end_index points to a real entry.
    void render_avg(float start_index, float end_index, float resolution);
    // renders a solid column, not two separate lines.
    void render_minmax(float start_index, float end_index, float resolution);
    // same as append_minmaxavg, but minval and maxval will be equal to avg.
    void append(float avg);
    void append_minmaxavg(float minval, float maxval, float avg);
    // return num of elements appended. memory consumption is a little bit
    // more than for twice as much elements because of the 'mipmapping'. 
    int  size();
    int  get_change_counter();
    void inc_change_counter();
    MipBufEntry<float>* get(int i);

private:
    MipBuf_t<float> m_mip_buf;
};


#endif // __MIP_BUF_RENDERER_H__
