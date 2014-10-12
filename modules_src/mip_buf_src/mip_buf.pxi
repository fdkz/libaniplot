#
# c++
#


cdef extern from "mip_buf_renderer.h":

    struct cpp_MipBufEntryFloat "MipBufEntry<float>":
        float minval
        float maxval
        float avg

    struct cpp_MipBufRenderer "MipBufRenderer":
        void  (*append)(float avg)
        void  (*append_minmaxavg)(float minval, float maxval, float avg)
        void  (*render_avg)(float start_index, float end_index, float resolution)
        void  (*render_minmax)(float start_index, float end_index, float resolution)
        cpp_MipBufEntryFloat* (*get)(int i)
        int   (*size)()
        int   (*get_change_counter)()
        void  (*inc_change_counter)()

    void delete "delete " (void *o)
    cpp_MipBufRenderer* new_MipBufRenderer "new MipBufRenderer" ()


cdef class MipBufRenderer:

    cdef cpp_MipBufRenderer* instance

    def __cinit__(self):
        #print "msg MipBufRenderer pyx creation"
        self.instance = new_MipBufRenderer()

    def __dealloc__(self):
        #print "msg MipBufRenderer pyx destruction"
        delete(self.instance)


    def append(self, float avg):
        self.instance.append(avg)

    def append_minmaxavg(self, float minval, float maxval, float avg):
        self.instance.append_minmaxavg(minval, maxval, avg)

    def render_avg(self, float start_index, float end_index, float resolution):
        self.instance.render_avg(start_index, end_index, resolution)

    def render_minmax(self, float start_index, float end_index, float resolution):
        self.instance.render_minmax(start_index, end_index, resolution)

    def get(self, i):
        """ return (minval, maxval, avg) of the sample at index i """
        cdef cpp_MipBufEntryFloat* e
        e = self.instance.get(i)
        if not e:
            raise IndexError, "MipBufRenderer index out of range"
        return e.minval, e.maxval, e.avg

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
