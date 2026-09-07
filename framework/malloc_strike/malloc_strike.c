#include "malloc_strike.h"
#include <string.h>

#define MALLOC_MAX_RECORDS 1024
#define MALLOC_POISON 0xAA

static size_t g_malloc_count;
static size_t g_malloc_sizes[MALLOC_MAX_RECORDS];
static size_t g_malloc_record_count;
static size_t g_malloc_fail_at = (size_t)-1;

void *__real_malloc(size_t size);

void *__wrap_malloc(size_t size) {
    size_t index = g_malloc_count;
    g_malloc_count++;

    if (g_malloc_record_count < MALLOC_MAX_RECORDS) {
        g_malloc_sizes[g_malloc_record_count] = size;
        g_malloc_record_count++;
    }

    if (index == g_malloc_fail_at) return (NULL);

    void *ptr = __real_malloc(size);

    if (ptr != NULL) memset(ptr, MALLOC_POISON, size);

    return ptr;
}

void malloc_strike_reset(void) {
    g_malloc_count = 0;
    g_malloc_record_count = 0;
    g_malloc_fail_at = (size_t)-1;
}

void malloc_strike_fail_at(size_t index) {
    g_malloc_fail_at = index;
}

size_t malloc_strike_count(void) {
    return (g_malloc_count);
}

size_t malloc_strike_size(size_t index) {
    if (index >= g_malloc_record_count) return (0);
    return (g_malloc_sizes[index]);
}
