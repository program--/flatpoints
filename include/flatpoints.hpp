#include <cstdint>
#include <string>
#include <vector>
#include <fstream>

using std::string;
using std::vector;

namespace flatpoints {

struct Header
{
    uint64_t         coordinates_count;
    uint64_t         properties_count;
    vector<uint64_t> offsets;
    vector<string>   properties_names;

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

        for (size_t i = 0; i < this->properties_count + 1; ++i) {
            file.write(reinterpret_cast<char*>(&(this->offsets[i])), 8);
        }

        for (size_t i = 0; i < this->properties_count; ++i) {
            size_t strlen = this->properties_names[i].size() + 1;
            file.write(this->properties_names[i].c_str(), strlen);
            bytes_written += strlen;
        }

        return ((8 * this->properties_count + 3) + bytes_written);
    };
};

namespace io {

class Reader;
class Writer;

} // namespace io
} // namespace flatpoints