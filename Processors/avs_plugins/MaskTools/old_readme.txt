MaskTools v2 - alpha 2

Authors :

Kurosu : kurosu@inforezo.org, original author. Though all his code has been
rewritten since, for refactorisation purposes, his ideas still remain.

Manao : manao@melix.net, rewritter. Some of the filters are actually
written by me, though very few of them are from my original design.
I claim all responsibility for the bugs.

mg262 : some of the filters are originally his. I included them with his
authorization. If they are bugged, however, it's my fault :)

Didee : though not exactly a coder, he suffered so much bugs, and found
so many interesting ideas that he can't be left out of this disclaimer.
He managed to survive the bugs long enough to provide us with the 
LimitedSharpen script

mf : mf@onthanet.net, author of mfToon, and coauthor of vmToon.

vectrangle : coauthor of vmToon.

tsp : for the idea of the fast median finding when possible set of values
is small, for the second idea to speed it up a bit more, and finally for
the help debugging issues in a multithreaded environment

-----

Introduction.

Avisynth 2.5.6 is required. It might very well not work at all with previous version.

This is a brand new version of the MaskTools. Internally, all the code has been rewritten.
Externally, the name of the functions changes, some parameters / behavior too, but the
idea behind the MaskTools is still alive : allowing fast masks building / tweaking / 
processing.

The rewritting was necessary, to separate the actual filters from avisynth 2.5, which allows :
 * a core code that is portable ( linux / windows ). No more asm inline specific to Visual C++.
 * a core code that will be easily used for avisynth 3.0. 
 
The rewritting could have been made without changing the function names and behaviors, however,
I thought it was time to clean the set of filters from useless / deprecated filters, and to 
sanitize some of the filters. To make the transition to the v2 easier, I renamed all the functions,
which will allow the use of both old and new MaskTools dlls.

-----

Available filters :

 * masks
   + mt_edge
   + mt_motion
 * morphologics
   + mt_expand
   + mt_inpand
   + mt_inflate
   + mt_inflate
 * luts
   + mt_lut
   + mt_lutxy
   + mt_lutf
   + mt_luts
 * support
   + mt_makediff
   + mt_adddiff
   + mt_average
   + mt_clamp
 * merges
   + mt_merge
 * operators
   + mt_logic
   + mt_hysteresis
   + mt_invert
   + mt_binarize
 * convolutions
   + mt_convolution
 * blurs
   + mt_mappedblur
 * helpers
   + mt_circle
   + mt_square
   + mt_diamond
   + mt_losange
   + mt_rectangle
   + mt_ellipse
   + mt_polish
   
0. Common parameters

The filters still share the same common parameters. Here is the list ( default values in parenthesis ):
 * Y(3), U(1), V(1) : allow to specify which processing should be applied to each channel.
   + x = -255..0 means setting all the pixels of the channel to -x.
   + x = 1 means that we don't care about that channel. It's the fastest processing ( it does nothing at all ).
That also means that the output can't be predicted and reproduced.
   + x = 2 means that the channel is left untouched. Depending on the filter, an internal copy might
be needed.
   + x = 3 means that the actual processing of the filter is used
   + x = 4 means that the second clip channel is preserved ( only for filters with two or more input clips )
   + x = 5 means that the third clip channel is preserved ( only for filters with three or more input clips )
 * chroma("") : allow to set the mode of both chroma channels in a more user-friendly way. Possible strings
are "process" ( u=v=3 ), "copy" or "copy first" ( u=v=1 ), "copy second" ( u=v=4 ), "copy third" ( u=v=5 ),
"none" ( u=v=1 ) and finally, a number "xxx" ( u=v=-xxx )

 * offx(0), offy(0), w(-1), h(-1) : allow to select the area processed. w = -1 and h = -1 mean that the
whole width and height are used
   
1. Masks

