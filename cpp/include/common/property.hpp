#ifndef FLATPOINTS_COMMON_PROPERTY_H_
#define FLATPOINTS_COMMON_PROPERTY_H_

#include <cstdint>
#include <string>
#include <vector>
#include <type_traits>

namespace flatpoints {
namespace common {

enum type
{
    NIL     = 0,
    INT32   = 1,
    INT64   = 2,
    UINT32  = 3,
    UINT64  = 4,
    FLOAT32 = 5,
    FLOAT64 = 6,
    STRING  = 7,
    BOOL    = 8
};

struct empty
{};

class property
{
    type tag;

  public:
    constexpr type get_type() { return this->tag; }
    virtual void   insert(size_t, void*);
};

template<typename T>
class tagged_property : public virtual property
{
    type tag;
    void set_tag()
    {
        if (std::is_same<common::empty, T>()) {
            this->tag = type::NIL;
        } else if (std::is_same<int32_t, T>()) {
            this->tag = type::INT32;
        } else if (std::is_same<int64_t, T>()) {
            this->tag = type::INT64;
        } else if (std::is_same<uint32_t, T>()) {
            this->tag = type::UINT32;
        } else if (std::is_same<uint64_t, T>()) {
            this->tag = type::UINT64;
        } else if (std::is_same<float, T>()) {
            this->tag = type::FLOAT32;
        } else if (std::is_same<double, T>()) {
            this->tag = type::FLOAT64;
        } else if (std::is_same<std::string, T>()) {
            this->tag = type::STRING;
        } else if (std::is_same<bool, T>()) {
            this->tag = type::BOOL;
        }
    }

  public:
    std::vector<T> data;

    tagged_property()
      : data(std::vector<T>(0))
    {
        this->set_tag();
    };

    tagged_property(size_t num)
      : data(std::vector<T>(num))
    {
        this->set_tag();
    };

    void insert(size_t i, void* d) { this->data[i] = static_cast<T>(d); }
};

} // namespace common
} // namespace flatpoints

#endif