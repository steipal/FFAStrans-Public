Some general information first.

The recording process is the following:
SDR :
[Camera sensor] -> Linear R,G,B -> OETF -> Non linear R',G',B' -> Color Matrix -> Y',C'r,C'b
Y',C'r,C'b -> Inv Color Matrix -> Non linear R',G',B' -> OETF-1 -> Linear R,G,B
HDR :
[Camera sensor] -> Linear R,G,B -> OOTF (PQ/HLG) -> EOTF-1 (PQ/HLG) -> Non linear R',G',B' -> Color Matrix -> Y',C'r,C'b
Y',C'r,C'b -> Inv Color Matrix -> Non linear R',G',B' -> EOTF (PQ/HLG) -> Inv OOTF (PQ/HLG) -> Linear R,G,B

We can thought that at the level of Linear R,G,B, we have directly the "original" light information.
Unfortunately not. The R,G,B provided by the Camera sensor are linked to chromaticity parameters
(things like white color T°, etc...). So, the more appropriate color space closest to the "original"
light information seems the XYZ color space.

In the Document directory i've put a pdf file describing how things work,
with detailled explainations and formula.

Note about HDR HLG:
For speed-up:
8 bits input use 3D lookup (startup is slow).
10 and 12 bits use 2D lookup (startup is slow),
but there is a resolution loss noticeable effect on low values.

Note about YV12/YV16/YV24 input/ouput:
For ConvertYUVtoxxx functions, convertion to YV24 if input is not YV24 is "quick".
If you want a true correct precise/perfect convertion, i would avise you to use
a resampler and feed directly to YV24.
For ConvertxxxtoYUV functions, if you choose an ouput different from YV24, same
remark, convertion is "quick".
If you want a true correct precise/perfect convertion, i would avise you
to ouput to YV24, and use a resampler to achieve the real output format you want.

Functions inside this plugin:


**************************************
**      ConvertYUVtoLinearRGB       **
**************************************

ConvertYUVtoLinearRGB(int Color,int OutputMode,int HDRMode,float HLGLb,float HLGLw,int HLGColor,
     bool OOTF,bool EOTF,bool fullrange,bool mpeg2c,int threads,bool logicalCores,bool MaxPhysCore,
     bool SetAffinity,bool sleep,int prefetch,int ThreadLevel)

Accepted input: Planar YUV 8 to 16 bits.

   Color -
      Set the color mode of the data.
         0: BT2100
         1: BT2020
         2: BT709
         3: BT601_525
         4: BT601_625

       Default: 2 (int)

   OutputMode -
      Set the output data mode.
         0: No change : Input 8 Bits -> Output : RGB32, Input > 8 Bits -> Output : RGB64
	 1: The ouput will be RGB64
	 2: The ouput will be RGBPS (Planar RGB float)

       Default: 0 (int)

   HDRMode -
      Has effect only if Color=0.
         0: PQ mode.
         1: HLG normalized 10000 cd/m² mode.
         2: HLG not normalized.

       Default: 0 (int)

   HLGLb -
      Set the black level in cd/m² for HLG mastering linear display value (Fd).
      Has effect only if HDRMode is set to 1 or 2.

       Default: 0.05 (float)

   HLGLw -
      Set the white level in cd/m² for HLG mastering linear display value (Fd).
      Has effect only if HDRMode is set to 1 or 2.

       Default: 1000.0 (float)

   HLGColor -
      Set the color space to use for the OOTF HLG function. Values are the same than Color

       Default: 1 (int)

   OOTF -
      Color = 0:

        HDRMode = 0, 1, 2:
      If set to false, the OOTF-1 step will be skipped during the linear convertion.
      The output will be the linear displayed data (Fd) instead of the linear scene data.

      If both EOTF and OOTF are false output will be standard RGB.

      =================
      Color <> 0:
      If EOTF is false, nothing is done whatever OOTF => Output will be standard RGB.
      If OOTF is false and EOTF is true, the output will be the linear displayed data (Fd).

       Default: true (bool)

   EOTF -
      Color = 0:

        HDRMode = 0:
      If set to false, the EOTF step will be skipped during the linear convertion.
      The output will not be consistant with anything standard.

        HDRMode = 1 or 2: No effect.

      If both EOTF and OOTF are false output will be standard RGB.

      =================
      Color <> 0:
      If EOTF is false, nothing is done whatever OOTF => Output will be standard RGB.
      If OOTF is false, and EOTF is true, the output will be the linear displayed data (Fd).

       Default: true (bool)

   fullrange -
      If set to true, the YUV input data will be considered full range value.

       Default: false (bool)

   mpeg2c -
      Has effect only if input is YV12. If set to false, chroma placement will be
      considered mpeg-1, otherwise mpeg-2.
      Not implemented yet.

       Default: true (bool)

   threads -
      Controls how many threads will be used for processing. If set to 0, threads will
      be set equal to the number of detected logical or physical cores,according logicalCores parameter.

      Default: 0  (int)

   logicalCores -
      If threads is set to 0, it will specify if the number of threads will be the number
      of logical CPU (true) or the number of physical cores (false). If your processor doesn't
      have hyper-threading or threads<>0, this parameter has no effect.

      Default: true (bool)

   MaxPhysCore -
      If true, the threads repartition will use the maximum of physical cores possible. If your
      processor doesn't have hyper-threading or the SetAffinity parameter is set to false,
      this parameter has no effect.

      Default: true (bool)

   SetAffinity -
      If this parameter is set to true, the pool of threads will set each thread to a specific core,
      according MaxPhysCore parameter. If set to false, it's leaved to the OS.
      If prefecth>number of physical cores, it's automaticaly set to false.

      Default: false (bool)

  sleep -
      If this parameter is set to true, once the filter has finished one frame, the threads of the
      threadpool will be suspended (instead of still running but waiting an event), and resume when
      the next frame will be processed. If set to false, the threads of the threadpool are always
      running and waiting for a start event even between frames.

      Default: false (bool)

  prefetch - (added negative trim feature)
      This parameter will allow to create more than one threadpool, to avoid mutual resources acces
      if "prefetch" is used in the avs script.
      0 : Will set automaticaly to the prefetch value use in the script. Well... that's what i wanted
          to do, but for now it's not possible for me to get this information when i need it, so, for
          now, 0 will result in 1. For now, if you're using "prefetch" in your script, put the same
          value on this parameter.

      Default: 0

  ThreadLevel -
      This parameter will set the priority level of the threads created for the processing (internal
      multithreading). No effect if threads=1.
      1 : Idle level.
      2 : Lowest level.
      3 : Below level.
      4 : Normal level.
      5 : Above level.
      6 : Highest level.
      7 : Time critical level (WARNING !!! use this level at your own risk)

      Default : 6

