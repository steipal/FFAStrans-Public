Function SafeColorLimiter(clip clp) {      

    Original = clp.IsY ? "Y" : clp.IsY8 ? "Y8" : clp.IsYV12   ? "YV12"  : clp.IsYUY2  ? "YUY2"
        \ : clp.IsYV16      ? "YV16"  : clp.IsYV24  ? "YV24"
        \ : clp.Is420 ? "YUV420" : clp.IsYV411 ? "YUV411" : clp.Is422 ? "YUV422" : clp.Is444 ? "YUV444"
        \ : ""
        
    #Bit Depth   
    Bpc = clp.BitsPerComponent
        
    #Check bit depth    
    Assert(Bpc == 8 || Bpc == 10 || Bpc == 12 || Bpc == 14 || Bpc == 16 || Bpc == 32, "Safe Color Limiter: Bit Depth not supported," + Chr(10)+"8bit, 10bit, 12bit, 14bit, 16bit, 32bit planar are supported!")
    
    #Values for 32bit Float
    min_luma_float=16/255.0
    max_luma_float=235/255.0
    min_chroma_float=-112/255.0
    max_chroma_float=107/255.0
    
    #Apply the appropriate clipping according to the bit depth
     if (Original == "Y" && Bpc == 8) {
     
        #Luma only
        Limiter(clp, min_luma=16, max_luma=235) #8bit Y
        propSet("_ColorRange", 1) #Limited TV Range
        my_output=last
        
       }
    else if (Original == "YUV411" || Original == "YV12" || Original == "YUV420" && Bpc == 8 || Original == "YV16" || Original == "YUY2" || Original == "YUV422" && Bpc == 8 || Original == "YV24" || Original == "YUV444" && Bpc == 8) {
        
        #Luma & Chroma
        Limiter(clp, min_luma=16, max_luma=235, min_chroma=16, max_chroma=240) #8bit YUV
        propSet("_ColorRange", 1) #Limited TV Range
        my_output=last
        
     }
     else if (Original == "Y" && Bpc == 10) {
     
        #Luma only
        Limiter(clp, min_luma=64, max_luma=940) #10bit Y
        propSet("_ColorRange", 1) #Limited TV Range
        my_output=last
     }
     else if (Original == "YUV420" && Bpc == 10 || Original == "YUV411" && Bpc == 10 || Original == "YUV422" && Bpc == 10 || Original == "YUV444" && Bpc == 10) {
        
        #Luma & Chroma    
        Limiter(clp, min_luma=64, max_luma=940, min_chroma=64, max_chroma=940) #10bit YUV
        propSet("_ColorRange", 1) #Limited TV Range
        my_output=last
        
     }
     else if (Original == "Y" && Bpc == 12) {
        
        #Luma only
        Limiter(clp, min_luma=256, max_luma=3760) #12bit Y
        propSet("_ColorRange", 1) #Limited TV Range
        my_output=last
        
     }
     else if (Original == "YUV420" && Bpc == 12 || Original == "YUV411" && Bpc == 12 || Original == "YUV422" && Bpc == 12 || Original == "YUV444" && Bpc == 12) {
        
        #Luma & Chroma
        Limiter(clp, min_luma=256, max_luma=3760, min_chroma=256, max_chroma=3760) #12bit YUV
        propSet("_ColorRange", 1) #Limited TV Range
        my_output=last
        
     }
     else if (Original == "Y" && Bpc == 14) {
     
        #Luma only
        Limiter(clp, min_luma=1024, max_luma=15040) #14bit Y
        propSet("_ColorRange", 1) #Limited TV Range
        my_output=last
        
     }
     else if (Original == "YUV420" && Bpc == 14 || Original == "YUV411" && Bpc == 14 || Original == "YUV422" && Bpc == 14 || Original == "YUV444" && Bpc == 14) {
     
        #Luma & Chroma
        Limiter(clp, min_luma=1024, max_luma=15040, min_chroma=1024, max_chroma=15040) #14bit YUV
        propSet("_ColorRange", 1) #Limited TV Range
        my_output=last
        
     }
     else if (Original == "Y" && Bpc == 16) {
     
        #Luma only
        Limiter(clp, min_luma=4096, max_luma=60160) #16bit Y
        propSet("_ColorRange", 1) #Limited TV Range
        my_output=last
        
     }
     else if (Original == "YUV420" && Bpc == 16 || Original == "YUV411" && Bpc == 16 || Original == "YUV422" && Bpc == 16 || Original == "YUV444" && Bpc == 16) {
     
        #Luma & Chroma
        Limiter(clp, min_luma=4096, max_luma=60160, min_chroma=4096, max_chroma=60160) #16bit YUV
        propSet("_ColorRange", 1) #Limited TV Range
        my_output=last
        
     }
     else if (Original == "Y" && Bpc == 32) {
     
        #Luma only
        Limiter(clp, min_luma=min_luma_float, max_luma=max_luma_float, min_chroma=min_chroma_float, max_chroma=max_chroma_float) #32bit Y
        propSet("_ColorRange", 1) #Limited TV Range
        my_output=last
        
     }
     else if (Original == "YUV420" && Bpc == 32 || Original == "YUV411" && Bpc == 32 || Original == "YUV422" && Bpc == 32 || Original == "YUV444" && Bpc == 32) {
     
        #Luma & Chroma
        Limiter(clp, min_luma=min_luma_float, max_luma=max_luma_float, min_chroma=min_chroma_float, max_chroma=max_chroma_float) #32bit YUV
        propSet("_ColorRange", 1) #Limited TV Range
        my_output=last
        
     }
     else {
     
     #return RGB as-is
     my_output=clp
     
     }
     
     return my_output

}
