#ifndef MALLOC_STRIKE_H
#define MALLOC_STRIKE_H

#include <stddef.h>

void malloc_strike_reset(void);
void malloc_strike_fail_at(size_t index);
size_t malloc_strike_count(void);
size_t malloc_strike_size(size_t index);

#endif
