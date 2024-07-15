#ifndef HEADER_H_
#define HEADER_H_

#include <stdint.h>
#include <stdbool.h>

/*!
@code_uid{free_fun(), Free function brief description}
@code_litem{Details}
Free function longer description.

@param[in]  x  - the parameter x

@returns
pointer to a static array

@code_bw_trace{brief}
- @tr{SRS_PRJ_FF_00}
- @tr{DVR_PRJ_MC4_R11_03}
@code_fw_trace
@endcode_uid
*/
uint8_t const* free_fun(uint32_t x);

/*!
@code_uid{Foo, Class Foo brief description}
@code_litem{Details}
Class Foo longer description.

@code_bw_trace{brief}
- @tr{SRS_PRJ_Foo_00}
@code_fw_trace
@endcode_uid
*/
typedef struct Foo {
    /*! @code_uid{Foo::x, Attribute x of class Foo brief description}
    @code_litem{Details}
    Attribute x of class Foo: longer description.
    @code_bw_trace{brief}
    - @tr{SRS_PRJ_Foo_01}
    @endcode_uid
    */
    uint32_t x;

    /*! @code_uid{Foo::x_dis, Duplicate Inverse Storage for attribute Foo::x}
    @code_litem{Details}
    Duplicate Inverse Storage (DIS) for attribute Foo::x: longer description.
    @code_bw_trace{brief}
    - @tr{SRS_PRJ_Foo_01}
    - @tr{Foo_verify_()}
    - @tr{Foo::x}
    @endcode_uid
    */
    uint32_t x_dis;
} Foo;

/*!
@code_uid{Foo_inst, Foo instance brief description}
@code_litem{Details}
Foo instance longer description.
@code_bw_trace{brief}
- @tr{SRS_PRJ_Foo_04}
- @tr{Foo}
- @tr{DVP_PRJ_MC4_R11_03}
@code_fw_trace
@endcode_uid
*/
extern Foo const Foo_inst;

/*!
@code_uid{Foo_update_(), Update operation to preserve the class invariant}
@code_litem{Details}
Constructor of class Foo longer description.
@param[in]  me - the instance pointer (OOP in C)
@code_bw_trace{brief}
- @tr{SRS_PRJ_Foo_02}
- @tr{Foo}
@code_fw_trace
@endcode_uid
*/
static inline void Foo_update_(Foo* const me) {
    me->x_dis = ~(uintptr_t)me->x;
}

/*!
@code_uid{Foo_ctor(), Constructor of class Foo brief description}
@code_litem{Details}
Constructor of class Foo longer description.
@param[in]  me - the instance pointer (OOP in C)
@param[in]  x  - the initial value for me->x
@code_bw_trace{brief}
- @tr{SRS_PRJ_Foo_02}
- @tr{Foo}
@code_fw_trace
@endcode_uid
*/
static inline void Foo_ctor(Foo * const me, uint32_t const x) {
    me->x = x;
    Foo_update_(me);
}

/*!
@code_uid{Foo_verify_(), Operation verify_() of class Foo brief description}
@code_litem{Details}
Operation verify_() of class Foo longer description.
@param[in]  me - the instance pointer (OOP in C)
@returns 'true' when the Foo instance verification succeeds, 'false' otherwise.
@code_bw_trace{brief}
- @tr{SRS_PRJ_Foo_03}
- @tr{Foo}
@code_fw_trace
@endcode_uid
*/
bool Foo_verify_(Foo const * const me);

#endif // HEADER_H_
