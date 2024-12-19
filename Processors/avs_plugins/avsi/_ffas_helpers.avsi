function _ffas_helpers(clip)
    {
        #Check if frame properties are there
        my_frame_properties = propGetAll(clip)
        
        #If there are no frame properties, let's do what we can
        if (Int(my_frame_properties.ArraySize()) == 0) {
        
             
             #Check interlacing per filter-builder workaround
             if (IsFrameBased(clip) == true && GetParity(clip) == true) {
                  clip = propSet(clip, "_FieldBased", 2) #TFF
             }
             else if (IsFrameBased(clip) == true && GetParity(clip) == false) {
                  clip = propSet(clip, "_FieldBased", 1) #BFF
             }
             else {
                  clip = propSet(clip, "_FieldBased", 0) #progressive
                   }
             
             #Check Frame Size to set matrix, transfer and primaries
             if (clip.Height() <= 480) {
                 clip = propSet(clip, "_Matrix", 6) #BT601 NTSC
                 clip = propSet(clip, "_Transfer", 6) #BT601 NTSC
                 clip = propSet(clip, "_Primaries", 6) #BT601 NTSC
                 }
                 
            else if (clip.Height() <= 576 && clip.Height() > 480) {
                 clip = propSet(clip, "_Matrix", 5) #BT601 PAL
                 clip = propSet(clip, "_Transfer", 6) #BT601 PAL
                 clip = propSet(clip, "_Primaries", 5) #BT601 PAL                
                }

             else if (clip.Height() > 576) {
                clip = propSet(clip, "_Matrix", 1) #BT709
                clip = propSet(clip, "_Transfer", 1) #BT709
                clip = propSet(clip, "_Primaries", 1) #BT709              
                }
                
                
              #Set Limited TV Range for YUV and Full PC Range for RGB
              if (clip.NumComponents() == 1 || clip.Is420() == true || clip.Is422() == true || clip.isYUY2() == true || clip.Is444() == true) {
                clip = propSet(clip, "_ColorRange", 1) #Limited TV Range
                }
             else {
                clip = propSet(clip, "_ColorRange", 0) #Full PC Range
                }
         return clip
        }
                
         #If there are SOME frame properties, let's try to preserve those and fill the gap
         else if (Int(my_frame_properties.ArraySize()) > 0) {
         
         
              #Check if we have the interlacing flag / field property
              try {
                      if (propGetInt(clip, "_FieldBased") >= 0 ) {
         
                      #We have the field property, so we pass it through
                      clip = clip
                    }
             }

              #We don't have the field property, so we assume
              catch (property) {

                     #Check interlacing per filter-builder workaround
                     if (IsFrameBased(clip) == true && GetParity(clip) == true) {
                       clip = propSet(clip, "_FieldBased", 2) #TFF
                     }
                     else if (IsFrameBased(clip) == true && GetParity(clip) == false) {
                       clip = propSet(clip, "_FieldBased", 1) #BFF
                     }
                     else {
                       clip = propSet(clip, "_FieldBased", 0) #progressive
                     }
              }
              
              #Check if we have Matrix
              try {
                      if (propGetInt(clip, "_Matrix") >= 0) {
        
                      my_matrix = propGetInt(clip, "_Matrix")
                      }
              }
        
              catch (property) {
                       my_matrix = Undefined()
                       }

              #Check if we have Transfer
              try {
                      if (propGetInt(clip, "_Transfer") >= 0) {
                      my_transfer = propGetInt(clip, "_Transfer")
                      }
              }        
 
              catch (property) {
                      my_transfer = Undefined()
                      }

              #Check if we have Primaries
              try {
                      if (propGetInt(clip, "_Primaries") >= 0) {
                      my_primaries =  propGetInt(clip, "_Primaries")
                      }
              }

              catch (property) {
                      my_primaries = Undefined()
                      }
        
              #If we have matrix, transfer, primaries, we pass them through        
              if (Defined(my_matrix) == true && Defined(my_transfer) == true && Defined(my_primaries) == true) {
                      clip = clip
                      }

              #We have only matrix
              else if (Defined(my_matrix) == true && Defined(my_transfer) == false && Defined(my_primaries) == false) {

                          #BT709
                          if (my_matrix == 1) {
                
                              clip = propSet(clip, "_Matrix", 1)
                              clip = propSet(clip, "_Transfer", 1)
                              clip = propSet(clip, "_Primaries", 1)
                              }
             
                          #BT601 PAL 
                          else if (my_matrix == 5) {
            
                              clip = propSet(clip, "_Matrix", 5)
                              clip = propSet(clip, "_Transfer", 6)
                              clip = propSet(clip, "_Primaries", 5)
                              }
                
                           #BT601 NTSC   
                           else if (my_matrix == 6) {
             
                              clip = propSet(clip, "_Matrix", 6)
                              clip = propSet(clip, "_Transfer", 6)
                              clip = propSet(clip, "_Primaries", 6)
                              }
                
                           #if none of the above, we pass everything through   
                           else {
                              clip = clip
                              }
              }                
                
              #We have only transfer
              else if (Defined(my_matrix) == false && Defined(my_transfer) == true && Defined(my_primaries) == false) {

                           #BT709
                           if (my_transfer == 1) {
             
                              clip = propSet(clip, "_Matrix", 1)
                              clip = propSet(clip, "_Transfer", 1)
                              clip = propSet(clip, "_Primaries", 1)
                              }
                
                           #BT601 NTSC   
                           else if (my_transfer == 6 && clip.Height() <= 480) {
             
                              clip = propSet(clip, "_Matrix", 6)
                              clip = propSet(clip, "_Transfer", 6)
                              clip = propSet(clip, "_Primaries", 6)
                              }
                
                           #BT601 PAL
                           else if (my_transfer == 6 && clip.Height() > 480) {
             
                              clip = propSet(clip, "_Matrix", 5)
                              clip = propSet(clip, "_Transfer", 6)
                              clip = propSet(clip, "_Primaries", 5)
                              }
                
                           #BT2020 SDR   
                           else if (my_transfer == 14) {
             
                              clip = propSet(clip, "_Matrix", 9)
                              clip = propSet(clip, "_Transfer", 14)
                              clip = propSet(clip, "_Primaries", 9)
                              }
                
                           #HLG
                           else if (my_transfer == 18) {
             
                              clip = propSet(clip, "_Matrix", 9)
                              clip = propSet(clip, "_Transfer", 18)
                              clip = propSet(clip, "_Primaries", 9)
                              }
                
                           #PQ
                           else if (my_transfer == 16) {
             
                              clip = propSet(clip, "_Matrix", 9)
                              clip = propSet(clip, "_Transfer", 16)
                              clip = propSet(clip, "_Primaries", 9)
                              }
                
                            #if none of the above, we pass everything through 
                            else {
                              clip = clip
                              }
              }                

              #We have only primaries
              else if (Defined(my_matrix) == false && Defined(my_transfer) == false && Defined(my_primaries) == true) {

                           #BT709
                           if (my_primaries == 1) {
             
                              clip = propSet(clip, "_Matrix", 1)
                              clip = propSet(clip, "_Transfer", 1)
                              clip = propSet(clip, "_Primaries", 1)
                              }
                
                           #BT601 NTSC   
                           else if (my_primaries == 6) {
             
                              clip = propSet(clip, "_Matrix", 6)
                              clip = propSet(clip, "_Transfer", 6)
                              clip = propSet(clip, "_Primaries", 6)
                              }
                
                           #BT601 PAL
                           else if (my_primaries == 5) {
             
                              clip = propSet(clip, "_Matrix", 5)
                              clip = propSet(clip, "_Transfer", 6)
                              clip = propSet(clip, "_Primaries", 5)
                              }
                
                            #if none of the above, we pass everything through 
                            else {
                              clip = clip
                              }
              }                

              #We have matrix and transfer
              else if (Defined(my_matrix) == true && Defined(my_transfer) == true && Defined(my_primaries) == false) {

                           #BT709
                           if (my_matrix == 1 || my_transfer == 1) {
             
                              clip = propSet(clip, "_Matrix", 1)
                              clip = propSet(clip, "_Transfer", 1)
                              clip = propSet(clip, "_Primaries", 1)
                              }
                
                           #BT601 NTSC   
                           else if (my_matrix == 6 && my_transfer == 6) {
             
                              clip = propSet(clip, "_Matrix", 6)
                              clip = propSet(clip, "_Transfer", 6)
                              clip = propSet(clip, "_Primaries", 6)
                              }
                
                           #BT601 PAL
                           else if (my_matrix == 5 && my_transfer == 6) {
             
                              clip = propSet(clip, "_Matrix", 5)
                              clip = propSet(clip, "_Transfer", 6)
                              clip = propSet(clip, "_Primaries", 5)
                              }
                
                           #BT2020 SDR   
                           else if (my_transfer == 14) {
             
                              clip = propSet(clip, "_Matrix", 9)
                              clip = propSet(clip, "_Transfer", 14)
                              clip = propSet(clip, "_Primaries", 9)
                              }
                
                           #HLG
                           else if (my_transfer == 18) {
             
                              clip = propSet(clip, "_Matrix", 9)
                              clip = propSet(clip, "_Transfer", 18)
                              clip = propSet(clip, "_Primaries", 9)
                              }
                
                           #PQ
                           else if (my_transfer == 16) {
             
                              clip = propSet(clip, "_Matrix", 9)
                              clip = propSet(clip, "_Transfer", 16)
                              clip = propSet(clip, "_Primaries", 9)
                              }
                
                            #if none of the above, we pass everything through 
                            else {
                              clip = clip
                              }
              }


              #We have matrix and primaries
              else if (Defined(my_matrix) == true && Defined(my_transfer) == false && Defined(my_primaries) == true) {

                           #BT709
                           if (my_matrix == 1 || my_primaries == 1) {
             
                              clip = propSet(clip, "_Matrix", 1)
                              clip = propSet(clip, "_Transfer", 1)
                              clip = propSet(clip, "_Primaries", 1)
                              }
                
                           #BT601 NTSC   
                           else if (my_matrix == 6 || my_primaries == 6) {
             
                              clip = propSet(clip, "_Matrix", 6)
                              clip = propSet(clip, "_Transfer", 6)
                              clip = propSet(clip, "_Primaries", 6)
                              }
                
                           #BT601 PAL
                           else if (my_matrix == 5 || my_primaries == 5) {
             
                              clip = propSet(clip, "_Matrix", 5)
                              clip = propSet(clip, "_Transfer", 6)
                              clip = propSet(clip, "_Primaries", 5)
                              }
                
                            #if none of the above, we pass everything through 
                            else {
                              clip = clip
                              }
              }



              #We have transfer and primaries
              else if (Defined(my_matrix) == true && Defined(my_transfer) == true && Defined(my_primaries) == false) {

                           #BT709
                           if (my_transfer == 1 || my_primaries == 1) {
             
                              clip = propSet(clip, "_Matrix", 1)
                              clip = propSet(clip, "_Transfer", 1)
                              clip = propSet(clip, "_Primaries", 1)
                              }
                
                           #BT601 NTSC   
                           else if (my_transfer == 6 && my_primaries == 6) {
             
                              clip = propSet(clip, "_Matrix", 6)
                              clip = propSet(clip, "_Transfer", 6)
                              clip = propSet(clip, "_Primaries", 6)
                              }
                
                           #BT601 PAL
                           else if (my_transfer == 6 && my_primaries == 5) {
             
                              clip = propSet(clip, "_Matrix", 5)
                              clip = propSet(clip, "_Transfer", 6)
                              clip = propSet(clip, "_Primaries", 5)
                              }
                
                           #BT2020 SDR   
                           else if (my_transfer == 14) {
             
                              clip = propSet(clip, "_Matrix", 9)
                              clip = propSet(clip, "_Transfer", 14)
                              clip = propSet(clip, "_Primaries", 9)
                              }
                
                           #HLG
                           else if (my_transfer == 18) {
             
                              clip = propSet(clip, "_Matrix", 9)
                              clip = propSet(clip, "_Transfer", 18)
                              clip = propSet(clip, "_Primaries", 9)
                              }
                
                           #PQ
                           else if (my_transfer == 16) {
             
                              clip = propSet(clip, "_Matrix", 9)
                              clip = propSet(clip, "_Transfer", 16)
                              clip = propSet(clip, "_Primaries", 9)
                              }
                
                            #if none of the above, we pass everything through 
                            else {
                              clip = clip
                              }
              }

              #We have no matrix, transfer or primaries
              else if (Defined(my_matrix) == false && Defined(my_transfer) == false && Defined(my_primaries) == false) {

                          #Check Frame Size to set matrix, transfer and primaries
                           if (clip.Height() <= 480) {
                               clip = propSet(clip, "_Matrix", 6) #BT601 NTSC
                               clip = propSet(clip, "_Transfer", 6) #BT601 NTSC
                               clip = propSet(clip, "_Primaries", 6) #BT601 NTSC
                               }
                 
                          else if (clip.Height() <= 576 && clip.Height() > 480) {
                               clip = propSet(clip, "_Matrix", 5) #BT601 PAL
                               clip = propSet(clip, "_Transfer", 6) #BT601 PAL
                               clip = propSet(clip, "_Primaries", 5) #BT601 PAL                
                              }

                           else if (clip.Height() > 576) {
                              clip = propSet(clip, "_Matrix", 1) #BT709
                              clip = propSet(clip, "_Transfer", 1) #BT709
                              clip = propSet(clip, "_Primaries", 1) #BT709              
                              }
              }
              
              
              
              #Check if we have the range information
              try {
                      if (propGetInt(clip, "_ColorRange") >= 0 ) {
         
                      #We have the range property, so we pass it through
                      clip = clip
                    }
             }

              #We don't have the range property, so we assume
              catch (property) {

                     #Set Limited TV Range for YUV and Full PC Range for RGB
                     if (clip.NumComponents() == 1 || clip.Is420() == true || clip.Is422() == true || clip.isYUY2() == true || clip.Is444() == true) {
                       clip = propSet(clip, "_ColorRange", 1) #Limited TV Range
                     }
                     else {
                       clip = propSet(clip, "_ColorRange", 0) #Full PC Range
                     }
              }
         return clip
         }
	}

