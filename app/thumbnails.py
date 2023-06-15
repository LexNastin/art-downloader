# from . import DATA_DIR, MEDIA_DIR
import os
import mimetypes
import cv2
from PIL import Image

# remove first 2
DATA_DIR = "/home/lex/tohart-viewer/data"
MEDIA_DIR = os.path.join(DATA_DIR, "media")
THUMBNAIL_DIR = os.path.join(DATA_DIR, "thumbnails")
os.makedirs(THUMBNAIL_DIR, exist_ok=True)

WIDTH = 960
HEIGHT = 540
HWIDTH = 480
HHEIGHT = 270

def crop(image: Image.Image, des_width, des_height):
    width = image.width
    height = image.height
    if width/height <= des_width/des_height:
        # height higher than needed
        new_height = round(width/des_width*des_height)

        crop_x1 = 0
        crop_x2 = width - 1
        crop_y1 = height//2 - new_height//2
        crop_y2 = height//2 + new_height//2 - 1
    else:
        # width higher than needed
        new_width = round(height/des_height*des_width)

        crop_x1 = width//2 - new_width//2 - 1
        crop_x2 = width//2 + new_width//2
        crop_y1 = 0
        crop_y2 = height - 1
    crop = (crop_x1, crop_y1, crop_x2, crop_y2)
    return image.crop(crop)

#16776WIDTH58
def get_thumbnail(timestamp):
    thumbnail_file = os.path.join(THUMBNAIL_DIR, f"{timestamp}.webp")
    if os.path.exists(thumbnail_file):
        return f"/thumb/{timestamp}.webp"

    post_media_dir = os.path.join(MEDIA_DIR, timestamp)
    media_files = os.listdir(post_media_dir)
    if not media_files:
        return "todo: fix thumbnails empty media"

    if len(media_files) > 4:
        media_files = media_files[:4]

    mimetype = mimetypes.guess_type(media_files[0])[0].split("/")[0]

    images = []
    for media_file in media_files:
        if mimetype == "video":
            video = cv2.VideoCapture(os.path.join(post_media_dir, media_file))
            frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
            middle = round(frames/2)
            video.set(cv2.CAP_PROP_POS_FRAMES, middle)
            _, image = video.read()
            image = Image.fromarray(image)
            images.append(image)
            video.release()
        if mimetype == "image":
            image = Image.open(media_file)
            images.append(image)

    thumbnail = Image.new("RGBA", (WIDTH, HEIGHT))
    
    if len(images) == 1:
        img = images[0]
        img = crop(img, WIDTH, HEIGHT)

        img.thumbnail((WIDTH, HEIGHT))
        thumbnail.paste(img, (0, 0))
    if len(images) == 2:
        img1 = images[0]
        img1 = crop(img1, HWIDTH, HEIGHT)
        img1 = img1.resize((HWIDTH, HEIGHT))

        img2 = images[1]
        img2 = crop(img2, HWIDTH, HEIGHT)
        img2 = img2.resize((HWIDTH, HEIGHT))

        thumbnail.paste(img1, (0, 0))
        thumbnail.paste(img2, (HWIDTH, 0))
    if len(images) == 3:
        img1 = images[0]
        img1 = crop(img1, HWIDTH, HHEIGHT)
        img1 = img1.resize((HWIDTH, HHEIGHT))

        img2 = images[1]
        img2 = crop(img2, HWIDTH, HHEIGHT)
        img2 = img2.resize((HWIDTH, HHEIGHT))

        img3 = images[2]
        img3 = crop(img3, WIDTH, HHEIGHT)
        img3 = img3.resize((WIDTH, HHEIGHT))

        thumbnail.paste(img1, (0, 0))
        thumbnail.paste(img2, (HWIDTH, 0))
        thumbnail.paste(img3, (0, HHEIGHT))
    if len(images) == 4:
        img1 = images[0]
        img1 = crop(img1, HWIDTH, HHEIGHT)
        img1 = img1.resize((HWIDTH, HHEIGHT))

        img2 = images[1]
        img2 = crop(img2, HWIDTH, HHEIGHT)
        img2 = img2.resize((HWIDTH, HHEIGHT))

        img3 = images[2]
        img3 = crop(img3, HWIDTH, HHEIGHT)
        img3 = img3.resize((HWIDTH, HHEIGHT))

        img4 = images[3]
        img4 = crop(img4, HWIDTH, HHEIGHT)
        img4 = img4.resize((HWIDTH, HHEIGHT))

        thumbnail.paste(img1, (0, 0))
        thumbnail.paste(img2, (HWIDTH, 0))
        thumbnail.paste(img3, (0, HHEIGHT))
        thumbnail.paste(img4, (HWIDTH, HHEIGHT))

    thumbnail.save(thumbnail_file)
    image.close()
