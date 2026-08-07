#ifndef HEADER_H_
#define HEADER_H_

#include <stdint.h>
#include <stdbool.h>

// This file (header.h) intentionally does NOT contain Doxygen
// documentation. Instead, all code elements are documented
// in the external file (code.dox). This allows the documentation
// to evolve independently from the source code.

// free function
uint8_t const *free_fun(uint32_t x);

// This following demonstrates how to document a *class* in C

//! @class Foo
typedef struct Foo {
    uint32_t x;      //!< @public @memberof Foo
    uint32_t x_dis;  //!< @private @memberof Foo
} Foo;

//! @public @memberof Foo
void Foo_ctor(Foo * const me, uint32_t const x);

//! @public @memberof Foo
bool Foo_verify_(Foo const * const me);

//! @public @memberof Foo
void Foo_update_(Foo* const me);

//! @public @static @memberof Foo
extern Foo Foo_inst;

#endif // HEADER_H_
