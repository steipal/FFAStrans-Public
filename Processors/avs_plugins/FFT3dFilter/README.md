# fft3dfilter #

FFT3DFilter is 3D Frequency Domain filter - strong denoiser and moderate sharpener.

Previous versions by Fizick and martin53

## Links

Original documentation: https://avisynth.org.ru/fft3dfilter/fft3dfilter.html
Project: https://github.com/pinterf/fft3dfilter
Forum: https://forum.doom9.org/showthread.php?t=174347

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
