# HOW TO BUILD

1. Checkout zimg into ..\$(SolutionDir).
2. Checkout the latest AviSynthPlus into ..\$(SolutionDir).
3. Use provided solution file.
4. ???
5. **Prophet**

# HOW TO USE

## AviSynth compatibility mode
- z_PointResize(clip, int target_width, int target_height, float "src_left", float "src_top", float "src_width", float "src_height", string "chromaloc_op", string "dither", bool "interlaced")
- z_BilinearResize(clip, int target_width, int target_height, float "src_left", float "src_top", float "src_width", float "src_height", string "chromaloc_op", string "dither", bool "interlaced")
- z_BicubicResize(clip, int target_width, int target_height, float "b", float "c", float "src_left", float "src_top", float "src_width", float "src_height", string "chromaloc_op", string "dither", bool "interlaced")
- z_LanczosResize(clip, int target_width, int target_height, float "src_left", float "src_top", float "src_width", float "src_height", int "taps", string "chromaloc_op", string "dither", bool "interlaced")
- z_Lanczos4Resize(clip, int target_width, int target_height, float "src_left", float "src_top", float "src_width", float "src_height", int "taps", string "chromaloc_op", string "dither", bool "interlaced")
- z_Spline16Resize(clip, int target_width, int target_height, float "src_left", float "src_top", float "src_width", float "src_height", string "chromaloc_op", string "dither", bool "interlaced")
- z_Spline36Resize(clip, int target_width, int target_height, float "src_left", float "src_top", float "src_width", float "src_height", string "chromaloc_op", string "dither", bool "interlaced")
- z_Spline64Resize(clip, int target_width, int target_height, float "src_left", float "src_top", float "src_width", float "src_height", string "chromaloc_op", string "dither", bool "interlaced")

chromaloc_op - see below for the valid values\
dither (same as dither_type) - see below for the valid values

## VapourSynth compatibility mode
```
z_ConvertFormat(
    clip clip,
    int "width",
    int "height",
    string "pixel_type",
    string "colorspace_op",
    string "chromaloc_op",
    bool "interlaced",
    float "src_left",
    float "src_top",
    float "src_width",
    float "src_height",
    string "resample_filter",
    float "filter_param_a",
    float "filter_param_b",
    string "resample_filter_uv",
    float "filter_param_a_uv",
    float "filter_param_b_uv",
    string "dither_type",
	string "cpu_type",
	float "nominal_luminance",
	bool "approximate_gamma",
    int "use_props"
    bool "scene_referred"
    int "bit_depth"
    string "chroma_subsampling")
```
- width: output width in pixels
- height: output height in pixels
- pixel_type:
    ```
    "YV24" ("YUV444", "YUV444P8"), "YV16" ("YUV422", "YUV422P8"), "YV12" ("YUV420", "YUV420P8"), "YV411" ("YUV411", "YUV411P8"), "Y8",
    "YUV444P10", "YUV422P10", "YUV420P10", "Y10",
    "YUV444P12", "YUV422P12", "YUV420P12", "Y12",
    "YUV444P14", "YUV422P14", "YUV420P14", "Y14",
    "YUV444P16", "YUV422P16", "YUV420P16", "Y16",
    "YUV444PS", "YUV422PS", "YUV420PS", "Y32",
    "RGBP" ("RGBP8"),
    "RGBP10",
    "RGBP12",
    "RGBP14",
    "RGBP16",
    "RGBPS",
    "RGBAP" ("RGBAP8"),
    "RGBAP10",
    "RGBAP12",
    "RGBAP14",
    "RGBAP16",
    "RGBAPS",
    "YUVA444" ("YUVA444P8"), "YUVA422" ("YUVA422P8"), "YUVA420" (YUVA420P8"),
    "YUVA444P10", "YUVA422P10", "YUVA420P10",
    "YUVA444P12", "YUVA422P12", "YUVA420P12",
    "YUVA444P14", "YUVA422P14", "YUVA420P14",
    "YUVA444P16", "YUVA422P16", "YUVA420P16",
    "YUVA444PS", "YUVA422PS", "YUVA420PS"
    ```
- colorspace_op:
	- matrix (default YUV: `"170m"`)
        ```
        "rgb" (0),
        "709" (1),
        "unspec" (2),
        "fcc" (4),
        "470bg" ("601") (5),
        "170m" (6), (Equivalent to 470bg)
        "240m" (7),
        "ycgco" (8),
        "2020ncl" ("2020") (9),
        "2020cl" (10),
        "chromancl" (12),
        "chromacl" (13),
        "ictcp" (14)
        ```
	- transfer
        ```
        "709" (1),
        "unspec" (2),
        "470m" (4),
        "470bg" (5),
        "601" (6), (Equivalent to 709)
        "240m" (7),
        "linear" (8),
        "log100" (9),
        "log316" (10),
        "xvycc" (11),
        "srgb" (13),
        "2020_10" ("2020") (14), (Equivalent to 709)
        "2020_12" (15), (Equivalent to 709)
        "st2084" (16),
        "std-b67" (18),
        "prophoto" (30)
        ```
	- primaries
        ```
        "709" (1),
        "unspec" (2),
        "470m" (4),
        "470bg" (5),
        "170m" (6),
        "240m" (7), (Equivalent to 170m)
        "film" (8),
        "2020" (9),
        "st428" ("xyz") (10),
        "st431-2" ("dci-p3") (11),
        "st432-1" ("display-p3") (12),
        "jedec-p22" (22),
        "prophoto" (30)
        ```
	- range (default RGB: `"full"`; YUV < 32-bit: `"limited"`)
        ```
        "limited" ("l") (1),
        "full" ("f") (0)
        ```
