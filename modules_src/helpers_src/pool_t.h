#ifndef __POOL_T_H__
#define __POOL_T_H__

//
// example with parameters:
//
//     ptrbuf_elements  = 3
//     segment_elements = 4
//     and 18 items appended
//
//   ----------------------------------------------------------
//   ptrbuf0                             ptrbuf1
//
//     segment0   segment1   segment2      segment3   segment4
//
//      item0      item4      item8         item12     item16
//      item1      item5      item9         item13     item17
//      item2      item6      item10        item14
//      item3      item7      item11        item15
//   ----------------------------------------------------------
//
//   the pool is a linked list of ptrbuf's.
//   each ptrbuf is an array of segments.
//   each segment is an array of items.
//

#include <string.h> // memset
#include <assert.h>

#include <stdio.h>


struct pool_dummy_t { int dummy; };


template<class T>
class pool_t
{
public:

    pool_t(int segment_elements=20000, int ptrbuf_elements=2000);
    ~pool_t();

    // everything inside will be destroyed
    void clear();

    void append(T& item);
    // be VERY careful with this. you have to clear the object yourself.
    T*   append();

    // -size..size-1. 0 is the first one appended. -1 is the last element.
    T*   get(int i);

    // TODO: iterator logic. implement get_next and get_prev.
    // append() and clear() will increment this. will be zero after creation.
    // nothing can reset it.
    int  get_change_counter();
    void inc_change_counter();

    int  size();


    // execute some internal tests. lifesavers while developing this class.
    void test();


protected:

    int   m_size;
    int   m_change_counter;
    int   m_PTRBUF_ELEMENTS;
    int   m_SEGMENT_ELEMENTS;

    // first PTRBUF_ELEMENTS entries point to SEGMENT_ELEMENTS buffers of T.
    // the last pointer makes a linked list to next ptrbuf, if needed.
    // so the size of m_ptrbuf is PTRBUF_ELEMENTS + 1 pointers.
    pool_dummy_t** m_ptrbuf;

    void* m_create_ptrbuf();
    void* m_get_ptrbuf(int n);
    void  m_release_ptrbuf(void* ptrbuf);
};


// --------------------------------------------------------------------------
// ---- LIFECYCLE -----------------------------------------------------------
// --------------------------------------------------------------------------


template<class T>
pool_t<T>::pool_t(int segment_elements, int ptrbuf_elements)
{
    m_size             = 0;
    m_change_counter   = 0;
    m_PTRBUF_ELEMENTS  = ptrbuf_elements;
    m_SEGMENT_ELEMENTS = segment_elements;
    m_ptrbuf           = 0;
}


template<class T>
pool_t<T>::~pool_t()
{
    m_release_ptrbuf(m_ptrbuf);
}


// --------------------------------------------------------------------------
// ---- METHODS -------------------------------------------------------------
// --------------------------------------------------------------------------


template<class T>
void pool_t<T>::clear()
{
    m_release_ptrbuf(m_ptrbuf);
    m_size   = 0;
    m_ptrbuf = 0;
    m_change_counter++;
}


template<class T>
void pool_t<T>::append(T& item)
{
    *(append()) = item;
}


template<class T>
T* pool_t<T>::append()
{
    //printf("\n\nAPPEND\n");
    int index_in_segment = m_size % m_SEGMENT_ELEMENTS;
    int ptrbuf_num       = m_size / m_SEGMENT_ELEMENTS / m_PTRBUF_ELEMENTS;
    int segment_num      = m_size / m_SEGMENT_ELEMENTS % m_PTRBUF_ELEMENTS; // segment num in ptrbuf

    if (!m_ptrbuf)
        m_ptrbuf = (pool_dummy_t**)m_create_ptrbuf();

    // find ptrbuf according to ptrbuf_num. create it if not found.
    pool_dummy_t** ptrbuf = m_ptrbuf;
    for (int i = 0; i < ptrbuf_num; i++)
    {
        if (ptrbuf[m_PTRBUF_ELEMENTS])
            ptrbuf = (pool_dummy_t**)ptrbuf[m_PTRBUF_ELEMENTS];
        else
        {
            //printf("creating new buf\n");
            assert(i == ptrbuf_num - 1);
            assert(segment_num ==0);
            assert(index_in_segment == 0);
            ptrbuf[m_PTRBUF_ELEMENTS] = (pool_dummy_t*)m_create_ptrbuf();
        }
    }

    //printf("index_in_segment %i ptrbuf_num %i segment_num %i\n", index_in_segment, ptrbuf_num, segment_num);
    //printf("PTRBUF_ELEMENTS %i SEGMENT_ELEMENTS %i m_size %i\n", m_PTRBUF_ELEMENTS, m_SEGMENT_ELEMENTS, m_size);

    // find segment according to segment_num. if not found, create it.
    if (!ptrbuf[segment_num])
    {
        //printf("creating new segment bytes %i sizeof %i\n", m_SEGMENT_ELEMENTS * sizeof(T), sizeof(T));
        ptrbuf[segment_num] = (pool_dummy_t*)new char[m_SEGMENT_ELEMENTS * sizeof(T)];
    }

    m_size++;
    m_change_counter++;

    //printf("ptrbuf[segment_num] %i\n", ptrbuf[segment_num]);
    //printf("returing %i\n", (((char*)ptrbuf[segment_num]) + 1));
    //printf("returing %i\n", (((char*)ptrbuf[segment_num]) + index_in_segment * sizeof(T)));
    //printf("returing %i\n", (index_in_segment * sizeof(T)));
    return (T*)((char*)ptrbuf[segment_num] + index_in_segment * sizeof(T));
}