The logicalCores, MaxPhysCore, SetAffinity and sleep are parameters to specify how the pool of thread
will be created and handled, allowing if necessary each people to tune according his configuration.


**************************************
**      ConvertLinearRGBtoYUV       **
**************************************

ConvertLinearRGBtoYUV(int Color,int OutputMode,int HDRMode,float HLGLb, float HLGLw,int HLGColor,
     bool OOTF,bool EOTF,bool fullrange,bool mpeg2c,bool fastmode,int threads,bool logicalCores,
     bool MaxPhysCore,bool SetAffinity,bool sleep,int prefetch,int ThreadLevel)

Accepted input: RGB32, RGB64 and Planar float RGB.

   Color -
      Set the color mode of the data.
         0: BT2100
         1: BT2020
         2: BT709
         3: BT601_525
         4: BT601_625

       Default: 2 (int)

   OutputMode -
      Set the output data mode. IF input is 8 bits output is 8 bits, 16 bits otherwise.
         0: YV24
	 1: YV16
	 2: YV12
       Default: 0 (int)

   OOTF -
      Color = 0:

        HDRMode = 0, 1, 2:
      If set to false, the OOTF step will be skipped during the linear convertion.
      Use this setting if the input is linear displayed data (Fd) instead of linear scene data.

      If both EOTF and OOTF are false, correct ouput if input is standard RGB.

      =================
      Color <> 0:
      If EOTF is false, nothing is done whatever OOTF, correct ouput if input is standard RGB.
      OOTF is false and EOTF is true :
      Use this setting if the input is linear displayed data (Fd) instead of linear scene data.

       Default: true (bool)

   EOTF -
      Color = 0:

        HDRMode = 0:
      If set to false, the EOTF-1 step will be skipped during the linear convertion.
      The output will not be consistant with anything standard.

        HDRMode = 1 or 2: no effect.

      If both EOTF and OOTF are false, correct ouput if input is standard RGB.

      =================
      Color <> 0 :
      If EOTF is false, nothing is done whatever OOTF, correct ouput if input is standard RGB.
      OOTF is false and EOTF is true :
      Use this setting if the input is linear displayed data (Fd) instead of linear scene data.

       Default: true (bool)

   fullrange -
      If set to true, the YUV output data will be set full range.

       Default: false (bool)

   mpeg2c -
      Has effect only if output is YV12. If set to false, chroma convertion will be mpeg-1, otherwise mpeg-2.
      Not implemented yet.

       Default: true (bool)

   fastmode -
      Has effect only if input is float. If set to true, the de-linear convertion will be done using
      a lookup table of 20 bits input (mantisse size of float is 24 bits). Otherwise, the function will
      be calculated each time, this will create a huge slowdown.

       Default: true (bool)

