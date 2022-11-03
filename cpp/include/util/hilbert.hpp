#pragma once
#ifndef FLATPOINTS_UTIL_HILBERT_H_
#define FLATPOINTS_UTIL_HILBERT_H_

#include <cstdint>
#include <type_traits>
#include <vector>

using std::size_t;
using std::vector;

namespace flatpoints {
namespace util {
namespace internal {

template<typename T>
using integral_vector =
  typename std::enable_if<std::is_integral<T>::value, vector<T>>::type;

template<typename T>
using numeric_vector = typename std::enable_if<
  std::is_integral<T>::value | std::is_floating_point<T>::value,
  vector<T>>::type;

template<typename T>
using integral_void = typename std::enable_if<std::is_integral<T>::value>::type;

// rotate/flip a quadrant appropriately
template<typename T>
inline void rotate(T n, T* x, T* y, T rx, T ry)
{
    if (ry == 0) {
        if (rx == 1) {
            *x = n - 1 - *x;
            *y = n - 1 - *y;
        }

        // Swap x and y
        T t = *x;
        *x  = *y;
        *y  = t;
    }
}

// Convert (x,y) to index
template<typename T>
inline void positionToIndex(T n, T x, T y, T* h)
{
    T d = 0;
    for (T s = n / 2; s > 0; s /= 2) {
        T rx = (x & s) > 0;
        T ry = (y & s) > 0;
        d += s * s * ((3 * rx) ^ ry);
        rotate(n, &x, &y, rx, ry);
    }

    *h = d;
}

// convert index to (x,y)
template<typename T>
inline void indexToPosition(T n, T h, T* x, T* y)
{
    T t = h;
    *x = *y = 0;
    for (T s = 1; s < n; s *= 2) {
        T rx = 1 & (t / 2);
        T ry = 1 & (t ^ rx);
        rotate(s, x, y, rx, ry);
        *x += s * rx;
        *y += s * ry;
        t /= 4;
    }
}

template<typename T, typename S>
inline integral_vector<S> xToCol(S n, vector<T>& x, T xmax, T xmin)
{
    S         size = x.size();
    vector<S> s(size);
    T         diff = static_cast<T>(n) / (xmax - xmin);

    for (S i = 0; i < size; i++) {
        if (x[i] >= xmin && x[i] < xmax) {
            s[i] = static_cast<S>(floor((x[i] - xmin) * diff));
        } else if (x[i] == xmax) {
            s[i] = n - 1;
        } else {
            s[i] = static_cast<S>(-1);
        }
    }

    return s;
}

template<typename T, typename S>
inline integral_vector<S> yToRow(S n, vector<T>& y, T ymax, T ymin)
{
    S         size = y.size();
    vector<S> s(size);
    T         diff = static_cast<T>(n) / (ymax - ymin);

    for (S i = 0; i < size; i++) {
        if (y[i] >= ymin && y[i] < ymax) {
            s[i] = static_cast<S>(floor((y[i] - ymin) * diff));
        } else if (y[i] == ymax) {
            s[i] = n - 1;
        } else {
            s[i] = static_cast<S>(-1);
        }
    }

    return s;
}

template<typename T, typename S>
inline numeric_vector<T> colsToX(S n, vector<S>& cols, T xmax, T xmin)
{
    S         size = cols.size();
    vector<T> s(size);
    T         diff = (xmax - xmin) / static_cast<T>(n);

    for (S i = 0; i < size; i++) {
        s[i] = static_cast<T>(xmin + ((cols[i] + 0.5) * diff));
    }

    return s;
}

template<typename T, typename S>
inline numeric_vector<T> rowsToY(S n, vector<S>& rows, T ymax, T ymin)
{
    S         size = rows.size();
    vector<T> s(size);
    T         diff = (ymax - ymin) / static_cast<T>(n);

    for (S i = 0; i < size; i++) {
        s[i] = static_cast<T>(ymin + ((rows[i] + 0.5) * diff));
    }

    return s;
}
} // namespace internal

template<typename T>
struct extent
{
    T xmax;
    T ymax;
    T xmin;
    T ymin;
};

template<typename T>
inline uint64_t index(size_t n, T x, T y, extent<T>& bounds)
{
    uint64_t h;

    size_t   nn = size_t(1) << n;
    internal::positionToIndex(
      nn,
      internal::xToCol(nn, vector<T>{ x }, bounds.xmax, bounds.xmin)[0],
      internal::yToRow(nn, vector<T>{ y }, bounds.ymax, bounds.ymin)[0],
      &h
    );
    return h;
}

template<typename T>
inline vector<uint64_t>
index(size_t n, vector<T>& x, vector<T>& y, extent<T>& bounds)
{
    size_t    len  = x.size();
    size_t    nn   = size_t(1) << n;
    vector<T> xpos = internal::xToCol(nn, x, bounds.xmax, bounds.xmin),
              ypos = internal::yToRow(nn, y, bounds.ymax, bounds.ymin);

    vector<uint64_t> h(len);
    for (size_t i = 0; i < len; ++i) {
        internal::positionToIndex(nn, x[i], y[i], &h[i]);
    }

    return h;
}

template<typename T>
inline void coordinates(size_t n, uint64_t h, extent<T>& bounds, T& x, T& y)
{
    uint64_t xpos, ypos;
    size_t   nn = size_t(1) << n;
    internal::indexToPosition(nn, h, &xpos, &ypos);

    x =
      internal::colsToX(nn, vector<uint64_t>{ xpos }, bounds.xmax, bounds.xmin);
    y =
      internal::rowsToY(nn, vector<uint64_t>{ ypos }, bounds.ymax, bounds.ymin);
}

template<typename T>
inline void coordinates(
  size_t            n,
  vector<uint64_t>& h,
  extent<T>&        bounds,
  vector<T>&        x,
  vector<T>&        y
)
{
    size_t           len = h.size(), nn = size_t(1) << n;
    vector<uint64_t> xpos(len), ypos(len);

    for (size_t i = 0; i < len; ++i) {
        internal::indexToPosition(nn, h[i], &xpos[i], &ypos[i]);
    }

    x = internal::colsToX(nn, xpos, bounds.xmax, bounds.xmin);
    y = internal::rowsToY(nn, ypos, bounds.ymax, bounds.ymin);
}

} // namespace util
} // namespace flatpoints

#endif