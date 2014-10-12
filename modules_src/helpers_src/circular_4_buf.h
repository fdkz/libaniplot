#ifndef __CIRCULAR_4_BUF_H__
#define __CIRCULAR_4_BUF_H__


#include "circular_buffer_t.h"


struct coord4
{
    double x, y, z, t;
};


class Circular4Buf: public circular_buffer_t<coord4>
{
public:
    Circular4Buf(int capacity): circular_buffer_t<coord4>(capacity) {}
};


#endif // __CIRCULAR_4_BUF_H__
