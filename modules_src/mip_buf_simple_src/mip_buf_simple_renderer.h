#ifndef __MIP_BUF_SIMPLE_RENDERER_H__
#define __MIP_BUF_SIMPLE_RENDERER_H__

//
// modified/simplified version of the same file under mip_buf_src. this
// version has no minval/maxval support, and accepts only unsigned char data.
//

#include "mip_buf_simple_t.h"


// MipBuf and renderer combined.
// wrapper class to simplify python integration.

class MipBufSimpleRenderer
{
public:
    MipBufSimpleRenderer();
    ~MipBufSimpleRenderer();

    // end_index NOT one past last. end_index points to a real entry.
    void render_avg(float start_index, float end_index, float resolution);
    void append(unsigned char avg);
    int  size();
    int  get_change_counter();
    void inc_change_counter();
    MipBufSimpleEntry<unsigned char>* get(int i);

private:
    MipBufSimple_t<unsigned char> m_mip_buf;
};


#endif // __MIP_BUF_SIMPLE_RENDERER_H__
