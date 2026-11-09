# AVSTP

AVSTP - Avisynth Thread Pool

AVSTP is a programming library for Avisynth plug-in developers.
It helps supporting native multi-threading in plug-ins.
It works by sharing a thread pool between multiple plug-ins, so the 
number of threads stays low whatever the number of instantiated 
plug-ins.

A single avstp.dll can serve multiple avstp-aware Avisynth plugin dlls
when is copied next to them.
Such plugins can use or not use the services of avstp.

## Versions

- v1.0.3 (20151230) by Firesledge
- v1.0.4 (20201017) by Firesledge
- v1.0.4.1 (20230123) by Ferenc Pintér
  - Fixes rare hangup caused by internal memory corruption.
    See: https://github.com/pinterf/AVSTP/issues/1
  - Move project to github

## Author

Firesledge (aka Cretindesalpes)

Additional Fix by Ferenc Pintér

## Links

https://github.com/pinterf/AVSTP
http://avisynth.nl/index.php/AVSTP
http://ldesoras.free.fr/prod.html#src_avstp

## License

http://www.wtfpl.net/txt/copying/