The others parameters are identical to ConvertYUVtoLinearRGB.


**************************************
**         ConvertYUVtoXYZ          **
**************************************

ConvertYUVtoXYZ(int Color,int OutputMode,int HDRMode,float HLGLb,float HLGLw,float Crosstalk,
     int HLGColor,bool OOTF,bool EOTF,bool fullrange,bool mpeg2c,
     float Rx,float Ry,float Gx,float Gy,float Bx,float By,float Wx,float Wy,
     int threads,bool logicalCores,bool MaxPhysCore,bool SetAffinity,bool sleep,
     int prefetch,int ThreadLevel)

Accepted input: Planar YUV 8 to 16 bits.
The output will be tagged RGB even if data is XYZ.

   Crosstalk -
      Coeff for the crosstalk R,G,B matrix (for Method C of BT2446). Value 0.0 to 0.33.
      Will apply a crosstalk matrix on RGB before XYZ matrix convertion.
      Avoid value over 0.3 in 8 bits mode. 0.0 means no crosstalk between R,G,B.

       Default: 0.0 (float)

   Rx,Ry,Gx,Gy,Bx,By,Wx,Wy -
      These parameters allow to configure the chromaticity coordinates Red point, Green point, Blue point
      and White point. If not set, the values defined in the BT.xxxx of the Color parameter are used.

       Default: According Color parameter (float)

The others parameters are identical to ConvertYUVtoLinearRGB.


**************************************
**         ConvertXYZtoYUV          **
**************************************

ConvertXYZtoYUV(int Color,int OutputMode,int HDRMode,float HLGLb,float HLGLw,float Crosstalk,
     int HLGColor,bool OOTF,bool EOTF,bool fullrange,bool mpeg2c,bool fastmode,
     float Rx,float Ry,float Gx,float Gy,float Bx,float By,float Wx,float Wy,
     int pColor,float pRx,float pRy,float pGx,float pGy,float pBx,float pBy,float pWx,float pWy,
     int threads,bool logicalCores,bool MaxPhysCore,bool SetAffinity,bool sleep,
     int prefetch,int ThreadLevel)

Accepted input: RGB32, RGB64 and Planar float RGB.

   Crosstalk -
      Coeff for the crosstalk R,G,B matrix (for Method C of BT2446). Value 0.0 to 0.33.
      Will apply a reverse crosstalk matrix on RGB after XYZ matrix convertion.
      The value must be the same than used on YUVtoXYZ.
      Avoid value over 0.3 in 8 bits mode. 0.0 means no crosstalk between R,G,B.

       Default: 0.0 (float)

   pColor -
      Color mode used in YUV/RGBtoXYZ.
         0 : BT2100
         1 : BT2020
         2 : BT709
         3 : BT601_525
         4 : BT601_625

       Default: 2 if Color=0, 0 otherwise.


   pRx,pRy,pGx,pGy,pBx,pBy,pWx,pWy -
      Chromaticity datas used in previous YUV/RGBtoXYZ.

       Default: According pColor parameter (float)


The others parameters are identical to ConvertLinearRGBtoYUV.


**************************************
**         ConvertRGBtoXYZ          **
**************************************

ConvertRGBtoXYZ(int Color,int OutputMode,int HDRMode,float HLGLb, float HLGLw,float Crosstalk,
     int HLGColor,bool OOTF,bool EOTF,bool fastmode,
     float Rx,float Ry,float Gx,float Gy,float Bx,float By,float Wx,float Wy,
     int threads,bool logicalCores,bool MaxPhysCore,bool SetAffinity,bool sleep,
     int prefetch,int ThreadLevel)

Accepted input: RGB32, RGB64 and Planar float RGB.
The output will be tagged RGB even if data is XYZ.

The parameters are identical to ConvertYUVtoXYZ.


**************************************
**         ConvertXYZtoRGB          **
**************************************

ConvertXYZtoRGB(int Color,int OutputMode,int HDRMode,float HLGLb, float HLGLw,float Crosstalk,
     int HLGColor,bool OOTF,bool EOTF,bool fastmode,
     float Rx,float Ry,float Gx,float Gy,float Bx,float By,float Wx,float Wy,
     int pColor,float pRx,float pRy,float pGx,float pGy,float pBx,float pBy,float pWx,float pWy,
     int threads,bool logicalCores,bool MaxPhysCore,bool SetAffinity,bool sleep,
     int prefetch,int ThreadLevel)

Accepted input: RGB32, RGB64 and Planar float RGB.

   OutputMode -
      Set the output data mode.
         0: No change
	 1: Input 8 to 16 bits : no change, Input Planar float RGB -> Outpout RGB64.
       Default: 0 (int)