mt_edge, mt_motion and mt_motion allow to create masks. They are the counterpart of EdgeMask, 
DEdgeMask, DEdgeMask2 and MotionMask. 

 * mt_edge : string mode("sobel"), int thY1(10), int thY2(10), int thC1(10), int thC2(10)
   + mode choses the 3x3 convolution kernel used for the mask computing. There are three predefined kernel,
"sobel", "roberts" and "laplace", and you can enter also a 3x3 custom kernel. "sobel" uses the
kernel "0 -1 0 -1 0 1 0 1 0", "roberts": "0 0 0 0 2 -1 0 -1 0" and "laplace": "1 1 1 1 -8 1 1 1 1".
The normalization factor of the kernel is automatically computed and ceiled to the closest power of 2,
to allow faster processing. You can specify your own normalization factor by adding it to the list of 
coefficients ( "1 1 1 1 -8 1 1 1 1 8" for example ).
   + thX1 is the low threshold and thX2 the high threshold. Under thX1, the pixel is set to zero, over thX2,
to 255, and inbetween, left untouched.
   + three other kernels exists : "prewitt", "cartoon" and "min/max". "prewitt" is a more robust kernel, while "cartoon"
behaves like "roberts", but takes only negative edges into account. Finally, "min/max" computes
the local contrast ( local max - local min ).

 * mt_motion : int thY1(10), int thY2(10), int thC1(10), int thC2(10), int thT(10)
    + thT decides whether the frame is a scene change or not. The mask is made blank if 
a scene change is detected, else, the mask is computed. 
    + thX1, thX2 work as for mt_edge and mt_mapped.
    
2. Morphologics

mt_expand, mt_inpand, mt_inflate and mt_deflate are the counterpart of expand, inpand, inflate and deflate.

 * mt_expand : int thY(255), int thC(255), string mode("square")
   + replaces the pixel by the local maximum. thX allows to limit the maximum change.
   + mode : one amongs "square", "horizontal", "vertical" and "both". "square" uses the maximum of the
local square, "horizontal" the left and right neighbours, "vertical" the top and bottom, and "both" is
a combination of "horizontal" and "vertical". Additionnaly, you can specify a custom mode, by giving
a serie of offset coordinates, one for each points you want to take into account ( "0 0 -1 0 1 0" is
equivalent to "horizontal" ).
 
 * mt_inpand : int thY(255), int thC(255), string mode("square")
   + replaces the pixel by the local minimum.
   
 * mt_inflate : int thY(255), int thC(255)
   + compute a local average by taking into account only the neighbourgh whose value is higher than the pixel.
'mode' isn't supported yet.

 * mt_deflate : int thY(255), int thC(255)
   + compute a local average by taking into account only the neighbourgh whose value is lower than the pixel.
'mode' isn't supported yet.

3. Luts

mt_lut and mt_lutxy are the counterpart of yv12lut and yv12lutxy. Reports to the documentation of these filters
to know how reverse polish notation works.

 * mt_lut : string expr("x"), string yexpr("x"), string uexpr("x"), string vexpr("x")
   + if yexpr, uexpr or vexpr aren't defined, expr is used instead.
   
 * mt_lutxy : string expr("x"), string yexpr("x"), string uexpr("x"), string vexpr("x")
 
 * mt_lutf : clip, clip, string mode("avg"), string expr("y"), string yexpr("y"), string uexpr("y"), string vexpr("y")
   + mt_lutf takes two clips into account. It'll compute the "mode" operation over the
 pixels of the first clip, and then apply the lut on the second clip, with x = computed "mode"
 value, and y the usual lut variable. "mode" can be "avg", "std", "min", "max", "range" = "max" - "min",
 and "med" ( median ).
 
 * mt_luts : clip, clip, string mode("avg"), string pixels(""), string expr("x"), string yexpr("x"), string uexpr("x"), string vexpr("x")
   + mt_luts takes two clips into account. It'll compute the "mode" operation over the
 result of the lut expression, with the pixel of the first clip as x, and the neighbouring 
 pixel of the second clip as y. Since that doesn't make any sense when explained so bluntly,
 lets give some examples : 
     - mt_luts( c1, c1, mode = "avg", pixels = mt_square( 1 ), expr = "y" ) does a convolution
 by a 3x3 kernel filled with ones.
     - mt_luts( c1, c1, mode = "min", pixels = mt_square( 1 ), expr = "y" ) does an inpand
     - mt_luts( c1, c1, mode = "range", pixels = mt_square( 1 ), expr = "y" ) does a
 mt_edge( mode = "min/max" )
     - mt_luts( c1, c1, mode = "std", pixels = mt_square( 1 ), expr = "y" ) gives the local
 standard deviation of the clip
     - mt_luts( c1, c1, mode = "max", pixels = mt_square( 1 ), expr = "x y - abs" ) gives
 the maximum difference between the surrounding pixels and the center. 
  
