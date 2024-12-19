# yadifmod2

## Yet Another Deinterlacing Filter mod  for Avisynth2.6/Avisynth+

	yadifmod2 = yadif + yadifmod

### Requirement:
	- Avisynth2.6.0final/Avisynth+r2150 or greater.
	- WindowsVista SP2 or later.
	- Visual C++ Redistributable Packages for Visual Studio 2019.

### Syntax:

	yadifmod2(clip, int "order", int "field", int "mode", clip "edeint", int "opt")

####	clip -

		All planar 8/10/12/14/16/float formats are supported.

####	order -

		Set the field order.

		-1(default) = use avisynth's internal parity value
		 0 = bff
		 1 = tff

####	field -

		Controls which field to keep when using same rate output.

		-1 = set eqal to order.(default)
		 0 = keep bottom field.
		 1 = keep top field.

		This parameter doesn't do anything when using double rate output.

####	mode -

		Controls double rate vs same rate output, and whether or not the spatial interlacing check is performed.

		0 = same rate, do spatial check.(default)
		1 = double rate, do spatial check.
		2 = same rate, no spatial check.
		3 = double rate, no spatial check.

####	edeint -

		Clip from which to take spatial predictions.

		If this is not set, yadifmod2 will generate spatial predictions itself as same as yadif.

		This clip must be the same width, height, colorspace and bit depth as the input clip.
		If using same rate output, this clip should have the same number of frames as the input.
		If using double rate output, this clip should have twice as many frames as the input.

####	opt -

		Controls which cpu optimizations are used.

		 0 = Use C++ routine.
		 1 = Use SSE2 + SSE routine if possible. When SSE2 can't be used, fallback to 0.
		 2 = Use SSSE3 + SSE2 + SSE routine if possible. When SSSE3 can't be used, fallback to 1.
		 3 = Use SSE4.1 + SSSE3 + SSE2 + SSE routine if possible. When SSE4.1 can't be used, fallback to 2.
		 4 = Use SSE4.1 + SSSE3 + SSE2 + AVX routine if possible. When AVX can't be used, fallback to 3.
		 5 = Use AVX2 + AVX routine if possible. When AVX2 can't be used, fallback to 4. (default)

### Building:

#### Windows

    Use solution files.

#### Linux

##### Requirements

    Git
    C++11 compiler
    CMake >= 3.16

```
git clone https://github.com/Asd-g/yadifmod2 && \
cd yadifmod2 && \
mkdir build && \
cd build && \

cmake ..
make -j$(nproc)
sudo make install
```

### Changelog:

	0.0.0(20160305)
		initial release

	0.0.1(20160308)
		Chage default value of 'opt' to -1 and remove wrong description.
		This filter does not require 32byte alignment.

	0.0.2(20160318)
		Fix wrong calculation of spatial predictions when opt > 1.
		Thanks to Fizick the report.

	0.0.3(20160320)
		Add missing prediction score update.
		Also, fix previous frame position when n == 0.
		now, the outputs of yadifmod2 w/o edeint clip are almost same as yadif1.7 except edge part of image.

	0.0.4(20160527)
		Set filter mode as MT_NICE_FILTER automatically on Avisynth+MT.
		Disable AVX2 code if /arch:AVX2 is not set.

	0.0.4-1(20160705)
		Update avisynth.h to Avisynth+MT r2005

	0.1.0 (20160707)
		Add Avisynth+MT's high bit depth formats support.(back port from VapourSynth version)

	0.2.0 (20160815)
		Add Avisynth+MT's planar RGB and 10/12/14bits formats support.

	0.2.1 (20200513)
		Use internal CPU check.
		Removed /arch:AVX2 requirement for AVX2 code.

	0.2.2 (20200514)
		Copy frame properties when available.

    0.2.3 (20200523)
        Fixed high bit-depth output.
        Fixed crash for mode=2/3 when opt>0.

    0.2.4 (20200526)
        Allow clips with alpha plane.

    0.2.5 (20200612)
        Fixed crashing when opt=4 and the bit depth is not 32-bit.

    0.2.6 (20200630)
        Changed the opt value for AVX2 + AVX routine.

    0.2.7 (20210207)
        Set frame property _FieldBased to 0.

    0.2.8 (20230722)
        Throw error if YUV420 height is not mod4.
