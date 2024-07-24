import os
from typing import Callable, List, Union
import torch
import PIL.Image
import PIL.ImageOps
import requests

def load_image(
    image: Union[str, PIL.Image.Image], convert_method: Callable[[PIL.Image.Image], PIL.Image.Image] = None
) -> PIL.Image.Image:
    if isinstance(image, str):
        if image.startswith("http://") or image.startswith("https://"):
            image = PIL.Image.open(requests.get(image, stream=True).raw)
        elif os.path.isfile(image):
            image = PIL.Image.open(image)
        else:
            raise ValueError(
                f"Incorrect path or URL. URLs must start with `http://` or `https://`, and {image} is not a valid path."
            )
    elif isinstance(image, PIL.Image.Image):
        image = image
    else:
        raise ValueError(
            "Incorrect format used for the image. Should be a URL linking to an image, a local path, or a PIL image."
        )

    image = PIL.ImageOps.exif_transpose(image)

    if convert_method is not None:
        image = convert_method(image)
    else:
        image = image.convert("RGB")

    return image

def draw_mask(
    init_image: Union[str, PIL.Image.Image], 
    ref_image: Union[str, PIL.Image.Image],
    params: List[float] = None,
    savepath: str = None
):
    if len(params) != 3:
        raise ValueError("The parameters must be a list containing three values.")
    
    CENTER_ROW_FROM_TOP, CENTER_COL_FROM_LEFT, SCALE = params
    
    init_image = load_image(init_image)
    init_width, init_height = init_image.size
    ref_image = load_image(ref_image)
    w, h = ref_image.size
    aspect_ratio = h / w

    if aspect_ratio > 1:
        width = int(SCALE * 256 / aspect_ratio)
        height = int(SCALE * 256)
    else:
        width = int(SCALE * 256)
        height = int(SCALE * 256 * aspect_ratio)

    center_row_rm = int(CENTER_ROW_FROM_TOP * init_height)
    center_col_rm = int(CENTER_COL_FROM_LEFT * init_width)

    step_height2, remainder = divmod(height, 2)
    step_height1 = step_height2 + remainder
    step_width2, remainder = divmod(width, 2)
    step_width1 = step_width2 + remainder

    save_mask = torch.zeros((init_height, init_width))
    save_mask[center_row_rm - step_height1: center_row_rm + step_height2, center_col_rm - step_width1: center_col_rm + step_width2] = 1
    mask_image = PIL.Image.fromarray((save_mask * 255).byte().numpy(), mode='L')

    if savepath:
        mask_image.save(savepath)

if __name__ == "__main__":
    #path = './benchmark/Custom/a professional photograph of a yellow rubber duck and a cat on the bed, ultra realistic/'
    path = './benchmark/Custom/0008 a cartoon animation of a panda in the forest/'
    init_image = path + 'bg58.png'
    ref_image = path + 'fg_63da0587b82cf5cb1db7fef0_2.jpg'
    params = [0.8, 0.3, 0.5]    # CENTER_ROW_FROM_TOP, CENTER_COL_FROM_LEFT, SCALE
    draw_mask(init_image, ref_image, params, path + "mask1.jpg")