The others parameters are identical to ConvertXYZtoYUV.


********************************************
**       ConvertXYZ_Scale_HDRtoSDR        **
********************************************

ConvertXYZ_Scale_HDRtoSDR(float Coeff_X, float Coeff_Y, float Coeff_Z,
     int threads,bool logicalCores,bool MaxPhysCore,bool SetAffinity,bool sleep,
     int prefetch,int ThreadLevel)
     
Accepted input: RGB64 and Planar float RGB.

For now, it's just a linear scalling, just for testing. Formula is just Out_X=Coeff_X*In_X (etc...).

   Coeff_X -
      Linear scalar value used on X plane.
      
       Default: 100.0 (float)

   Coeff_Y -
      Linear scalar value used on Y plane.
      
       Default: Coeff_X (float)

   Coeff_Z -
      Linear scalar value used on Z plane.
      
       Default: Coeff_X (float)

The others parameters are identical to ConvertYUVtoLinearRGB.


********************************************
**       ConvertXYZ_Scale_SDRtoHDR        **
********************************************

ConvertXYZ_Scale_SDRtoHDR(float Coeff_X, float Coeff_Y, float Coeff_Z,
     int threads,bool logicalCores,bool MaxPhysCore,bool SetAffinity,bool sleep,
     int prefetch,int ThreadLevel)
     
Accepted input: RGB64 and Planar float RGB.

Produce linear scalling. Formula is just Out_X=In_X/Coeff_X (etc...).

   Coeff_X -
      Linear scalar value used on X plane.
      
       Default: 100.0 (float)

   Coeff_Y -
      Linear scalar value used on Y plane.
      
       Default: Coeff_X (float)

   Coeff_Z -
      Linear scalar value used on Z plane.
      
       Default: Coeff_X (float)

The others parameters are identical to ConvertYUVtoLinearRGB.


********************************************
**       ConvertXYZ_Hable_HDRtoSDR        **
********************************************

ConvertXYZ_Hable_HDRtoSDR(float exposure_X,float whitescale_X,float a_X,float b_X,float c_X,
     float d_X,float e_X,float f_X,float exposure_Y,float whitescale_Y,float a_Y,float b_Y,float c_Y,
     float d_Y,float e_Y,float f_Y,float exposure_Z,float whitescale_Z,float a_Z,float b_Z,float c_Z,
     float d_Z,float e_Z,float f_Z,int pColor,float pRx,float pRy,float pGx,float pGy,
     float pBx,float pBy,bool fastmode,
     int threads,bool logicalCores,bool MaxPhysCore,bool SetAffinity,bool sleep,
     int prefetch,int ThreadLevel)
     
Accepted input: RGB64 and Planar float RGB.

Hable tonemap, you can have different parameters for each plane, if you want.

   exposure_X -
      Exposure value used on X plane.
      
       Default: 2.0 (float)

   whitescale_X -
      White scale value used on X plane.
      
       Default: 11.2 (float)

   a_X -
      a value used on X plane.
      
       Default: 0.15 (float)

   b_X -
      b value used on X plane.
      
       Default: 0.5 (float)

   c_X -
      c value used on X plane.
      
       Default: 0.1 (float)

   d_X -
      d value used on X plane.
      
       Default: 0.2 (float)

   e_X -
      e value used on X plane.
      
       Default: 0.02 (float)

   f_X -
      f value used on X plane.
      
       Default: 0.3 (float)

   exposure_Y,whitescale_Y,a_Y,b_Y,c_Y,d_Y,e_Y,f_Y
      Values used on Y plane.

       Default: exposure_X,whitescale_X,a_X,b_X,c_X,d_X,e_X,f_X (float)

   exposure_Z,whitescale_Z,a_Z,b_Z,c_Z,d_Z,e_Z,f_Z
      Values used on Z plane.

       Default: exposure_X,whitescale_X,a_X,b_X,c_X,d_X,e_X,f_X (float)

The others parameters are identical to ConvertXYZtoRGB.


********************************************
**       ConvertRGB_Hable_HDRtoSDR        **
********************************************

ConvertRGB_Hable_HDRtoSDR(float exposure_R,float whitescale_R,float a_R,float b_R,float c_R,
     float d_R,float e_R,float f_R,float exposure_G,float whitescale_G,float a_G,float b_G,float c_G,
     float d_G,float e_G,float f_G,float exposure_B,float whitescale_B,float a_B,float b_B,float c_B,
     float d_B,float e_B,float f_B,bool fastmode,
     int threads,bool logicalCores,bool MaxPhysCore,bool SetAffinity,bool sleep,
     int prefetch,int ThreadLevel)
     