4. Supports

Supports filters are mmxed version of commonly used luts or combination of luts. All these are the work of mg262

 * mt_average : equivalent to mt_lutxy("x y + 2 /")
 
 * mt_makediff : equivalent to mt_lutxy("x y - 128 +")
 
 * mt_adddiff : equivalent to mt_lutxy("x y + 128 -")
 
 * mt_clamp : clip "bright", clip "dark", int overshoot(0), int undershoot(0)
   + clip the value of the clip between bright + overshoot and dark - undershoot

5. Merge

mt_merge is the counterpart of MaskedMerge.

 * mt_merge : clip clip1, clip clip2, clip mask, bool "luma"
   + merge clip1 and clip2 according to the mask. If "luma" is true, only the luma
mask plane is used, and both chroma planes are processed with it - without needing
to specify u=v=3 or chroma="process"
   
6. Operators

mt_logic, mt_hysteresis, mt_invert and mt_binarize are the counterpart of Logic, HysteresyMask, Invert and Binarize.

 * mt_logic : clip mask1, clip mask2, string mode("and")
   + apply the operator "mode" to merge both masks. 6 modes are available : "and", "or", "xor", "andn", "min" and "max".
   
 * mt_hysteresis : clip mask1, clip mask2
   + grows the first mask into the second.
   
 * mt_invert :
   + inverts the mask
   
 * mt_binarize : int threshold(128), bool upper(false)
   + "threshold" sets the threshold value. "Upper" decides how threshold works. If false, values
under the threshold are set to 0, over to 255. Else, it's reversed.

7. Convolutions

mt_convolution is the counterpart of YV12Convolution.

 * mt_convolution : clip, string horizontal("1 1 1"), string vertical("1 1 1"), bool saturate(true), float total(1.0f)
   + apply the convolution defined by t(horizontal) * vertical on the video. Both vectors must have an odd length.
   + if saturate, the result of the convolution is clipped to [0..255], else it's absolute value is clipped.
   + if total is defined, it overrides the values automatically computed to normalize the convolution
