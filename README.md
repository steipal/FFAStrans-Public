# FFAStrans

Free Workflow and transcoding system
FFAStrans is workflow and transcoding system based on the principles of connecting nodes to create dynamic workflows. It's aimed at broadcasters and video professionals for automatic transcoding of media files through drop folders or API. FFAStrans is free to use for anyone but competes in the same market as highly expensive enterprise media solutions. Decoding and encoding relies on FFMpeg and AviSynth is used for extra filters.



User Interface
	-Intuitive graphical interface for creating complex workflows
	-Easily set up host farms for distributed node processing
	-Run as service in complex farms or as a single standalone application
	-Monitor jobs using inbuilt application or through http
	-Restart finished or failed jobs from start or from node of failure
Workflow
  Use as a generic file flow system
  Advanced decision making and variables nodes to dynamically adapt your file flow
  Multiple simultaneous workflows with different configurations, each run in separate processes
  Use functions to manipulate and extract data from strings, numbers and arrays
  Use functions to extract JSON data from JSON strings
  Extensive set of file, media and system variables
  Send e-mail notification with dynamic job data using variables
  Create custom presets for all nodes
  Read text or binary files into user variables
  Generate any kind of text file populated and altered with variables
  Execute any DOS command from within workflow
File Monitors
  Smart monitoring of image sequences
  Create custom user variables and statics
  Automatically fetch web videos like YouTube, Vimeo etc. by dropping URL-shorcuts in dropfolder
  Continuously process files as new when modified
  Configure FFAStrans to read and QuickTime reference files
  Monitor local or UNC paths and FTP
  Monitor camera file structures from Panasonic P2, Canon-XF and GoPro
Encoding
  Create high quality HEVC content with HDR support
  Encode broadcast formats like XDCAM-HD, AVC-Intra, DNxHD/HR and ProRes
  Process and conform audio without touching the video (transwrap)
  Convert images into video
  Create custom FFMpeg based encoder profile
  Preserve timecode throughout transcoding
Filtering
  Apply loudness control according to EBU-R128
  Broadcast quality PAL <> NTSC conversions
  Insert video or stills images
  Overlay watermark and transparent video
  Add superimposed timecode just like real broadcast VTR's
  Insert custom AviSynth script
API
  Easy third party integration with JSON based API
  Create, start, stop and pause jobs and populate variables through API
  Monitor, pause/resume and abort jobs through REST API using JSON
