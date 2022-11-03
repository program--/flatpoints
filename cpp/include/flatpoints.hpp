#pragma once
#ifndef FLATPOINTS_POINTS_H_
#define FLATPOINTS_POINTS_H_
#include <unordered_map>
#include "common.hpp"

using std::unordered_map;

namespace flatpoints {

class flatpoints
{
    common::header                          _header;
    vector<uint64_t>                        _data;
    unordered_map<string, common::property> _properties;

    flatpoints(string);
};

inline flatpoints::flatpoints(string path) {}

} // namespace flatpoints

#endif