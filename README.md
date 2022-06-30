# Danbooru Autotagger

A tag prediction system for anime-style images.

![image](https://user-images.githubusercontent.com/8430473/176574544-d8ebe9e0-fdf2-4090-8864-b856ce5e3ff9.png)

# Demo

Try it at https://autotagger.donmai.us.

Or go to https://danbooru.donmai.us/ai_tags to browse predicted tags on all posts on
Danbooru. Here are some examples of different tags:

* https://danbooru.donmai.us/ai_tags?search[tag_name]=comic&search[order]=score_desc
* https://danbooru.donmai.us/ai_tags?search[tag_name]=hatsune_miku&search[order]=score_desc
* https://danbooru.donmai.us/ai_tags?search[tag_name]=cat&search[order]=score_desc

# Quickstart

```
# Get tags for a single image
cat image.jpg | docker run --rm -i ghcr.io/danbooru/autotagger autotag -

# Run the web server. Open http://localhost:5000.
docker run --rm -p 5000:5000 ghcr.io/danbooru/autotagger

# Get tags from the web server.
curl http://localhost:5000/evaluate -X POST -F file=@hatsune_miku.jpg -F format=json
```

# Web

Start the app server:

```bash
# With Docker
docker run --rm -p 5000:5000 ghcr.io/danbooru/autotagger

# Without Docker
python -m poetry run gunicorn
```

Then open http://localhost:5000 to use the webapp. Here you can upload images and
view the list of predicted tags.

# API

Start the app server as above, then do:

```bash
curl http://localhost:5000/evaluate -X POST -F file=@hatsune_miku.jpg -F format=json
```

The output will look like this:

```json
[
  {
    "filename": "hatsune_miku.jpg",
    "tags": {
      "1girl": 0.9995526671409607,
      "hatsune_miku": 0.9995216131210327,
      "vocaloid": 0.9981155395507812,
      "solo": 0.9938727617263794,
      "thighhighs": 0.970325767993927,
      "long_hair": 0.9630335569381714,
      "twintails": 0.9352861046791077,
      "very_long_hair": 0.8532902002334595,
      "necktie": 0.8532789945602417,
      "aqua_hair": 0.8266996145248413,
      "detached_sleeves": 0.796751081943512,
      "skirt": 0.7879447340965271,
      "rating:s": 0.7843148112297058,
      "aqua_eyes": 0.6136178374290466,
      "zettai_ryouiki": 0.5611224174499512,
      "thigh_boots": 0.37453025579452515,
      "black_legwear": 0.37255123257637024,
      "full_body": 0.3261113464832306,
      "simple_background": 0.28789788484573364,
      "boots": 0.286143958568573,
      "headset": 0.27902844548225403,
      "white_background": 0.23441512882709503,
      "shirt": 0.21720334887504578,
      "looking_at_viewer": 0.2044636756181717,
      "pleated_skirt": 0.17705336213111877,
      "smile": 0.17575393617153168,
      "bare_shoulders": 0.17370294034481049,
      "headphones": 0.16347116231918335,
      "standing": 0.15511766076087952,
      "rating:g": 0.13711321353912354,
      "aqua_necktie": 0.11798079311847687,
      "black_skirt": 0.11197035759687424,
      "blush": 0.10813453793525696
    }
  }
]
```

# CLI

Generate tags for a single image:

```bash
# With Docker:
cat image.jpg | docker run --rm ghcr.io/danbooru/autotagger autotag -

# Without Docker:
./autotag image.jpg
```

Generate tags for multiple images:

```bash
# With Docker:
# `-v $PWD:/host` means mount the current directory as /host inside the Docker container.
docker run --rm -v $PWD:/host ghcr.io/danbooru/autotagger autotag /host/image1.jpg /host/image2.jpg

# Without Docker:
./autotag image1.jpg image2.jpg
```

Generate tags for all images inside the `images/` directory:

```bash
# With Docker:
# Change `images` to whatever your image directory is called.
docker run --rm -v $PWD/images:/images ghcr.io/danbooru/autotagger autotag /images

# Without Docker:
./autotag images/
```

Generate tags for all files inside a directory matching a pattern:

```bash
find images/ -name '*.jpg' | ./autotag -i -
```

Generate a list of tags in CSV format, suitable for importing into your own Danbooru instance:

```bash
./autotag -c -f -N images/ | gzip > tags.csv.gz
```

# Manual Installation

```
# Install system dependencies
apt-get update
apt-get install git build-essential gfortran libatlas-base-dev libffi-dev libssl-dev libbz2-dev liblzma-dev

# Get code
git clone https://github.com/danbooru/autotagger.git
cd autotagger

# Install Python (skip this if Python 3.9.13 is already installed)
git clone https://github.com/asdf-vm/asdf.git ~/.asdf --branch v0.10.0
echo ". $HOME/.asdf/asdf.sh" >> ~/.bashrc
exec bash
asdf plugin add python
asdf install python 3.9.13
asdf shell python 3.9.13

# Install Python dependencies
pip install poetry==1.1.13
python -m poetry env use 3.9
python -m poetry install --no-dev

# Download latest model
wget https://github.com/danbooru/autotagger/releases/download/2022.06.20-233624-utc/model.pth -O models/model.pth

# Test that it works
./autotag test/hatsune_miku.jpg
```

# Implementation

The current model is stock Resnet-152, pretrained on Imagenet then finetuned
on Danbooru for about 10 epochs.

The model is trained on about 5500 tags. This includes character tags with >750
posts, copyright tags with >2000 posts, and general tags with >2500 posts, but not artist
or meta tags. Ratings are also included.

The model is available at https://github.com/danbooru/autotagger/releases.

# See also

* https://github.com/KichangKim/DeepDanbooru
* https://github.com/SmilingWolf/SW-CV-ModelZoo
* https://github.com/zyddnys/RegDeepDanbooru
* https://github.com/rezoo/illustration2vec
* https://www.gwern.net/Danbooru2021
* https://console.cloud.google.com/storage/browser/danbooru_public/data?project=danbooru1 (Danbooru data dumps)
