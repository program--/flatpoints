#include <fstream>
#define CATCH_CONFIG_MAIN
#include "catch.hpp"

#include "flatpoints.hpp"

flatpoints::Header test_header;
string             path = "data/test_header.flatpoints";

TEST_CASE("Read/Write")
{
    uint64_t       val_cc = 472;
    uint64_t       val_pc = 6;
    vector<string> val_pn{
        "prop1", "prop2", "prop3", "prop4", "prop5", "prop6"
    };
    vector<flatpoints::Type> val_ty{
        flatpoints::Type::INT64, flatpoints::Type::STRING,
        flatpoints::Type::BOOL,  flatpoints::Type::INT64,
        flatpoints::Type::INT32, flatpoints::Type::UINT64
    };
    vector<uint64_t> val_of{ 3, 29, 353, 2834, 29343, 48505, 95864 };

    test_header.coordinates_count = val_cc;
    test_header.properties_count  = val_pc;
    test_header.properties_names  = val_pn;
    test_header.properties_types  = val_ty;
    test_header.offsets           = val_of;

    std::ofstream ofile;
    ofile.open(path, std::ios::binary);
    test_header.write(ofile);
    ofile.close();

    std::ifstream ifile;
    ifile.open(path, std::ios::binary);
    test_header = flatpoints::Header();
    test_header.read(ifile);

    REQUIRE(test_header.coordinates_count == val_cc);
    REQUIRE(test_header.properties_count == val_pc);
    for (size_t i = 0; i < 6; ++i) {
        REQUIRE(test_header.properties_names[i] == val_pn[i]);
        REQUIRE(test_header.properties_types[i] == val_ty[i]);
        REQUIRE(test_header.offsets[i] == val_of[i]);
    }
    REQUIRE(test_header.offsets[6] == val_of[6]);
}