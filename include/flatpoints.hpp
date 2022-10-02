#include <cstdint>
#include <string>
#include <vector>
#include <fstream>

using std::string;
using std::vector;

namespace flatpoints {

enum Type
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

struct Header
{
    uint64_t         coordinates_count;
    uint64_t         properties_count;
    vector<string>   properties_names;
    vector<Type>     properties_types;
    vector<uint64_t> offsets;

    /**
     */
    void read(std::ifstream& file)
    {
        file.seekg(0, std::ios::beg);
        file.read(reinterpret_cast<char*>(&(this->coordinates_count)), 8);
        file.read(reinterpret_cast<char*>(&(this->properties_count)), 8);

        this->offsets = vector<uint64_t>(this->properties_count + 1);
        for (size_t i = 0; i < this->properties_count + 1; ++i) {
            file.read(reinterpret_cast<char*>(&(this->offsets[i])), 8);
        }

        this->properties_types = vector<Type>(this->properties_count);
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

namespace io {

class Reader;
class Writer;

} // namespace io
} // namespace flatpoints