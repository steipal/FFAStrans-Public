## MaskTools 2

This is a fork of the old Manao's masktools2 plugin. It mostly contains performance improvements, bugfixes and some little things that make the plugin more "mature".

### Difference to masktools2 a48

* Works correctly with Avisynth Alpha 4 (including mt). Doesn't work with previous alphas.

* Much cleaner and easy to understand codebase.

* No MMX-optimized versions. MMX is too old to support and is always slower than SSE2.

* **all luts**: faster lut calculation, faster startup, reduced memory footprint if the same lut is used for multiple planes or some planes aren't processed. For example ```mt_lutxyz(c1, c2, c3, "x y + z -")``` will use only 16MBs of memory instead of 48MBs.

* **mt_lutspa**: does not depend on source clip performance as it doesn't get requested at all (unless mode 2 is used). Always much faster (5-o9k times).

* **all filters**: faster modes 2, 4 and 5 (copy), negative (memset) modes.

* **mt_hysteresis**: 3-4 times better performance.

* **all luts**: performance in mode 3 with empty lut is now identical to mode 2. Thus ```mt_lut(chroma="128")``` is a bit faster than ```grayscale()``` instead of being much slower.

* **mt_merge**: luma=true now supports YV24.

* **mt_luts**: correct value is used as x. More info [here](http://forum.doom9.org/showpost.php?p=1637985&postcount=544).

* **sobel/roberts/laplace modes of mt_edge**: better performance when SSSE3 is available.

* **mt_edge("cartoon")**: 10 times faster when SSE2 is available.

* **all asm-optimized filters**: same performance on any resolution up to mod-1. Original masktools used unoptimized version for any non-mod8 clips.

_All filters were tested on Core i7 860. Performance might be a bit different on other CPUs._