Format is: `"matS[:transS[:primS[:rangeS]]]=>matD[:transD[:primD[:rangeD]]]"`\
Example JPEG to MPEG: `"170m:709:709:f=>709:709:709:l"`\
There is keyword "auto" for source matrix, transfer, primaries, range. When it's used the corresponding input frame properties are used, if such frame properties don't exist either an error is arised or default matrix and color range are used.\
There is keyword "same" for destination matrix, transfer, primaries, range. When it's used the corresponding source value is applied for destination too so there is no conversion.
- chromaloc_op (default left):
    ```
    "left" ("mpeg2") (0),
    "center" ("jpeg", "mpeg1") (1),
    "top_left" (2),
    "top" (3),
    "bottom_left" (4),
    "bottom" (5)
    ```
Format is" `"[locS]=>[locD]"`\
Example JPEG to MPEG2: `"center=>left"`\
There is keyword "auto" for source chromaloc_op. When it's used the corresponding input frame property is used, if such frame property doesn't exist default chromaloc is used.\
There is keyword "same" for destination chromaloc_op. When it's used the corresponding source value is applied for destination too so there is no conversion.
- interlaced (default: false): whether to use interlaced mode.\
If `use_props=1` is used and `interlaced` is not specified, frame property `_FieldBased` is read to enable/disable the interlaced mode.
- resample_filter (default bicubic 0/0.5):
    ```
    "point",
    "bilinear",
    "bicubic",
    "spline16",
    "spline36",
    "spline64",
    "lanczos"
    ```
- filter_param_a: first parameter to resampler
- filter_param_b: second parameter to resampler\
Example Bicubic (Mitchell-Netravali): `resample_filter="bicubic", filter_param_a=0.333, filter_param_b=0.333`\
Example 4-tap Lanczos: `resample_filter="lanczos", filter_param_a=4`
- resample_filter_uv: resampling mode for chroma (same filters as "resample_filter")
- filter_param_a_uv: first parameter to chroma resampler
- filter_param_b_uv: second parameter to chroma resampler
- dither_type (default "none"):
    ```
    "none",
    "ordered",
    "random",
    "error_diffusion"
    ```
- cpu_type:
    ```
    "none",
    "avx",
    "avx_e" ("ivy"),
    "avx2",
    "avx512f,
    "avx512_skx" ("skx"),
    "avx512_clx",
    "avx512_pmc" ("cannon"),
    "avx512_snc" ("ice"))
    ```
- nominal_luminance (default 100.0): nominal peak luminance in cd/m^2 for standard-dynamic range (SDR) systems (more info [here](https://github.com/sekrit-twc/zimg/blob/93f8504a67373d428158219eb3aca0455e4c20ca/src/zimg/api/zimg.h#L595))
- approximate_gamma (default true): evaluating transfer functions at reduced precision
- use_props (default -1) - whether to read and set frame properties
    ```
    -1: If frame properties are supported - if every value of colorspace_op and every value of chromaloc_op is specified, and it's different than "auto", 0, otherwise 1.
        If frame properties are supported - if every value of colorspace_op is specified and different than "auto", src and dst colorspaces are with subsampling 0 (rgb, yuv444), this is 0, otherwise 1.
        If frame properties are not supported - 0.
        If interlaced=true - 0.
    0: If frame properties are supported - only set frame properties.
    1: Read and set frame properties.
    2: Save properties of the source clip as frame properties: z_ChromaLocation, z_ColorRange, z_Matrix, z_Transfer, z_Primaries.
    Every value of colorspace_op and chromaloc_op must be specified and different than "auto".
    3: Save properties of the source clip as frame properties: z_ChromaLocation, z_ColorRange, z_Matrix, z_Transfer, z_Primaries.
    Frame properties _ChromaLocation, _ColorRange, _Matrix, _Transfer, _Primaries must exist.
    Frame properties _Matrix, _Transfer, _Primaries must have values different than 2 (unspec).
    4: Use z_xxx frame properties as target values.
    z_xxx frame propeties are removed after the colorspace conversion.
    ```
use_props=0 is faster than use_props=1\
use_props=2 is faster than use_props=3\
Example use_props=2 and use_props=4
```
z_ConvertFormat(pixel_type="rgbp", colorspace_op="709:709:709:l=>rgb:linear:709:f", chromaloc_op="left=>left", use_props=2)
z_ConvertFormat(pixel_type="yv12", use_props=4) # convert rgb to yuv with the yuv initial properties
```
Example use_props=3 and use_props=4
```
z_ConvertFormat(pixel_type="rgbp", colorspace_op="709:709=>rgb:linear", use_props=3)
z_ConvertFormat(pixel_type="yv12", use_props=4) # convert rgb to yuv with the yuv initial properties
```

- scene_referred (default false) - whether to use scene-referred transfer function

- bit_depth: output bit depth (8, 10, 12, 14, 16, 32)\
It doesn't have effect if `pixel_type` is defined.

- chroma_subsampling: output chroma subsampling ("444", "422", "420")\
It doesn't have effect if `pixel_type` is defined.

The names of the frame properties that are read and set are: `_ChromaLocation, _ColorRange, _Matrix, _Transfer, _Primaries`, `_SARNum`, `_SARDen`.\
The frame properties read and set the corresponding numerical index of the parameters. For example: matrix `"709"` has numerical index `1` and the frame property have value of `1`.

See VapourSynth documentation for valid string constants.
