import os
import cv2


def color_print(text, color_name):
    color = {"red": 31, "green": 32}.get(color_name, 37)
    print("\033[{}m{}\033[0m".format(color, text))


def reduction_image(img, width=640, height=480):
    return cv2.resize(img, (width, height))
    # h, w = img.shape[:2]
    # if w > h:
    #     img = cv2.resize(img, (width, int(h * width / w)))
    # else:
    #     img = cv2.resize(img, (int(w * height / h), height))
    # return img


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

    capture = cv2.VideoCapture(movie_path)
    if not capture.isOpened():
        color_print(f"Failed to open {movie_path}.", "red")
        return

    fps = capture.get(cv2.CAP_PROP_FPS)
    width = capture.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
    writer = cv2.VideoWriter(
        output_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (640, 480)
    )

    while capture.isOpened():
        ret, frame = capture.read()
        if not ret:
            color_print("Movie is finished.", "green")
            break

        if cv2.waitKey(10) == 27:  # ESC key
            color_print("ESC key is pressed.", "green")
            break

        frame = reduction_image(frame, 640, 480)
        writer.write(frame)

    capture.release()
    writer.release()


def main():
    make_preview_movie("movie.mp4", "preview")


if __name__ == "__main__":
    main()
