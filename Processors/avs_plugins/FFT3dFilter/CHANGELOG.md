### Change log - fft3dfilter  ###

```
FFT3DFilter v2.9 (20210324)
  - Fix issue when pfactor <> 0 and using 10+ bits (Xinyue Lu, neo_FFT3D) 
  - Fix incorrect negative value float to integer rounding (Xinyue Lu, neo_FFT3D r7)
  - add CMake build system
  - linux build
  - Replace never used 3dnow ApplyWiener3D4 with simd SSE2. (bt=4, degrid=0, pfactor=0) (2x speed)

FFT3DFilter v2.8 (20201201)
  - Fix: chroma plane filtering for 32 bit float formats  

FFT3DFilter v2.7 (20201130)
  - Fix: make fftw plans thread safe.
  - preserve frame properties for avs+

FFT3DFilter v2.6 (20190131)
  - Fix: Proper rounding when internal 32 bit float data are converted back to integer pixel values

FFT3DFilter v2.5 (20180702)
  - 32bit Float YUV: Chroma center to 0.0 instead of 0.5, to match new Avisynth+ r2728-

FFT3DFilter v2.4 (20170608)
  - some inline asm (not all) ported to simd intrisics, helps speedup x64 mode, but some of them faster also on x86.
  - intrinsics bt=0 
  - intrinsics bt=2, degrid=0, pfactor=0
  - intrinsics bt=3 sharpen=0/1 dehalo=0/1
  - intrinsics bt=3
  - Adaptive MT settings for Avisynth+: MT_SERIALIZED for bt==0 (temporal), MT_MULTI_INSTANCE for others
  - Copy Alpha plane if exists
  - reentrancy checks against bad multithreading usage
    Note: for properly operating in MT_SERIALIZED mode in Avisynth MT, please use Avs+ r2504 or better.

FFT3DFilter v2.3 (20170221)
  - apply current avs+ headers
  - 10-16 bits and 32 bit float colorspace support in AVS+
  - Planar RGB support
  - look for libfftw3f-3.dll first, then fftw3.dll
  - inline asm ignored on x64 builds
  - pre-check: if plane to process for greyscale is U and/or V return original clip
  - auto register MT mode for avs+: MT_SERIALIZED

Previous versions by Fizick and martin53
```
Original Docs:
https://avisynth.org.ru/fft3dfilter/fft3dfilter.html
Project:
https://github.com/pinterf/fft3dfilter
Forum:
https://forum.doom9.org/showthread.php?t=174347

Build instructions
------------------
### Windows Visual Studio MSVC

use IDE

### Windows GCC

(mingw installed by msys2)
 From the 'build' folder under project root:

```
del ..\CMakeCache.txt
cmake .. -G "MinGW Makefiles" -DENABLE_INTEL_SIMD:bool=on
@rem test: cmake .. -G "MinGW Makefiles" -DENABLE_INTEL_SIMD:bool=off
cmake --build . --config Release
```

### Linux

Note: ENABLE_INTEL_SIMD is automatically off for non-x86 architectures

Clone repo and build

```
git clone https://github.com/pinterf/fft3dfilter
cd fft3dfilter
cmake -B build -S .
cmake --build build
```

Useful hints:

build after clean:

```
cmake --build build --clean-first
```

Force no Intel x86-assembler support:

```
cmake -B build -S . -DENABLE_INTEL_SIMD:bool=off
```

delete CMake cache:

```
rm build/CMakeCache.txt
```



* Find binaries at
  
        build/fft3dfilter/libfft3dfilter.so

* Install binaries

        cd build
        sudo make install

