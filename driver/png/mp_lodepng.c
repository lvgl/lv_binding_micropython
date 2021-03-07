#include "py/obj.h"

/**
 * Implementation of memory allocation functions for lodepng, which delegate gc allocation
 * This allows lodepng use the ram reserved for Micropython gc
 */


void* lodepng_malloc(size_t size)
{
    return m_malloc(size);
}

void* lodepng_realloc(void* ptr, size_t new_size)
{
    return m_realloc(ptr, new_size);
}

void lodepng_free(void* ptr)
{
    m_free(ptr);
}


