#pragma once
#ifndef FLATPOINTS_POINTS_H_
#define FLATPOINTS_POINTS_H_
#include <vector>
#include <string>
#include <cstdint>
#include <unordered_map>
#include <fstream>

using std::string;
using std::unordered_map;
using std::vector;

namespace flatpoints {

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
    int32_t  int32_v;
    int64_t  int64_v;
    uint32_t uint32_v;
    uint64_t uint64_v;
    float    float32_v;
    double   float64_v;
    string   string_v;
    bool     bool_v;
};

struct property
{
    flatpoints::value val;
    flatpoints::type  tag;
};

struct header
{
    uint64_t         start_of_data;
    uint64_t         coordinates_count;
    uint64_t         properties_count;
    vector<string>   properties_names;
    vector<type>     properties_types;
    vector<uint64_t> offsets;

    /**
     */
    void read(std::ifstream& file)
    {
        char magic[3];
        file.seekg(0, std::ios::beg);

        file.read(reinterpret_cast<char*>(&(magic[0])), 1);
        file.read(reinterpret_cast<char*>(&(magic[1])), 1);
        file.read(reinterpret_cast<char*>(&(magic[2])), 1);
        if (magic[0] != 'F' && magic[1] != 'P' && magic[2] != 'S') {
            file.close();
            throw "Magic number not correct";
        }

        file.read(reinterpret_cast<char*>(&(this->coordinates_count)), 8);
        file.read(reinterpret_cast<char*>(&(this->properties_count)), 8);

        this->offsets = vector<uint64_t>(this->properties_count + 1);
        for (size_t i = 0; i < this->properties_count + 1; ++i) {
            file.read(reinterpret_cast<char*>(&(this->offsets[i])), 8);
        }

        this->properties_types = vector<type>(this->properties_count);
        for (size_t i = 0; i < this->properties_count; ++i) {
            file.read(reinterpret_cast<char*>(&(this->properties_types[i])), 1);
        }

        this->properties_names = vector<string>(this->properties_count);
        for (size_t i = 0; i < this->properties_count; ++i) {
            std::getline(file, this->properties_names[i], '\0');
        }
    }

    /**
     */
    size_t write(std::ofstream& file)
    {
        size_t bytes_written = 0;
        file.seekp(0, std::ios::beg);

        // Magic
        file.write(0x46, 1);
        file.write(0x50, 1);
        file.write(0x53, 1);
        bytes_written += 3;

        file.write(reinterpret_cast<char*>(&(this->coordinates_count)), 8);
        file.write(reinterpret_cast<char*>(&(this->properties_count)), 8);
        bytes_written += 16;

        for (size_t i = 0; i < this->properties_count + 1; ++i) {
            file.write(reinterpret_cast<char*>(&(this->offsets[i])), 8);
        }
        bytes_written += (this->properties_count + 1) * 8;

        for (size_t i = 0; i < this->properties_count; ++i) {
            file.write(
              reinterpret_cast<char*>(&(this->properties_types[i])), 1
            );
        }
        bytes_written += this->properties_count;

        for (size_t i = 0; i < this->properties_count; ++i) {
            size_t strlen = this->properties_names[i].size() + 1;
            file.write(this->properties_names[i].c_str(), strlen);
            bytes_written += strlen;
        }

        return bytes_written;
    };
};

class points
{
    flatpoints::header              _header;
    vector<uint64_t>                _data;
    unordered_map<string, property> _properties;
};

} // namespace flatpoints

#endif