( the computed value is the sum of the coefficients of the kernel ( if it's 0, it becomes 1 ) )
   + computations occurs in float only if a float it used in the strings. If total is float, but none
of the coefficients are, total will be rounded to the closest integer
   
8. Blurs

mt_mappedblur implements a spatial blur.

 * mt_mappedblur : clip, clip map, string kernel("1 1 1 1 1 1 1 1 1"), string mode("replace")
   + 'map' is a clip of local thresholds.
   + 'mode' sets how pixels over the threshold are processed : "replace" means they are replace by the central value,
"dump" means they won't be taken into account. 
   + 'kernel' is the convolution kernel applied to the processed pixels
   
9. Helpers

Helpers filters don't have common parameters. They allow to create strings that can be passed as argument to other
filters of the set.

 * mt_circle : int radius(1), bool zero(true)
 * mt_square : int radius(1), bool zero(true)
 * mt_diamond : int radius(1), bool zero(true)
 * mt_ellipse : int hor_radius(1), int ver_radius(1), bool zero(true)
 * mt_rectangle : int hor_radius(1), int ver_radius(1), bool zero(true)
 * mt_losange : int hor_radius(1), int ver_radius(1), bool zero(true)
 * mt_polish : string infix("x")
    
------------

Conclusion

There is still some works to do, and things to test. At the moment, no bug are known, but nobody apart me tested it.
So bear in mind that this is an alpha yet, and that MaskTools 1.5.8 should be prefered for important stuff.

However, using this alpha will allow :
 * to make the set of filters more stable
 * to profit from the speed gain on some filters ( especially expand / inpand / edge / motion / merge )
 
There'll be a dedicated thread on doom9's forum to report bugs, and for feature request. 

In the todo list, at the moment :
 * better documentation. All stuff from 1.5.8 documentation that isn't deprecated / junked will be backported.
Avisynth formatting will be resumed too, instead of this crappy .txt
 * at the moment, there's mmx / isse optimizations. sse2 might come, with avisynth 2.6 ( for aligning stuff ).
 * add isse optimizations for mt_inpand / mt_expand new modes ( softwire ? )
 * add checks where needed.
 
-------

Developpers : 

The source code is released as gpl. The c++ code in itself isn't really interesting ( though some templates made
code factorization possible and relatively cleaned ). I adopted, as much as I could, a pure c++ approach, though
some parts could be a bit cleaner.

The interesting part is the nasm code. If you look at the code, you'll see it's heavyly macroized. I tried to create
macros that allowed "clean" loop unrolling, without too hassle. Also, I made a macro for convolution stuff,
that I'm rather proud of. That's what allowed to make easily the morphologic asm functions, and the edges' one.

--------

Changes from alpha 1 to alpha 2 :

 * added functions to luts : sin, abs, cos, tan, exp, log, acos, atan, asin
 * added "vertical", "horizontal" and "both" mode to mt_inpand / mt_expand
 * added mt_convolution
 * fixed mt_merge behavior for y, u, v = 2.
 * added y, u, v = 4, for masked merge : copy the second clip channel. It's worth for any two clips input filters.
 * internal changes ( code reorganization )
 
Changes from alpha 2 to alpha 3 :
 
 * Fixed : mt_invert, mt_binarize, mt_lutxy, which weren't working properly anymore
 * Fixed : offset created by incorrect rounding in mt_convolution
 * Fixed : mmx version of edges filters ( soft thresholding, and roberts )
 * Fixed : mmx version of motion edge ( soft thresholding )
 * added : mt_mappedblur
 
Changes from alpha 3 to alpha 4 :

 * added : custom modes for inpand / expand
 
Changes from alpha 4 to alpha 5 :
 * added : helpers for creating string for inpand / expand custom modes :
   - mt_circle
   - mt_square
   - mt_diamond
   - mt_ellipse
   - mt_rectangle
   - mt_losange
 * added : helper for lut : consersion from infix to reverse polish notation : 
   - mt_polish
   
Changes from alpha 5 to alpha 6 :
 * fixed : mt_polish was having some trouble with functions

Changes from alpha 6 to alpha 7 :
 * fixed : forgot to add functions to the parser. Thanks Didee for pointing that out.
 
Changes from alpha 7 to alpha 8 :
 * fixed : mt_edge in custom mode wasn't working properly 
 * fixed : mt_edge in custom mode, optimized wasn't working properly either
 * fixed : mt_lutxy was slow to load, it's better now
 
Changed from alpha 8 to alpha 9 :
 * fixed : mt_lut, mt_lutxy : even faster loading
 * fixed : mt_convolution : negative coefficients were offseted by 1
 * fixed : mt_convolution : division by zero if the sum of the coefficients was 0.
 
Changed from alpha 9 to alpha 10 :
 * fixed : offY was always set to offX
 * fixed : offset quirk
 * fixed : mt_convolution was crashing with floats
 * changed : luts' equal operator is now equivalent to abs(x-y) < 0.000001
 * added : bool saturate(true) parameter to mt_convolution
 * added : float total(1.0) parameter to mt_convolution

Changes from alpha 10 to alpha 11 :
 * fixed : mt_convolution's multiple instanciation bug
 
Changes from alpha 11 to alpha 12 :
 * fixed : bug with some width ( mod4 ) for the non processing mode ( != 1 or 3 )
 * changed : mt_merge order swapped for mask operation
 
Changes from alpha 12 to alpha 13 :
 * fixed : mt_merge order swapped for mask operation ( no comment... )

Changes from alpha 13 to alpha 14 :
 * fixed : random crashes with some width and asm functions ( thx Didee )
 
Changes from alpha 14 to alpha 15 :
 * fixed : bugs from inflate & deflate ( thx you know you )
 * reversed : inflate and deflate now match their masktools' v1 counterparts' behavior.
( if anybody used the new buggy one, let him speak quickly )

Changes from alpha 15 to alpha 16 :
 * fixed : some asm code used in invert, binarize and memset to a particular value.
Bug made the first 8 pixels of the picture to be incorrect. Also, avoid another nasty issue
that arise when cropping ( not my fault this time, though ).

Changes from alpha 16 to alpha 17 :
 * changed : behavior of mt_edge with a custom kernel : the automatic normalization factor
is now the sum of the absolute value of the coefficients, ceiled to the next power of two 
if that power is <= 128 ( else, it isn't ceiled ).
 * added : cartoon mode for mt_edge
 * added : modified mfToon script, for masktools v2. mfToonLite's speed goes from 30 fps
to 70 fps, mfToon from 4.5 to 6.5.

Changed from alpha 17 to alpha 18 :
 * added : mt_makediff, mt_adddiff, mt_average and mt_clamp, ported from mg262's
limitedsupport plugin. The asm code is his, though it has been ported to nasm. They
respectively amount to MakeDiff, AddDiff, SimpleAverage and Clamp.
 * added : mt_edge : "prewitt" kernel, taken from mg262's Prewitt filter. Unlike mg262's filter,
there's no multiplier ( it's always 1 ), but mt_edge's thresholds still apply. Results,
and speed, are identical except for the borders, which are now filtered.
 * added : "chroma" parameter, taken from mg262's excellent idea. It's a string that,
if used, overrides U and V values. It can be either "process", "copy", "copy first",
"copy second" or a number. "copy" and "copy second" work alike.
 * added : vmToon-0.74, adapted to masktools 2.0.
 * added : LimitedSharpenFaster, with LimitedSupport functions imported into the masktools.
 
Changes from alpha 18 to alpha 19 :
 * code refactoring
 * fixed : bug with asm and width lower than 64
 * fixed : doesn't prepend (0, 0) pixel to the forms helpers
 * added : "min/max" mode to mt_edge. The edge value is local max - local min ( taken on a
3x3 square ).
 * added : mt_lutf : a frame lut, see the description above
 * added : mt_luts : a spatial lut, see the description above

Changed from alpha 19 to alpha 20 :
 * fixed : huge bug preventing most filters from working

Changed from alpha 20 to alpha 21 :
 * fixed : two & three input clips filters where requesting wrong frames
leading to ghost artefacts.

Changed from alpha 21 to alpha 22 : 
 * added : "med"/"median" mode to luts/lutf
 * changed : luts doesn't necessarily consider the center pixel
 * changed back : forms helpers prepends (0, 0). 
 * changed : forms helpers now have a bool "zero" parameter, defaulted to true
 * added : bool "luma" parameter to mt_merge, which makes it use the luma mask for
all three planes, and which forces chroma modes to "process" ( u=v=3 )

Changed from alpha 22 to alpha 23 :
 * fix & speed up : median mode, thanks to tsp's insightfull remark. Note to self : think
less like a mathematician, and more like a programmer. Simpler, faster & not bugged.

Changed from alpha 23 to alpha 24 :
 * fixed : issues with MT.dll ( thanks tsp, Boulder, vanessam and all those who suffered the bug )
 * fixed : check for YV12 colorspace, and report an error if it isn't ( thanks Boulder )
 * speed up : median mode for luts ( once again, thanks to tsp )
