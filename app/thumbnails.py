from . import DATA_DIR, MEDIA_DIR
import os
import mimetypes
import cv2
from PIL import Image
from werkzeug.security import safe_join
from pillow_heif import register_heif_opener

register_heif_opener()

THUMBNAIL_DIR = os.path.join(DATA_DIR, "thumbnails")
os.makedirs(THUMBNAIL_DIR, exist_ok=True)

WIDTH = 1440
HEIGHT = 810
HWIDTH = WIDTH//2
HHEIGHT = HEIGHT//2

def crop(image: Image.Image, des_width, des_height):
    width = image.width
    height = image.height
    if width/height <= des_width/des_height:
        # height higher than needed
        new_height = round(width/des_width*des_height)

        crop_x1 = 0
        crop_x2 = width
        crop_y1 = height//2 - new_height//2
        crop_y2 = height//2 + new_height//2
    else:
        # width higher than needed
        new_width = round(height/des_height*des_width)

        crop_x1 = width//2 - new_width//2 - 1
        crop_x2 = width//2 + new_width//2
        crop_y1 = 0
        crop_y2 = height
    crop = (crop_x1, crop_y1, crop_x2, crop_y2)
    return image.crop(crop)

def get_fail():
    fail_file = os.path.join(THUMBNAIL_DIR, "fail.webp")
    if os.path.exists(fail_file):
        return "/thumb/fail.webp"

    width_3 = round(WIDTH/3)
    # original (163, 178, 201)
    img = Image.new("RGBA", (WIDTH, HEIGHT))
    red = Image.new("RGBA", (width_3 + 1, HEIGHT), (255, 0, 0))
    green = Image.new("RGBA", (width_3 + 1, HEIGHT), (0, 255, 0))
    blue = Image.new("RGBA", (width_3 + 1, HEIGHT), (0, 0, 255))
    img.paste(red, (0, 0))
    img.paste(green, (width_3, 0))
    img.paste(blue, (width_3*2, 0))
    img.save(fail_file)
    return "/thumb/fail.webp"

#16776WIDTH58
def gen_thumbnail(timestamp):
    thumbnail_file = safe_join(THUMBNAIL_DIR, f"{timestamp}.webp")
    post_media_dir = safe_join(MEDIA_DIR, timestamp)
    if not os.path.exists(post_media_dir):
        return get_fail()
    media_files = os.listdir(post_media_dir)
    if not media_files:
        return get_fail()

    media_files.sort(key=lambda x: int(x.split(".")[0]))

    if len(media_files) > 4:
        media_files = media_files[:4]

    images = []
    for media_file in media_files:
        mimetype = mimetypes.guess_type(media_file)[0].split("/")[0]
        if mimetype == "video":
            video = cv2.VideoCapture(os.path.join(post_media_dir, media_file))
            frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
            middle = round(frames/2) - 1
            video.set(cv2.CAP_PROP_POS_FRAMES, middle)
            _, image = video.read()
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)
            images.append(image)
            video.release()
        if mimetype == "image":
            image = Image.open(os.path.join(post_media_dir, media_file))
            images.append(image)

    thumbnail = Image.new("RGBA", (WIDTH, HEIGHT))
    
    if len(images) == 1:
        img = images[0]
        img = crop(img, WIDTH, HEIGHT)
        img = img.resize((WIDTH, HEIGHT))

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
        img1 = crop(img1, HWIDTH, HEIGHT)
        img1 = img1.resize((HWIDTH, HEIGHT))

        img2 = images[1]
        img2 = crop(img2, HWIDTH, HHEIGHT)
        img2 = img2.resize((HWIDTH, HHEIGHT))

        img3 = images[2]
        img3 = crop(img3, HWIDTH, HHEIGHT)
        img3 = img3.resize((HWIDTH, HHEIGHT))

        thumbnail.paste(img1, (0, 0))
        thumbnail.paste(img2, (HWIDTH, 0))
        thumbnail.paste(img3, (HWIDTH, HHEIGHT))
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
    return f"/thumb/{timestamp}.webp"

def get_thumbnail(timestamp):
    thumbnail_file = safe_join(THUMBNAIL_DIR, f"{timestamp}.webp")
    if os.path.exists(thumbnail_file):
        return f"/thumb/{timestamp}.webp"

    return gen_thumbnail(timestamp)