template<class T>
T* pool_t<T>::get(int i)
{
    if (i >= m_size)
        return NULL;
    if (i < 0)
        i += m_size;
    if (i < 0)
        return NULL;

    int index_in_segment = i % m_SEGMENT_ELEMENTS;
    int ptrbuf_num       = i / m_SEGMENT_ELEMENTS / m_PTRBUF_ELEMENTS;
    int segment_num      = i / m_SEGMENT_ELEMENTS % m_PTRBUF_ELEMENTS; // segment num in ptrbuf

    //printf("index_in_segment %i ptrbuf_num %i segment_num %i\n", index_in_segment, ptrbuf_num, segment_num);
    //printf("PTRBUF_ELEMENTS %i SEGMENT_ELEMENTS %i m_size %i\n", m_PTRBUF_ELEMENTS, m_SEGMENT_ELEMENTS, m_size);

    pool_dummy_t** ptrbuf = (pool_dummy_t**)m_get_ptrbuf(ptrbuf_num);
    assert(ptrbuf);
    assert(ptrbuf[segment_num]);

    return (T*)((char*)ptrbuf[segment_num] + index_in_segment * sizeof(T));
}


template<class T>
int pool_t<T>::get_change_counter()
{
    return m_change_counter;
}


template<class T>
void pool_t<T>::inc_change_counter()
{
    m_change_counter++;
}


template<class T>
int pool_t<T>::size()
{
    return m_size;
}


// --------------------------------------------------------------------------
// ---- PRIVATE -------------------------------------------------------------
// --------------------------------------------------------------------------


// recursively release all ptrbuf's
template<class T>
void pool_t<T>::m_release_ptrbuf(void* ptrbuf)
{
    pool_dummy_t** ptrbufcast = (pool_dummy_t**)ptrbuf;

    if (ptrbufcast)
    {
        // last element of ptrbuf is ptr to the next ptrbuf
        if (ptrbufcast[m_PTRBUF_ELEMENTS])
            m_release_ptrbuf(ptrbufcast[m_PTRBUF_ELEMENTS]);

        for (int i = 0; i < m_PTRBUF_ELEMENTS; i++)
        {
            if (ptrbufcast[i])
                delete [] ptrbufcast[i];
            else
                break;
        }
        delete [] ptrbufcast;
    }
}


// return n-th ptrbuf. return NULL if doesn't exist.
template<class T>
void* pool_t<T>::m_get_ptrbuf(int n)
{
    pool_dummy_t** ptrbuf = m_ptrbuf;
    for (int i = 0; i < n; i++)
    {
        if (ptrbuf[m_PTRBUF_ELEMENTS])
            ptrbuf = (pool_dummy_t**)ptrbuf[m_PTRBUF_ELEMENTS];
        else
            return NULL;
    }
    return ptrbuf;
}


template<class T>
void* pool_t<T>::m_create_ptrbuf()
{
    pool_dummy_t** ptrbuf = new pool_dummy_t*[m_PTRBUF_ELEMENTS + 1];
    memset(ptrbuf, 0, sizeof(pool_dummy_t**) * (m_PTRBUF_ELEMENTS + 1));
    return ptrbuf;
}


// --------------------------------------------------------------------------
// ---- TESTING -------------------------------------------------------------
// --------------------------------------------------------------------------


struct pool_test_element_t
{
    pool_test_element_t(int _v1, int _v2): v1(_v1), v2(_v2) {}
    int v1;
    int v2;
};


template<class T>
void pool_t<T>::test()
{
    pool_t<pool_test_element_t> p(2,2);
    pool_test_element_t  e1(3,4);
    pool_test_element_t  e2(5,6);
    pool_test_element_t  e4(9,10);
    pool_test_element_t* e;

    printf("111\n");
    p.append(e1);
    p.append(e2);

    printf("222\n");
    assert(p.size() == 2);

    printf("2221\n");
    pool_test_element_t* e3 = p.append();
    printf("2222\n");
    e3->v1 = 7;
    e3->v2 = 8;
    //*e3 = pool_test_element_t(7, 8);
    printf("2223\n");
    p.append(e4);

    printf("333\n");
    assert(p.size() == 4);

    e = p.get(0);
    assert(e->v1 == 3 && e->v2 == 4);
    e = p.get(3);
    printf("444\n");
    assert(e->v1 == 9 && e->v2 == 10);
    e = p.get(2);
    assert(e->v1 == 7 && e->v2 == 8);
    e = p.get(1);
    printf("555 v1 %i v2 %i\n", e->v1, e->v2);
    assert(e->v1 == 5 && e->v2 == 6);
    printf("555\n");
}


#endif // __POOL_T_H__
