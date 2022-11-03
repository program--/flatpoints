#pragma once
#ifndef FLATPOINTS_UTIL_COMPRESSION_H_
#define FLATPOINTS_UTIL_COMPRESSION_H_
#include <cstdint>
#include <vector>
#include "vtenc/vtenc.h"

using std::vector;

namespace flatpoints {
namespace util {

inline vector<uint8_t> compress(vtenc* handler, vector<uint64_t>& data)
{
    const size_t    len     = data.size();
    const size_t    enc_cap = vtenc_max_encoded_size64(len);
    vector<uint8_t> encoded(enc_cap * sizeof(uint64_t));
    int             rc;
    rc = vtenc_encode64(handler, data.data(), len, encoded.data(), enc_cap);
    if (rc != VTENC_OK) {
        throw "VTEnc encoding failed";
    }
    encoded.resize(vtenc_encoded_size(handler));
    return encoded;
}

inline vector<uint64_t>
decompress(vtenc* handler, vector<uint8_t>& data, size_t num)
{
    int              rc;
    vector<uint64_t> decoded(num);
    rc = vtenc_decode64(handler, data.data(), data.size(), decoded.data(), num);
    if (rc != VTENC_OK) {
        throw "VTEnc decoding failed";
    }

    return decoded;
}

} // namespace util
} // namespace flatpoints

#endif