#pragma once
#include "common/property.hpp"
#include <fstream>
#ifndef FLATPOINTS_POINTS_H_
#define FLATPOINTS_POINTS_H_
#include <unordered_map>
#include "json/json.hpp"
#include "common.hpp"

using std::unordered_map;
using json = nlohmann::json;
using flatpoints::common::tagged_property;

namespace flatpoints {

class flatpoints
{
    common::header                          _header;
    vector<uint64_t>                        _data;
    unordered_map<string, common::property> _properties;

  public:
    flatpoints(string);

  private:
    void _init_header(json&);
    void _parse_props(json&);
    void _parse_coords(json&);
};

inline void flatpoints::_init_header(json& data)
{
    this->_header                   = common::header();
    this->_header.coordinates_count = data.size();
    this->_header.properties_count  = data[0]["properties"].size();
    vector<string>       property_names;
    vector<common::type> property_types;
    auto                 items = data[0]["properties"].items();
    for (auto it = items.begin(); it != items.end(); ++it) {
        property_names.push_back(it.key());
        switch (it.value().type()) {
            case json::value_t::number_float:
                property_types.push_back(common::type::FLOAT32);
                break;
            case json::value_t::number_integer:
                property_types.push_back(common::type::INT64);
                break;
            case json::value_t::number_unsigned:
                property_types.push_back(common::type::UINT64);
                break;
            case json::value_t::boolean:
                property_types.push_back(common::type::BOOL);
                break;
            case json::value_t::string:
                property_types.push_back(common::type::STRING);
                break;
            case json::value_t::binary:
                property_types.push_back(common::type::UINT32);
                break;
            case json::value_t::null:
            case json::value_t::array:
            case json::value_t::discarded:
            case json::value_t::object:
                property_types.push_back(common::type::NIL);
                break;
        }
    }

    std::move(
      property_names.begin(),
      property_names.end(),
      this->_header.properties_names.begin()
    );

    std::move(
      property_types.begin(),
      property_types.end(),
      this->_header.properties_types.begin()
    );
}

inline void flatpoints::_parse_props(json& data)
{
    unordered_map<string, common::property> properties;

    // Initializing properties
    for (size_t i = 0; i < this->_header.properties_count; ++i) {
        common::property p;
        switch (this->_header.properties_types[i]) {
            case common::type::NIL:
                p =
                  tagged_property<common::empty>(this->_header.coordinates_count
                  );
                break;
            case common::type::INT32:
                p = tagged_property<int32_t>(this->_header.coordinates_count);
                break;
            case common::type::INT64:
                p = tagged_property<int64_t>(this->_header.coordinates_count);
                break;
            case common::type::UINT32:
                p = tagged_property<uint32_t>(this->_header.coordinates_count);
                break;
            case common::type::UINT64:
                p = tagged_property<uint64_t>(this->_header.coordinates_count);
                break;
            case common::type::FLOAT32:
                p = tagged_property<float>(this->_header.coordinates_count);
                break;
            case common::type::FLOAT64:
                p = tagged_property<double>(this->_header.coordinates_count);
                break;
            case common::type::STRING:
                p = tagged_property<string>(this->_header.coordinates_count);
                break;
            case common::type::BOOL:
                p = tagged_property<bool>(this->_header.coordinates_count);
                break;
        }

        // Moving ownership
        properties[this->_header.properties_names[i]] = std::move(p);
    }

    // Inserting properties
    for (size_t i = 0; i < this->_header.coordinates_count; ++i) {
        for (size_t j = 0; j < this->_header.properties_count; ++i) {
            std::string pname = this->_header.properties_names[j];
            properties[pname].insert(i, &data[i]["properties"][pname]);
        }
    }
}

inline flatpoints::flatpoints(string path)
{
    std::ifstream file(path);
    json          geojson = json::parse(file);

    this->_init_header(geojson);
    this->_parse_props(geojson);
}

} // namespace flatpoints

#endif