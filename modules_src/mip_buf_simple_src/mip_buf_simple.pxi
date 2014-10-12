#
# c++
#

#
# modified/simplified version of the same file under mip_buf_src. this
# version has no minval/maxval support, and accepts only unsigned char data.
#

cdef extern from "mip_buf_simple_renderer.h":

    struct cpp_MipBufSimpleEntry "MipBufSimpleEntry<unsigned char>":
        unsigned char avg

    struct cpp_MipBufSimpleRenderer "MipBufSimpleRenderer":
        void  (*append)(unsigned char avg)
        void  (*render_avg)(float start_index, float end_index, float resolution)
        cpp_MipBufSimpleEntry* (*get)(int i)
        int   (*size)()
        int   (*get_change_counter)()
        void  (*inc_change_counter)()

    void delete "delete " (void *o)
    cpp_MipBufSimpleRenderer* new_MipBufSimpleRenderer "new MipBufSimpleRenderer" ()


cdef class MipBufSimpleRenderer:

    cdef cpp_MipBufSimpleRenderer* instance

    def __cinit__(self):
        #print "msg MipBufSimpleRenderer creation"
        self.instance = new_MipBufSimpleRenderer()

    def __dealloc__(self):
        #print "msg MipBufSimpleRenderer destruction"
        delete(self.instance)


    def append(self, unsigned char avg):
        self.instance.append(avg)

    def render_avg(self, float start_index, float end_index, float resolution):
        self.instance.render_avg(start_index, end_index, resolution)

    def get(self, i):
        cdef cpp_MipBufSimpleEntry* e
        e = self.instance.get(i)
        if not e:
            raise IndexError, "MipBufSimpleRenderer index out of range"
        return e.avg, e.avg, e.avg

    def size(self):
        return self.instance.size()


    def get_change_counter(self):
        """
        append() and clear() will increment this. will be zero after creation.
        nothing can reset it.
        """
        return self.instance.get_change_counter()

    def inc_change_counter(self):
        self.instance.inc_change_counter()
