import os
import cv2
from light_progress import ProgressBar


def color_print(text, color_name):
    color = {"red": 31, "green": 32}.get(color_name, 37)
    print("\033[{}m{}\033[0m".format(color, text))


def reduction_image(img, width=640, height=480):
    img = cv2.resize(img, (width, height))
    # ビットレートを下げる
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
    _, img = cv2.imencode(".jpg", img, encode_param)
    img = cv2.imdecode(img, 1)
    # return img

    # h, w = img.shape[:2]
    # if w > h:
    #     img = cv2.resize(img, (width, int(h * width / w)))
    # else:
    #     img = cv2.resize(img, (int(w * height / h), height))
    return img


def make_preview_movie(movie_path, output_dir="preview"):
    # make output dir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # make output path
    file_name = os.path.basename(movie_path)
    output_path = os.path.join(output_dir, file_name)

    # check output path
    if os.path.exists(output_path):
        color_print(f"{output_path} is already exists.", "red")
        return

    # open movie
    capture = cv2.VideoCapture(movie_path)
    if not capture.isOpened():
        color_print(f"Failed to open {movie_path}.", "red")
        return

    # get movie info
    fps = capture.get(cv2.CAP_PROP_FPS)
    width = capture.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
    size = (640, 480)

    # make writer
    writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, size)

    # make preview movie
    with ProgressBar(int(capture.get(cv2.CAP_PROP_FRAME_COUNT))) as pbar:
        while capture.isOpened():
            ret, frame = capture.read()
            if not ret:
                color_print("Movie is finished.", "green")
                break

            if cv2.waitKey(10) == 27:  # ESC key
                color_print("ESC key is pressed.", "red")
                break

            frame = reduction_image(frame, 640, 480)
            writer.write(frame)
            pbar.update(int(capture.get(cv2.CAP_PROP_POS_FRAMES)))

    # release
    capture.release()
    writer.release()


def main():
    make_preview_movie("movie.mp4", "preview")


if __name__ == "__main__":
    main()