Accepted input: RGB64 and Planar float RGB.

Hable tonemap, you can have different parameters for each plane, if you want.

   exposure_R -
      Exposure value used on R plane.
      
       Default: 2.0 (float)

   whitescale_R -
      White scale value used on R plane.
      
       Default: 11.2 (float)

   a_R -
      a value used on R plane.
      
       Default: 0.15 (float)

   b_R -
      b value used on R plane.
      
       Default: 0.5 (float)

   c_R -
      c value used on R plane.
      
       Default: 0.1 (float)

   d_R -
      d value used on R plane.
      
       Default: 0.2 (float)

   e_R -
      e value used on R plane.
      
       Default: 0.02 (float)

   f_R -
      f value used on R plane.
      
       Default: 0.3 (float)

   exposure_G,whitescale_G,a_G,b_G,c_G,d_G,e_G,f_G
      Values used on G plane.

       Default: exposure_R,whitescale_R,a_R,b_R,c_R,d_R,e_R,f_R (float)

   exposure_B,whitescale_B,a_B,b_B,c_B,d_B,e_B,f_B
      Values used on B plane.

       Default: exposure_R,whitescale_R,a_R,b_R,c_R,d_R,e_R,f_R (float)

The others parameters are identical to ConvertLinearRGBtoYUV.


********************************************
**       ConvertXYZ_Mobius_HDRtoSDR       **
********************************************

ConvertXYZ_Mobius_HDRtoSDR(float exposure_X,float transition_X,float peak_X,
     float exposure_Y,float transition_Y,float peak_Y,float exposure_Z,float transition_Z,float peak_Z,
     int pColor,float pRx,float pRy,float pGx,float pGy,float pBx,float pBy,bool fastmode,
     int threads,bool logicalCores,bool MaxPhysCore,bool SetAffinity,bool sleep,
     int prefetch,int ThreadLevel)
     
Accepted input: RGB64 and Planar float RGB.

Mobius tonemap, you can have different parameters for each plane, if you want.

   exposure_X -
      Exposure value used on X plane.
      
       Default: 2.0 (float)

   transition_X -
      Transition value used on X plane.
      
       Default: 0.3 (float)

   peak_X -
      Peak value used on X plane.
      
       Default: 1.0 (float)

   exposure_Y,transition_Y,peak_Y
      Values used on Y plane.

       Default: exposure_X,transition_X,peak_X (float)

   exposure_Z,transition_Z,peak_Z
      Values used on Z plane.

       Default: exposure_X,transition_X,peak_X (float)

The others parameters are identical to ConvertXYZtoRGB.


********************************************
**       ConvertRGB_Mobius_HDRtoSDR       **
********************************************

ConvertRGB_Mobius_HDRtoSDR(float exposure_R,float transition_R,float peak_R,
     float exposure_G,float transition_G,float peak_G,float exposure_B,float transition_B,
     float peak_B,bool fastmode,
     int threads,bool logicalCores,bool MaxPhysCore,bool SetAffinity,bool sleep,
     int prefetch,int ThreadLevel)
     
Accepted input: RGB64 and Planar float RGB.

Mobius tonemap, you can have different parameters for each plane, if you want.

   exposure_R -
      Exposure value used on R plane.
      
       Default: 2.0 (float)

   transition_R -
      Transition value used on R plane.
      
       Default: 0.3 (float)

   peak_R -
      Peak value used on R plane.
      
       Default: 1.0 (float)

   exposure_G,transition_G,peak_G
      Values used on G plane.

       Default: exposure_R,transition_R,peak_R (float)

   exposure_B,transition_B,peak_B
      Values used on B plane.

       Default: exposure_R,transition_R,peak_R (float)

The others parameters are identical to ConvertLinearRGBtoYUV.


********************************************
**      ConvertXYZ_Reinhard_HDRtoSDR      **
********************************************

ConvertXYZ_Reinhard_HDRtoSDR(float exposure_X,float contrast_X,float peak_X,
     float exposure_Y,float contrast_Y,float peak_Y,float exposure_Z,float contrast_Z,float peak_Z,
     int pColor,float pRx,float pRy,float pGx,float pGy,float pBx,float pBy,bool fastmode,
     int threads,bool logicalCores,bool MaxPhysCore,bool SetAffinity,bool sleep,
     int prefetch,int ThreadLevel)
     
Accepted input: RGB64 and Planar float RGB.

Reinhard tonemap, you can have different parameters for each plane, if you want.

   exposure_X -
      Exposure value used on X plane.
      
       Default: 2.0 (float)

   contrast_X -
      Contrast value used on X plane.
      
       Default: 0.5 (float)

   peak_X -
      Peak value used on X plane.
      
       Default: 1.0 (float)

   exposure_Y,contrast_Y,peak_Y
      Values used on Y plane.

       Default: exposure_X,contrast_X,peak_X (float)

   exposure_Z,contrast_Z,peak_Z
      Values used on Z plane.

       Default: exposure_X,contrast_X,peak_X (float)

