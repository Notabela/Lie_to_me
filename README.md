# Lie To Me

Lie detection using facial and voice recognition

## Requirements & Dependencies
#### Hardware requirements (recommended)
- Processor, 2 GHz
- RAM, 1 GB

### Required Modules
The Backend requires the following modules:
- [FFMPEG](http://ffmpeg.org/)

#### Supported browsers
The following browsers are supported on desktop platforms:

- Chrome 51 or higher
- Firefox 47 or higher
- Opera 37
- Edge 10586




## Installation
change FFMPEG_PATH and FFPROBE_PATH in file `__init__.py` to your FFMPEG install location
```python
10. FFMPEG_PATH  = '/usr/local/bin/ffmpeg' 
11. FFPROBE_PATH = '/usr/local/bin/ffprobe
```
 

`ON COMMAND LINE`
```bash
pip install -r requirements.txt
python application.py
```


`Web Application is available at http://127.0.0.1/5000`

#### Sample Video for Testing

[![75 Expressions in a minute](https://img.youtube.com/vi/ypqQ_mJIU3M/0.jpg)](https://www.youtube.com/watch?v=ypqQ_mJIU3M "75 Facial Expressions in a minute")
