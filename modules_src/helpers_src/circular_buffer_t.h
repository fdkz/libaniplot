#ifndef __CIRCULAR_BUFFER_T_H__
#define __CIRCULAR_BUFFER_T_H__


#include <assert.h>

#ifndef NULL
#define NULL 0
#endif


//
// no pop()
//


template<class T>
class circular_buffer_t
{
public:

    circular_buffer_t(int capacity = 0);
    ~circular_buffer_t();


    // everything inside will be destroyed
    void set_capacity(int capacity);
    void clear();

    void append(T& item);
    void appendval(T item); // so you can do: append(1234)
    // be VERY careful with this. you have to clear the object yourself.
    T*   append();

    // -1 is last. 0 is first, the eldest (oldest?)
    T*   get(int i);

    // append() and clear() will increment this. will be zero after creation.
    // nothing can reset it.
    int  change_counter();
    void add_change_counter();

    int  capacity();
    int  size();


    // execute some internal tests. lifesavers while developing this class.
    void test();


protected:

    int  m_capacity;
    int  m_change_counter;
    int  m_head; // one past last (youngest)
    int  m_size;

    T*   m_buffer;

    // index to m_buffer. return -1 if i is out of bounds
    inline int m_index(int i) const;
};


// --------------------------------------------------------------------------
// ---- LIFECYCLE -----------------------------------------------------------
// --------------------------------------------------------------------------


template<class T>
circular_buffer_t<T>::circular_buffer_t(int capacity)
{
    m_capacity       = 0;
    m_change_counter = 0;
    m_head           = 0;
    m_size           = 0;
    m_buffer         = 0;

    set_capacity(capacity);
}


template<class T>
circular_buffer_t<T>::~circular_buffer_t()
{
    delete [] m_buffer;
}


// --------------------------------------------------------------------------
// ---- METHODS -------------------------------------------------------------
// --------------------------------------------------------------------------


template<class T>
void circular_buffer_t<T>::set_capacity(int capacity)
{
    assert(capacity > 0);
    delete [] m_buffer;
    m_capacity = capacity;
    m_buffer   = new T[m_capacity];
    clear();
}


template<class T>
void circular_buffer_t<T>::clear()
{
    //memset(m_buffer, 0, sizeof(T) * m_capacity);
    m_size = 0;
    m_head = 0;
    m_change_counter++;
}


template<class T>
void circular_buffer_t<T>::append(T& item)
{
    m_buffer[m_head] = item;
    //m_head = m_index(m_head + 1);

    m_head++;
    if (m_head >= m_capacity) m_head = 0;
    if (m_size  < m_capacity) m_size++;

    m_change_counter++;
}


template<class T>
void circular_buffer_t<T>::appendval(T item)
{
    append(item);
}


template<class T>
T* circular_buffer_t<T>::append()
{
    int head = m_head;

    m_head++;
    if (m_head >= m_capacity) m_head = 0;
    if (m_size  < m_capacity) m_size++;

    m_change_counter++;

    return &m_buffer[head];
}


template<class T>
T* circular_buffer_t<T>::get(int i)
{
    int r = m_index(i);
    if (r < 0) return NULL;

    return &m_buffer[r];
}


template<class T>
int circular_buffer_t<T>::change_counter()
{
    return m_change_counter;
}


template<class T>
void circular_buffer_t<T>::add_change_counter()
{
    m_change_counter++;
}


template<class T>
int circular_buffer_t<T>::capacity()
{
    return m_capacity;
}


template<class T>
int circular_buffer_t<T>::size()
{
    return m_size;
}


/*
// start_time & end_time - timestamps in this TargetFrameBuffer..
// not the real time. check the timestamp.. may not be start_time
// or end_time.
// (both ends are inclusive)
void TargetFrameBuffer::get_slice_indices(
    double start_time,  double end_time,
    int*   start_index, int*   end_index)
{
    // we start from the end because the tail could be god-knows how long, and
    // usually we need some newer pieces anyway.

    int end_i = size() - 1;
    *end_index   = -1;
    *start_index = 0;

    // TODO: use m_fast_index here. no asserts needed

    // find the index of the last element
    if (end_i == -1) return; // we are empty :(

    while (end_i >= 0 && m_frame_buffer[m_index(end_i)].timestamp > end_time)
        end_i--;
    if (end_i == -1) return; // requested too old stuff

    // find the index of the first element
    int start_i = end_i;
    while (start_i >= 0 && m_frame_buffer[m_index(start_i)].timestamp >=
           start_time) start_i--;
    start_i++;

    *start_index = start_i;
    *end_index   = end_i;
}


// return true if exists
// returns the first equal or smaller time-point
bool TargetFrameBuffer::get_time_index(double time, int* index)
{
    int i = size() - 1;
    *index   = -1;
    if (i == -1) return false;

    while (i >= 0 && m_frame_buffer[m_index(i)].timestamp > time) i--;
    if (i == -1) return false; // requested too old stuff

    *index = i;
    return true;
}
*/


template<class T>
void circular_buffer_t<T>::test()
{
    circular_buffer_t<int> b(7);

    b.appendval(11);
    b.appendval(12);
    assert(b.size() == 2);
    b.appendval(13);
    b.appendval(14);
    b.appendval(15);
    b.appendval(16);
    b.appendval(17);
    assert(b.size() == 7);
    b.appendval(18);
    b.appendval(19);
    assert(b.size() == 7);

    assert(b.get(0)  != NULL && *b.get(0)  == 13);
    assert(b.get(-1) != NULL && *b.get(-1) == 19);
    assert(b.get(-7) != NULL && *b.get(-7) == 13);
    assert(b.get(-8) == NULL);
    assert(b.get(7)  == NULL);


    circular_buffer_t<int> c;
    assert(c.size() == 0);
    c.appendval(11);
    c.appendval(12);
    assert(b.get(0)  == NULL);
    assert(b.get(1)  == NULL);
    assert(b.get(-1) == NULL);


    // all tests passed

    //
    // in circular_buffer_t:m_index(int i) :
    //
    // capacity  head  size  i  r
    //    10      4     4    0  0
    //    10      4     4    3  3
    //    10      4     4    4 -1
    //    10      2     4    0  8
    //    10      2     4    3  1
}


// --------------------------------------------------------------------------
// ---- PRIVATE -------------------------------------------------------------
// --------------------------------------------------------------------------


template<class T>
int circular_buffer_t<T>::m_index(int i) const
{
    int r;

    if (i >= 0)
    {
        if (i >= m_size) return -1;
        r = m_head - m_size + i;
    }
    else
    {
        if (-i > m_size) return -1;
        r = m_head + i;
    }
    if (r < 0) r += m_size;
    
    return r;

    // this line works only in python.
    // % with negatives is a bit different there
    // r = (m_head - m_size + i) % m_capacity;
    // TODO: which is faster
    // this    : r = (m_head + i) % m_capacity;
    // or this : r = m_head + i; if (r < 0) r += m_size;
}


#endif // __CIRCULAR_BUFFER_T_H__