The others parameters are identical to ConvertXYZtoRGB.


********************************************
**      ConvertRGB_Reinhard_HDRtoSDR      **
********************************************

ConvertRGB_Reinhard_HDRtoSDR(float exposure_R,float contrast_R,float peak_R,
     float exposure_G,float contrast_G,float peak_G,float exposure_B,float contrast_B,
     float peak_B,bool fastmode,
     int threads,bool logicalCores,bool MaxPhysCore,bool SetAffinity,bool sleep,
     int prefetch,int ThreadLevel)
     
Accepted input: RGB64 and Planar float RGB.

Reinhard tonemap, you can have different parameters for each plane, if you want.

   exposure_R -
      Exposure value used on R plane.
      
       Default: 2.0 (float)

   contrast_R -
      Contrast value used on R plane.
      
       Default: 0.5 (float)

   peak_R -
      Peak value used on R plane.
      
       Default: 1.0 (float)

   exposure_G,contrast_G,peak_G
      Values used on G plane.

       Default: exposure_R,contrast_R,peak_R (float)

   exposure_B,contrast_B,peak_B
      Values used on B plane.

       Default: exposure_R,contrast_R,peak_R (float)

The others parameters are identical to ConvertLinearRGBtoYUV.


*******************************************************
**      ConvertLinearRGBtoYUV_BT2446_A_HDRtoSDR      **
*******************************************************

ConvertLinearRGBtoYUV_BT2446_A_HDRtoSDR(float Lhdr,float Lsdr,float CoeffAdj,bool fastmode,
     int threads,bool logicalCores,bool MaxPhysCore,bool SetAffinity,bool sleep,
     int prefetch,int ThreadLevel)
     
Accepted input: RGB64 and Planar float RGB.
WARNING : Input must be linear DISPLAYED data, so produced by
ConvertYUVtoLinearRGB with OOTF=false.
Output : YV24 16 bits.

HDR to SDR convertion, using the REC-BT.2446 method A tonemap.

   Lhdr -
      HDR max mastering level cd/m².
      
       Default: 1000.0 (float)

   Lsdr -
      SDR white targeting level cd/m².
      
       Default: 100.0 (float)
   
   CoeffAdj -
      This is not part of BT2446 A method, added, multiply the data by the value.

       Default: 1.0

The others parameters are identical to ConvertLinearRGBtoYUV.


*******************************************
**      ConverXYZ_BT2446_C_HDRtoSDR      **
*******************************************

ConverXYZ_BT2446_C_HDRtoSDR(bool ChromaC,bool PQMode,float Lhdr,float Lsdr,float pct_ref,
     float pct_ip,float pct_wp,float pct_sdr_skin,float pct_hdr_skin,float WhiteShift,
     int pColor,float pRx,float pRy,float pGx,float pGy,float pBx,float pBy,bool fastmode,
     int threads,bool logicalCores,bool MaxPhysCore,bool SetAffinity,bool sleep,
     int prefetch,int ThreadLevel)

Accepted input: RGB64 and Planar float RGB.
WARNING : Input must be linear DISPLAYED data, so produced by
ConvertYUVtoLinearRGB with OOTF=false.

You have to read the BT2446 C method to understand properly the purpose of the parameters.

   ChromaC -
      Allow the "Optional processing of chroma correction above HDR Reference White".
      Warning: Will create a slowdown.
      
       Default: false (bool)

   PQMode -
      Adjust some parameters to allow processing of PQ video.
      
       Default: false (bool)

   Lhdr -
      HDR max mastering level cd/m².
      
       Default: 10000.0 (float) if PQMode=true, else 1000.0 (float)

   Lsdr -
      SDR white targeting level cd/m².
      
       Default: 100.0 (float)

   pct_ref -
      Used to compute the Y HDR Reference White.
      
       Default: 0.58 (float) if PQMode=true, else 0.75 (float).

   pct_ip -
      Used to compute the SDR inflection point.
      
       Default: 0.80 (float).

   pct_wp -
      Used to compute the SDR white level corresponding to the HDR Reference White.
      
       Default: 0.96 (float).

   pct_sdr_skin -
      Value for SDR skin tones described in Annex 4 of Report ITU-R BT.2408.
      
       Default: 0.70 (float).

   pct_hdr_skin -
      Value for HDR skin tones described in Annex 4 of Report ITU-R BT.2408.
      
       Default: 0.44 (float) if PQMode=true, else 0.50 (float).

   WhiteShift -
      Value used for white shift in formula (26).
      
       Default: 0.00 (float).

