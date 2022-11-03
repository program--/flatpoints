#include <iostream>
#include <vector>
#include <cstdint>
#include <random>
#include <algorithm>
#include "util.hpp"
#include "vtenc/vtenc.h"

using std::vector;

int main()
{
    vtenc*           handler   = vtenc_create();
    vtenc*           handler2  = vtenc_create();
    size_t           num_int   = 100000;
    bool             all_equal = true;
    vector<uint64_t> x(num_int);
    for (int i = 0; i < num_int; i++) {
        x[i] = rand();
    }
    std::sort(x.begin(), x.end());

    vector<uint8_t>  encoded = flatpoints::util::compress(handler, x);
    vector<uint64_t> decoded =
      flatpoints::util::decompress(handler2, encoded, num_int);

    for (int i = 0; i < num_int; i++) {
        if (decoded[i] != x[i]) {
            all_equal = false;
        }
    }

    std::cout << "Encoded Size: " << encoded.size() << " bytes\n";
    std::cout << "Decoded Size: " << decoded.size() * 8 << " bytes\n";
    std::cout << "Compression Ratio: "
              << (1 - (encoded.size() / (double)(decoded.size() * 8))) * 100
              << "% \n";
    std::cout << "Decoded same as original?: " << (all_equal ? "Yes" : "No")
              << "\n";
    std::cout << std::endl;

    vtenc_destroy(handler);
    vtenc_destroy(handler2);

    return 0;
}