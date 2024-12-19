Depan and DepanEstimate
=======================

Motion estimation and compensation plugin for Avisynth+ and Avisynth v2.6 family.
Supporting YUY2, 4:2:0, 4:2:2, 4:4:4, planar RGB* at native 8-16 bit depths
Still supporting Windows XP.
x86 and x64 version
*in DepanStabilize

Files: depan.dll, depanestimate.dll 

Credits: 
- Fizick

Modification base:
- Depan: 1.13.1 by Fizick
- DepanEstimate 1.10 by Fizick
http://avisynth.org.ru/depan/depan.html

Change log
- (20240503)
  - Moved to Visual Studio 2022, v141_xp and v143 toolset, Intel Compiler ICX 2024.1 and ICL build support
  Depan 2.14
    - Fix: "DepanScenes" plane parameter for YUY2 clips did not work
  DepanEstimate 2.11
    - Throw an error if memory allocation fails

- (20200522)
  Depan 2.13.1.6 
  DepanEstimate 2.10.0.4
  - Update Avisynth headers, use V8 interface frame property copy if available

- (20200430)
  Depan 2.13.1.5: 
  fix regression: DepanInterleave colorspace check allowed no planar, only YUY2
  Depan: Fix an issue when Depan would search for inputlog file even when there was no inputlog filename provided
  Depan: Fix crash on YUY2 input on internal YV16 conversion
- (20190502)
  Moved to Visual Studio 2019 Community Edition, v141_xp and v142 toolset
  DepanEstimate 2.10.0.3
  Depan 2.13.1.4
  (20190311)
  - DepanStabilize planar RGB 8-16 bits support: Generate motion vectors with mvtools MDepan, use it for DepanStabilize. Input clip can be planar RGB.
  - add missing roundings to some internal interpolation calculations
  - update documentation from Fizick's 2016 version
- (20170525)
  Fix: DepanEstimate 2.10.0.2 : did not recognize Scene changes, giving valid motion vectors instead
  Depan: no change, rebuild with current headers 2.13.1.3 (20170525)
- Fix: DepanStabilize: removed too strict checking for large motion vectors received from depan
       that resulted in like scene change
- (20161228)
  Fix: for YV12 the debug info text chroma part was positioned at wrong place
  Depan: 2.13.1.2 
  DepanEstimate: 2.10.0.1
- (20161218)
  Depan: 2.13.1.1: YUY2 input fix, as in MvTools 2.7.8.22
  Previous build: Depan: 2.13.1 (20161119)
- (20161119)
  DepanEstimate: 2.10 
  - General support of 10-16 bit formats with Avisynth Plus (r2294 or newer recommended)
  - First digit of version number became 2 (Fizick's 1.x.x), others left untouched, (sync'd with Fizick's version number)
  - Built with Visual Studio 2015 Community Edition, v140-xp toolset

Links
  http://avisynth.org.ru/depan/depan.html

For more information see also documents folder.

External dependencies for DepanEstimate: 
- libfftw3f-3.dll (or renamed to FFT3W.DLL)
from http://www.fftw.org/ or look at ICL builds at http://forum.doom9.org/showthread.php?t=173229
  
- Requires Microsoft Visual C++ Redistributable 2022, 2019
  
Source code:
https://github.com/pinterf/mvtools
under mvtools-pfmod branch