The filter will automaticaly compute k1 to k4 according the input parameters.
There is no real check (and there will not be) for sanity values of the parameters,
so, if you put nonsense values, it's not impossible that you'll create a crash or garbage output.

The others parameters are identical to ConvertXYZtoRGB.


*******************************************
**       ConvertXYZ_ACES_HDRtoSDR        **
*******************************************

ConvertXYZ_ACES_HDRtoSDR(float a_X,float b_X,float c_X,float d_X,float e_X,
     float a_Y,float b_Y,float c_Y,float d_Y,float e_Y,float a_Z,float b_Z,
     float c_Z,float d_Z,float e_Z,float exposure_X,float exposure_Y,float exposure_Z,
     int pColor,float pRx,float pRy,float pGx,
     float pGy,float pBx,float pBy,bool fastmode,
     int threads,bool logicalCores,bool MaxPhysCore,bool SetAffinity,bool sleep,
     int prefetch,int ThreadLevel)
     
Accepted input: RGB64 and Planar float RGB.

ACES XYZ tonemap, you can have different parameters for each plane, if you want.
Calcul : v=(X,Y,Z)*exposure, (v*(v+a)+b)/(v*(c*v+d)+e)

   a_X -
      a value used on X plane.
      
       Default: 0.0245786 (float)

   b_X -
      b value used on X plane.
      
       Default: -0.000090537 (float)

   c_X -
      c value used on X plane.
      
       Default: 0.983729 (float)

   d_X -
      d value used on X plane.
      
       Default: 0.4329510 (float)

   e_X -
      e value used on X plane.
      
       Default: 0.238081 (float)

   exposure_X -
      exposure used on X plane.

       Default: 1.0 (float)

   a_Y,b_Y,c_Y,d_Y,e_Y,exposure_Y
      Values used on Y plane.

       Default: a_X,b_X,c_X,d_X,e_X,exposure_X (float)

   a_Z,b_Z,c_Z,d_Z,e_Z,exposure_Z
      Values used on Z plane.

       Default: a_X,b_X,c_X,d_X,e_X,exposure_X (float)

The others parameters are identical to ConvertXYZtoRGB.


*******************************************
**       ConvertRGB_ACES_HDRtoSDR        **
*******************************************

ConvertRGB_ACES_HDRtoSDR(float a_R,float b_R,float c_R,float d_R,float e_R,
     float a_G,float b_G,float c_G,float d_G,float e_G,float a_B,float b_B,
     float c_B,float d_B,float e_B,float exposure_R,float exposure_G,
     float exposure_B,bool fastmode,
     int threads,bool logicalCores,bool MaxPhysCore,bool SetAffinity,bool sleep,
     int prefetch,int ThreadLevel)
     
Accepted input: RGB64 and Planar float RGB.

ACES RGB tonemap, you can have different parameters for each plane, if you want.
Calcul : v=(R,G,B)*exposure, (v*(a*v+b))/(v*(c*v+d)+e)

   a_R -
      a value used on R plane.
      
       Default: 2.51 (float)

   b_R -
      b value used on R plane.
      
       Default: 0.03 (float)

   c_R -
      c value used on R plane.
      
       Default: 2.43 (float)

   d_R -
      d value used on R plane.
      
       Default: 0.59 (float)

   e_R -
      e value used on R plane.
      
       Default: 0.14 (float)

   exposure_R -
      exposure used on R plane.

       Default: 1.0 (float)

   a_G,b_G,c_G,d_G,e_G,exposure_G
      Values used on G plane.

       Default: a_R,b_R,c_R,d_R,e_R,exposure_R (float)

   a_B,b_B,c_B,d_B,e_B,exposure_B
      Values used on B plane.

       Default: a_R,b_R,c_R,d_R,e_R,exposure_R (float)

The others parameters are identical to ConvertLinearRGBtoYUV.


*************************************************************

Note :
======
ConvertXYZ_Scalar_HDRtoSDR is a simple scalar function, i've made just to see what result it produces.
Don't have expectations on this plugin, but if by luck it works for you...

*************************************************************

Note about pColor (and pRx,...)  parameters :
=============================================
These parameters are here just to know the input range value in 8-16 bits mode, because contrary
to RGB where range value is always [0.0,1.0], for XYZ the range value can vary according
the chromaticity parameters and white point value.
They have no other effect than setting, for example, in 8 bits, for X 0=0.0, 255=0.96.
These parameters have no effect in float mode.

*************************************************************

Note about linear values :
==========================

For ConvertYUVtoxxx functions, the output is:

For HDR data (Color=0), HDRMode=(0 or 1),
the output (R,G,B stage) is normalized for 1.0=10000 cd/m² (or 255 or 65535).

