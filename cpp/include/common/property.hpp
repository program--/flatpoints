#ifndef FLATPOINTS_COMMON_PROPERTY_H_
#define FLATPOINTS_COMMON_PROPERTY_H_

#include <cstdint>
#include <string>

namespace flatpoints {
namespace common {

enum type
{
    INT32   = 1,
    INT64   = 2,
    UINT32  = 3,
    UINT64  = 4,
    FLOAT32 = 5,
    FLOAT64 = 6,
    STRING  = 7,
    BOOL    = 8
};

union value
{
    int32_t     int32_v;
    int64_t     int64_v;
    uint32_t    uint32_v;
    uint64_t    uint64_v;
    float       float32_v;
    double      float64_v;
    std::string string_v;
    bool        bool_v;
};

struct property
{
    value val;
    type  tag;
};

} // namespace common
} // namespace flatpoints

#endif