function _MySwapFields(clip)
	{
		clip = SwapFields(clip)
		clip_interl = propGetAny(clip, "_FieldBased")
		if (clip_interl == 1) {
			clip_interl = 2
			clip = AssumeTFF(clip)
		} else if (clip_interl == 2) {
			clip_interl = 1
			clip = AssumeBFF(clip)
		}
		clip = propSet(clip, "_FieldBased", clip_interl)
		Return clip
	}

function __get_ff_fields(clip)
	{
		clip_interl = propGetAny(clip, "_FieldBased")
		if (clip_interl == 1) {
			Return 2
		} else if (clip_interl == 2) {
			Return 1
		}
		Return 0
	}

function _set_interl_props(clip)
    {
        #Check if frame properties are there
        my_frame_properties = propGetAll(clip)

        #If there are no frame properties, let's do what we can
        if (Int(my_frame_properties.ArraySize()) == 0) {
			#Check interlacing per filter-builder workaround
			if (IsFrameBased(clip) == true && GetParity(clip) == true) {
				clip = propSet(clip, "_FieldBased", 2) #TFF
			} else if (IsFrameBased(clip) == true && GetParity(clip) == false) {
				clip = propSet(clip, "_FieldBased", 1) #BFF
			} else {
				clip = propSet(clip, "_FieldBased", 0) #progressive
			}
        }
        return clip
    }