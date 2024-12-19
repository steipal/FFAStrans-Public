function Dmix3Stereo(clip a)
{
flr = GetChannel(a, 1, 2)
fcc = GetChannel(a, 3, 3)
return MixAudio(flr, fcc, 0.5858, 0.4142)
}# 3 Channels L,R,C or L,R,S


function Dmix3Dpl(clip a)
{
flr = GetChannel(a, 1, 2)
sl = GetChannel(a, 3)
sr = Amplify(sl, -1.0)
blr = MergeChannels(sl, sr)
return MixAudio(flr, blr, 0.5858, 0.4142)
}# 3 Channels only L,R,S


function Dmix4qStereo(clip a)
{
flr = GetChannel(a, 1, 2)
blr = GetChannel(a, 3, 4)
return MixAudio(flr, blr, 0.5, 0.5)
}# 4 Channels Quadro L,R,SL,SR


function Dmix4qDpl(clip a)
{
flr = GetChannel(a, 1, 2)
bl = GetChannel(a, 3)
br = GetChannel(a, 4)
sl = MixAudio(bl, br, 0.2929, 0.2929)
sr = MixAudio(bl, br, -0.2929, -0.2929)
blr = MergeChannels(sl, sr)
return MixAudio(flr, blr, 0.4142, 1.0)
}# 4 Channels Quadro L,R,SL,SR


function Dmix4qDpl2(clip a)
{
flr = GetChannel(a, 1, 2)
bl = GetChannel(a, 3)
br = GetChannel(a, 4)
sl = MixAudio(bl, br, 0.3714, 0.2144)
sr = MixAudio(bl, br, -0.2144, -0.3714)
blr = MergeChannels(sl, sr)
return MixAudio(flr, blr, 0.4142, 1.0)
}# 4 Channels Quadro L,R,SL,SR


function Dmix4sStereo(clip a)
{
flr = GetChannel(a, 1, 2)
fcc = GetChannel(a, 3, 3)
lrc = MixAudio(flr, fcc, 0.4142, 0.2929)
blr = GetChannel(a, 4, 4)
return MixAudio(lrc, blr, 1.0, 0.2929)
}# 4 Channels L,R,C,S


function Dmix4sDpl(clip a)
{
flr = GetChannel(a, 1, 2)
fcc = GetChannel(a, 3, 3)
lrc = MixAudio(flr, fcc, 0.4142, 0.2929)
sl = GetChannel(a, 4)
sr = Amplify(sl, -1.0)
blr = MergeChannels(sl, sr)
return MixAudio(flr, blr, 1.0, 0.2929)
}# 4 Channels L,R,C,S


function Dmix5Stereo(clip a)
{
flr = GetChannel(a, 1, 2)
fcc = GetChannel(a, 3, 3)
lrc = MixAudio(flr, fcc, 0.3694, 0.2612)
blr = GetChannel(a, 4, 5)
return MixAudio(lrc, blr, 1.0, 0.3694)
}# 5 Channels L,R,C,SL,SR


function Dmix5Dpl(clip a)
{
flr = GetChannel(a, 1, 2)
fcc = GetChannel(a, 3, 3)
lrc = MixAudio(flr, fcc, 0.3205, 0.2265)
bl = GetChannel(a, 4)
br = GetChannel(a, 5)
sl = MixAudio(bl, br, 0.2265, 0.2265)
sr = MixAudio(bl, br, -0.2265, -0.2265)
blr = MergeChannels(sl, sr)
return MixAudio(lrc, blr, 1.0, 1.0)
}# 5 Channels L,R,C,SL,SR


function Dmix5Dpl2(clip a)
{
flr = GetChannel(a, 1, 2)
fcc = GetChannel(a, 3, 3)
lrc = MixAudio(flr, fcc, 0.3254, 0.2301)
bl = GetChannel(a, 4)
br = GetChannel(a, 5)
sl = MixAudio(bl, br, 0.2818, 0.1627)
sr = MixAudio(bl, br, -0.1627, -0.2818)
blr = MergeChannels(sl, sr)
return MixAudio(lrc, blr, 1.0, 1.0)
}# 5 Channels FL,LR,C,SL,SR


function Dmix6Stereo(clip a)
{
flr = GetChannel(a, 1, 2)
fcc = GetChannel(a, 3, 3)
lrc = MixAudio(flr, fcc, 0.3694, 0.2612)
blr = GetChannel(a, 5, 6)
return MixAudio(lrc, blr, 1.0, 0.3694)
}# 6 Channels FL, FR, C, LFE, SL, SR


function Dmix6Dpl(clip a)
{
flr = GetChannel(a, 1, 2)
fcc = GetChannel(a, 3, 3)
lrc = MixAudio(flr, fcc, 0.3205, 0.2265)
bl = GetChannel(a, 5)
br = GetChannel(a, 6)
sl = MixAudio(bl, br, 0.2265, 0.2265)
sr = MixAudio(bl, br, -0.2265, -0.2265)
blr = MergeChannels(sl, sr)
return MixAudio(lrc, blr, 1.0, 1.0)
}# 6 Channels FL, FR, C, LFE, SL, SR


function Dmix6Dpl2(clip a)
{
flr = GetChannel(a, 1, 2)
fcc = GetChannel(a, 3, 3)
lrc = MixAudio(flr, fcc, 0.3254, 0.2301)
bl = GetChannel(a, 5)
br = GetChannel(a, 6)
sl = MixAudio(bl, br, 0.2818, 0.1627)
sr = MixAudio(bl, br, -0.1627, -0.2818)
blr = MergeChannels(sl, sr)
return MixAudio(lrc, blr, 1.0, 1.0)
}# 6 Channels FL, FR, C, LFE, SL, SR


function Dmix6StereoLfe(clip a)
{
flr = GetChannel(a, 1, 2)
fcc = GetChannel(a, 3, 3)
lrc = MixAudio(flr, fcc, 0.2929, 0.2071)
lfe = GetChannel(a, 4, 4)
lrc = MixAudio(lrc, lfe, 1.0, 0.2071)
blr = GetChannel(a, 5, 6)
return MixAudio(lrc, blr, 1.0, 0.2929)
}# 6 Channels FL, FR, C, LFE, SL, SR


function Dmix6DplLfe(clip a)
{
flr = GetChannel(a, 1, 2)
fcc = GetChannel(a, 3, 3)
lrc = MixAudio(flr, fcc, 0.2613, 0.1847)
lfe = GetChannel(a, 4, 4)
lrc = MixAudio(lrc, lfe, 1.0, 0.1847)
bl = GetChannel(a, 5)
br = GetChannel(a, 6)
sl = MixAudio(bl, br, 0.1847, 0.1847)
sr = MixAudio(bl, br, -0.1847, -0.1847)
blr = MergeChannels(sl, sr)
return MixAudio(lrc, blr, 1.0, 1.0)
}# 6 Channels FL, FR, C, LFE, SL, SR


function Dmix6Dpl2Lfe(clip a)
{
flr = GetChannel(a, 1, 2)
fcc = GetChannel(a, 3, 3)
lrc = MixAudio(flr, fcc, 0.2646, 0.1870)
lfe = GetChannel(a, 4, 4)
lrc = MixAudio(lrc, lfe, 1.0, 0.1870)
bl = GetChannel(a, 5)
br = GetChannel(a, 6)
sl = MixAudio(bl, br, 0.2291, 0.1323)
sr = MixAudio(bl, br, -0.1323, -0.2291)
blr = MergeChannels(sl, sr)
return MixAudio(lrc, blr, 1.0, 1.0)
}# 6 Channels FL, FR, C, LFE, SL, SR
