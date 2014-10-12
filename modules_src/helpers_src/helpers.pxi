#
# c++
#


cdef extern from "circular_4_buf.h":

    struct cpp_coord4 "coord4":
        double x
        double y
        double z
        double t


cdef extern from "circular_4_buf.h":

    struct cpp_Circular4Buf "Circular4Buf":
        int (*show)(char* s)

        void (*set_capacity)(int capacity)
        void (*clear)()

        cpp_coord4* (*append)()

        # -1 is last. 0 is first, the eldest (oldest?)
        cpp_coord4* (*get)(int i)

        int  (*change_counter)()
        void (*add_change_counter)()

        int  (*capacity)()
        int  (*size)()

    void delete "delete " (void *o)
    cpp_Circular4Buf* new_Circular4Buf "new Circular4Buf" (int capacity)


cdef class Circular4Buf:

    cdef cpp_Circular4Buf* instance

    def __cinit__(self, int capacity):
        #print "msg circbuf4 pyx creation"
        self.instance = new_Circular4Buf(capacity)

    def __dealloc__(self):
        #print "msg circbuf4 pyx destruction"
        delete(self.instance)


    def set_capacity(self, int capacity):
        """ everything inside will be destroyed """
        self.instance.set_capacity(capacity)

    def clear(self):
        self.instance.clear()

    def append(self, double x, double y, double z, double t):
        cdef cpp_coord4* c4
        c4 = self.instance.append()
        c4.x = x
        c4.y = y
        c4.z = z
        c4.t = t

    def append_vect(self, xyz_list, double t):
        cdef cpp_coord4* c4
        c4 = self.instance.append()
        c4.x = xyz_list[0]
        c4.y = xyz_list[1]
        c4.z = xyz_list[2]
        c4.t = t

    def get(self, i):
        cdef cpp_coord4* c4
        c4 = self.instance.get(i)
        if not c4: raise IndexError, "Circular4Buf index out of range"
        return c4.x, c4.y, c4.z, c4.t

    def capacity(self):
        return self.instance.capacity()

    def size(self):
        return self.instance.size()


    def change_counter(self):
        """
        append() and clear() will increment this. will be zero after creation.
        nothing can reset it.
        """
        return self.instance.change_counter()

    def add_change_counter(self):
        self.instance.add_change_counter()


#
# c
#


cdef extern from "opengl_graphics.h":
    #int c_g_show "g_show" (char* s)

    void g_draw_circle(double x, double y, double z,                      \
                       double radius, int segments)

    void g_draw_filled_circle(                                            \
                       double x, double y, double z,                      \
                       double radius, int segments)

    void g_draw_tail(cpp_Circular4Buf* buf, double duration,              \
                       float r, float g, float b,                         \
                       float alpha_head, float alpha_tail)

    void g_draw_filled_vec_triangle(                                      \
                       double x, double y, double z,                      \
                       double dx, double dz,                              \
                       double h, double sideangle,                        \
                       double r, double g, double b, double a)

    void g_draw_filled_triangle(                                          \
                       double x, double y, double z,                      \
                       double radius, double direction, double sideangle, \
                       double r, double g, double b, double a)

    void g_draw_grid(int x_tiles, int y_tiles, double tile_size)



def draw_circle(double x, double y, double z, double radius, int segments):
    g_draw_circle(x, y, z, radius, segments)

def draw_filled_circle(double x, double y, double z, double radius, int segments):
    g_draw_filled_circle(x, y, z, radius, segments)

def draw_tail(Circular4Buf buf, double duration, float r, float g, float b, float alpha_head, float alpha_tail):
    g_draw_tail(buf.instance, duration, r, g, b, alpha_head, alpha_tail)

def draw_filled_triangle(double x, double y, double z, double radius, double direction, double sideangle, double r = 0., double g = 0., double b = 0., double a = 1.):
    g_draw_filled_triangle(x, y, z, radius, direction, sideangle, r, g, b, a)

def draw_filled_vec_triangle(double x, double y, double z, double dx, double dz, double h, double sideangle, double r = 0., double g = 0., double b = 0., double a = 1.):
    g_draw_filled_vec_triangle(x, y, z, dx, dz, h, sideangle, r, g, b, a)

def draw_grid(int x_tiles, int y_tiles, double tile_size):
    g_draw_grid(x_tiles, y_tiles, tile_size)
