#pragma once
#ifndef FLATPOINTS_UTILS_H_
#define FLATPOINTS_UTILS_H_
#include <cstdint>
#include <vector>
#include "vtenc/vtenc.h"

using std::vector;

namespace flatpoints {
namespace utils {

inline vector<uint8_t> compress(vtenc* handler, vector<uint64_t>& data)
{
    const size_t    len     = data.size();
    const size_t    enc_cap = vtenc_max_encoded_size64(len);
    vector<uint8_t> encoded(enc_cap);
    int             rc;
    rc = vtenc_encode64(handler, data.data(), len, encoded.data(), enc_cap);
    if (rc != VTENC_OK) {
        throw "VTEnc encoding failed";
    }
    return encoded;
}

inline vector<uint64_t> decompress(vtenc* handler, vector<uint8_t>& data)
{
    int              rc;
    const size_t     enc_len = vtenc_encoded_size(handler);
    vector<uint64_t> decoded(enc_len);
    rc = vtenc_decode64(
      handler, data.data(), data.size(), decoded.data(), enc_len
    );
    if (rc != VTENC_OK) {
        throw "VTEnc decoding failed";
    }
    return decoded;
}

} // namespace utils
} // namespace flatpoints

#endif