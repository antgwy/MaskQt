from PIL import Image
import numpy as np
import os

def get_name_and_path(path):
    name_with_extension = os.path.basename(path)
    name, _ = os.path.splitext(name_with_extension)
    dir = os.path.dirname(path)
    if not dir.endswith('/'):
        dir += '/'
    return name, dir

def crop_mask_image(mask_path, image_path):
    mask = Image.open(mask_path)
    mask = mask.convert('RGB')
    image = Image.open(image_path)
    image = image.convert('RGB')

    mask_name, mask_dir = get_name_and_path(mask_path)
    image_name, image_dir = get_name_and_path(image_path)
    print(mask_dir, image_dir)

    data = np.array(mask)
    # print(data)

    white_areas = np.all(data == [255, 255, 255], axis=-1)

    # 确定白色区域的边界
    rows = np.any(white_areas, axis=1)
    cols = np.any(white_areas, axis=0)

    try:
        rmin, rmax = np.where(rows)[0][[0, -1]]
        cmin, cmax = np.where(cols)[0][[0, -1]]

        # 裁剪图像
        cropped_mask = mask.crop((cmin, rmin, cmax + 1, rmax + 1))
        cropped_image = image.crop((cmin, rmin, cmax + 1, rmax + 1))

        cropped_mask.save(mask_dir + f"{mask_name}_cropped.png")
        cropped_image.save(image_dir + f"{image_name}_cropped.png")
    except IndexError:
        print("No white areas found in the image.")

if __name__ == '__main__':
    mask_path = './cross-domain/seg_foreground/fg00_mask.png'
    image_path = './cross-domain/foreground/fg00.jpg'
    crop_mask_image(mask_path, image_path)