// almost a little joke :)
// macosx: gcc mip_buf_test.cpp mip_buf_renderer.cpp -lstdc++ -framework OpenGL

#include "mip_buf_t.h"
#include "mip_buf_renderer.h"
#include <stdio.h>


int main()
{
    printf("hello\n");

    pool_t<int> p;
    printf("testing\n");
    //p.test();

    printf("tested\n");
    //return 0;

    MipBuf_t<float> m;

    m.append(1, 2, 3);
    m.append(1, 2, 3);
    m.append(1, 2, 3);
    m.append(1, 2, 3);
    m.append(1, 2, 3);

    MipBuf_t<float>* buf;
    float start_pixel;
    int   start_index;
    float end_pixel;
    int   end_index;

    m.get_buf(
            1, 10, 10,
            &buf,
            &start_pixel, &start_index,
            &end_pixel,   &end_index);

    printf("start_pixel %.2f start_index %i end_pixel %.2f end_index %i\n",
        start_pixel, start_index, end_pixel, end_index);


    MipBufRenderer r;

    for (int i = 0; i < 100000; i++)
        r.append(1,2,3);

    r.get(1);

    printf("tests passed\n");
    return 0;
}
