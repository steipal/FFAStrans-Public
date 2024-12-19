## Description

Motion adaptive deinterlacing based on yadif with the use of w3fdif and cubic interpolation algorithms.

This is [a port of the VapourSynth plugin Bwdif](https://github.com/HomeOfVapourSynthEvolution/VapourSynth-Bwdif).

### Requirements:

- AviSynth 2.60 / AviSynth+ 3.4 or later

- Microsoft VisualC++ Redistributable Package 2022 (can be downloaded from [here](https://github.com/abbodi1406/vcredist/releases)) (Windows only)

### Usage:

```
BWDIF (clip, int "field", clip "edeint", int "opt", float "thr", bool "debug", bool "pass")
```

### Parameters:

- clip<br>
    A clip to process. All planar formats are supported.

- field<br>
    Controls the mode of operation (double vs same rate) and which field is kept.<br>
    -4: Double rate (alternates each frame). It uses `_FieldBased` frame property to determine with which field the clip starts.<br>
    -3: Same rate. It uses `_FieldBased` frame property to determine which field is kept.<br>
    -2: Double rate (alternates each frame). It uses `GetParity` clip property to determine with which field the clip starts.<br>
    -1: Same rate. It uses `GetParity` clip property to determine which field is kept.<br>
    0: Same rate, keep bottom field.<br>
    1: Same rate, keep top field.<br>
    2: Double rate (alternates each frame), starts with bottom field.<br>
    3: Double rate (alternates each frame), starts with top field.<br>
    Default: -1.

- edeint<br>
    Clip from which to take spatial predictions. This clip must be the same width, height, and colorspace as the input clip.<br>
    If using same rate output, this clip should have the same number of frames as the input. If using double rate output, this clip should have twice as many frames as the input.

- opt<br>
    Sets which cpu optimizations to use.<br>
    -1: Auto-detect.<br>
    0: Use C++ code.<br>
    1: Use SSE2 code.<br>
    2: Use AVX2 code.<br>
    3: Use AVX512 code.<br>
    Default: -1.

- thr<br>
    Threshold for interpolation.<br>
    If the difference between pixels of the prev/next frame is less than or equal to this, the resulted pixel wouldn't be interpolated.<br>
    Must be between 0.0..100.0.<br>
    100.0: No interpolation is performed.<br>
    Default: 0.0.

- debug<br>
    Whether to show which pixels will be interpolated.<br>
    Default: False.

- pass<br>
    Whether to return the source frame (repeated when double rate) when `_FieldBased` is `0`.
    Default: False.

### Building:

- Windows<br>
    Use solution files.

- Linux<br>
    ```
    Requirements:
        - Git
        - C++17 compiler
        - CMake >= 3.16
    ```
    ```
    git clone https://github.com/Asd-g/AviSynth-BWDIF && <br>
    cd AviSynth-BWDIF && <br>
    mkdir build && <br>
    cd build && <br>

    cmake ..
    make -j$(nproc)
    sudo make install
    ```
