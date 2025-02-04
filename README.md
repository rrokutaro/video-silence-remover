### Silence Detection (Cutter\.py)
This script can be used to remove silent parts from a video, keeping audible parts above a certain decibel (db) threshold. It can be used for removing silent parts from an interview, podcast, movie etc. It returns output findings to a `JSON` file containg necessary data that can be used to trim out audible parts. Python `3.10.6` was used when creating this script.
<br>

### Installation
**Create & Activate Virtual Environment**
```bash
python -m venv silence-removal
.\silence-removal\Scripts\activate
```
<br>

**Clone the repository**
```bash
git clone https://github.com/rrokutaro/video-silence-remover.git
cd silence-removal
```
<br>

**Install requirements**
```bash
pip install -r requirements
```
<br>

### Usage
```bash
python cutter.py --input "video.mp4" --output "output.json" --threshold -10 --min_silence 1 --buffer 0.5
```
<br>

- `--input | -i` : The input video video path
- `--output | -o` : The output json file path containing timestamps of audible parts
- `--threshold | -t` : Decibel threshold considered to be too silent. The number has to be preceded by a `-`. For example, remove silent parts below 10db -> `-10`. Raising this value means there will be less cuts, reducing it, means there will be more cuts
- `--min_silence | -m` : The minimum required silence duration required for removal
- `--buffer | -b` : Padding duration to prevent abrupt cuts while speakers are talking
<br>

### Notes
MoviePy could have been used here for returning the final video with the silence removed. But, for some reason even though GPU acceleration was used during testing, it was painfully slow. So, from here it would just be easier to use a tool like `Ffmpeg` to trim / keep audible parts without any issues of speed etc.
<br>

### PC Specs Used
- `GPU: MSI RTX 3060 VENTUS 2X 12GB GDDR6 VRAM`
- `CPU: Ryzen 5 5500 12 Logical Processors, 4.25Ghz Max Clock`
- `MotherBoard: MSI B450 A PRO MAX`
- `16GB 3200mhz DDR4 RAM`
