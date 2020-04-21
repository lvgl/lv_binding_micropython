#include <errno.h>
#include <stdio.h>
#include <stdint.h>

extern int errno;
extern char _heap_start;    //set by linker
extern char _heap_end;      //set by linker

// Increase program data space. Malloc and related functions depend on this
caddr_t _sbrk(int incr) {
    static char *heap_end = NULL;
    char *prev_heap_end;
    if (heap_end == NULL) {
        heap_end = &_heap_start;
    }

    prev_heap_end = heap_end;
    if (heap_end + incr > &_heap_end) {
        errno = ENOMEM;
        return (caddr_t)-1;
    }
    heap_end += incr;
    return (caddr_t)prev_heap_end;
}