For SDR data (Color<>0),
the output (R,G,B stage) is normalized for 1.0=100 cd/m² (or 255 or 65535).

For ConvertxxxtoYUV functions, the input is:

For HDR data (Color=0), HDRMode=(0 or 1),
the input (R,G,B stage) is normalized for 1.0=10000 cd/m² (or 255 or 65535).

For SDR data (Color<>0),
the input (R,G,B stage) is normalized for 1.0=100 cd/m² (or 255 or 65535).

*************************************************************

Note about Chromaticity parameters
==================================
On HDR stream, SEI mastering parameters provide the chromaticity parameters used.
Even if BT2100 has default value, i think it will produce optimal result in RGB/YUV
to XYZ convertion if SEI mastering parameters are used instead of default BT2100 values.
All the BTxxxx use D65 white point, if the SEI parameters are allready set to it, no use to
specify them.
These parameters can be get using mediainfo on the HDR stream.
Another way to get them, it's if you're using DGIndexNV, on HEVC HDR stream.
In that case, you'll have in the DGI file this line (for exemple) :

MASTERING 13250 34500 7500 3000 34000 16000 15635 16450 40000000 50

The values are the following:

MASTERING GreenX GreenY BlueX BlueY RedX RedY WhiteX WhiteY MaxMasteringLevel MinMasteringLevel

The GreenX GreenY BlueX BlueY RedX RedY WhiteX WhiteY are by 0.00002 steps.
The MaxMasteringLevel MinMasteringLevel are by 0.0001 steps.

In our exemple, it will result :
Gx: 0.265
Gy: 0.690
Bx: 0.150
By: 0.060
Rx: 0.680
Ry: 0.320
Wx: 0.3127
Wy: 0.3290
Max: 4000
Min: 0.05

Remark :
15635 16450 are the standard D65 white point value, no need in these case to put them.


*************************************************************


Some example use
================

BT.2020 to BT.709 convertion, do the following:
ConvertYUVtoXYZ(Color=1)
ConvertXYZtoYUV(pColor=1)

----------------------------------

BT.709 to BT.2020 convertion, do the following:
ConvertYUVtoXYZ()
ConvertXYZtoYUV(Color=1,pColor=2)

----------------------------------

HDR HLG (with mastering Lw at 1500 and HLG mastering display colorspace BT.2020) to HDR PQ convertion:
ConvertYUVtoLinearRGB(Color=0,HDRMode=1,HLGLw=1500,OOTF=false)
ConvertLinearRGBtoYUV(Color=0,OOTF=false)

----------------------------------

HDR PQ to HDR HLG (with mastering Lw at 1200 and HLG mastering display colorspace BT.709) convertion:
ConvertYUVtoLinearRGB(Color=0,OOTF=false)
ConvertLinearRGBtoYUV(Color=0,HDRMode=1,HLGLw=1200,HLGColor=2,OOTF=false)

Note: In this case, there is no speed-up for lowering input from 16 to 10 or 12 bits.

----------------------------------

BT2446 methods exemples.
Supposed to work with linear display, not linear sensor, so, OOTF=false.

Method A

ConvertYUVtoLinearRGB(Color=0,HDRMode=2,OOTF=false)
ConvertLinearRGBtoYUV_BT2446_A_HDRtoSDR(Lhdr=1000.0,CoeffAdj=1.0)

Method C

#For PQ at 4000 for exemple :

ConvertYUVtoXYZ(Color=0,HDRMode=0,OOTF=false,Crosstalk=0.0)
ConverXYZ_BT2446_C_HDRtoSDR(PQMode=true,Lhdr=4000.0,Lsdr=100.0,pColor=0)
ConvertXYZtoYUV(Color=2,pColor=0,OOTF=false,Crosstalk=0.0)

#For HLG at 1000 for exemple (HLG must not be normalized to 10000.0) :

ConvertYUVtoXYZ(Color=0,HDRMode=2,OOTF=false,Crosstalk=0.0)
ConverXYZ_BT2446_C_HDRtoSDR(PQMode=false,Lhdr=1000.0,Lsdr=100.0,pColor=0)
ConvertXYZtoYUV(Color=2,pColor=0,OOTF=false,Crosstalk=0.0)

#If you play with Crosstalk, put the same value on both sides.

ConvertYUVtoXYZ(Color=0,HDRMode=2,OOTF=false,Crosstalk=0.1)
ConverXYZ_BT2446_C_HDRtoSDR(PQMode=false,Lhdr=1000.0,Lsdr=100.0,pColor=0)
ConvertXYZtoYUV(Color=2,pColor=0,OOTF=false,Crosstalk=0.1)
