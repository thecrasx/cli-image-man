from os.path import exists as file_exists
from tempfile import gettempdir
from pathlib import Path
from enum import Enum
import numpy as np

from PIL import Image, ImageFilter
from PIL.Image import Resampling
import click


class ImageBlur(Enum):
    Simple = 10
    Box = 20
    Gaussian = 30


class ImageMan:
    def __init__(self, path: str, save_temp: bool = True):
        self.__path = path
        self.__image = Image.open(path)

        # If save_temp = true -> saves original image into temp directory
        # if self.save() overwrites the original image
        if save_temp:
            self.__original = self.copy()

            tmp_dir = gettempdir()

            if not tmp_dir[-1] in ("\\", "/"):
                tmp_dir += "\\" if "\\" in tmp_dir else "/"
            
            self.__tempPath = tmp_dir + "tmp-" + Path(self.__image.filename).name
        else:
            self.__original = None
            self.__tempPath = ""


    @property
    def mode(self) -> str:
        return self.__image.mode

    @property
    def tempPath(self) -> str:
        return self.__tempPath

    def size(self) -> tuple[int, int]:
        return self.__image.size



    def getMetaData(self):
        from PIL.ExifTags import TAGS
        exif_data = self.__image.getexif()

        for tag_id in exif_data:
            tag = TAGS.get(tag_id, tag_id)
            content = exif_data.get(tag_id)
            if isinstance(content, bytes):
                content = content.decode()
            click.echo(f'{tag:25}: {content}')
        click.echo("") 




    def getMetaDataWithExifTool(self) -> tuple[dict, dict]:
        from exiftool import ExifToolHelper

        try:
            elements = {}
            element_max_string = {} 
            with ExifToolHelper() as et:
                metadata = et.get_metadata(self.__path)

                for x in metadata:
                    for k in x:
                        if ":" in k:
                            el, sub_el = k.split(":")

                        else:
                            el = "0-kwargs"
                            sub_el = k

                        data = elements.get(el)
                        
                        if data is None:
                            elements[el] = [(sub_el, x[k])]
                        else:
                            data.append((sub_el, x[k]))

                        el_max_str = element_max_string.get(el)
                        if el_max_str is None:
                            element_max_string[el] = len(sub_el)
                        elif el_max_str < len(sub_el):
                            element_max_string[el] = len(sub_el)

            
            return elements, element_max_string

        except FileNotFoundError:
            click.echo("ExifTool not found")
            return (None, None)



    def save(self, path: str = None, overwrite: bool = False):
        if path is not None:
            if not overwrite and file_exists(path):
                raise FileExistsError
            
            self.__image.save(path)

        elif overwrite:
            if self.__original is not None:

                self.__original.save(self.__tempPath)

            self.__image.save(self.__path)

    
    def preview(self):
        self.__image.show("Image Preview")
            


    def copy(self) -> Image.Image:
        """
        Copies this image. Use this method if you wish to paste things
        into an image, but still retain the original.
        """
        return self.__image.copy()




    def changeOpacity(self, opacity):
        if self.__image.mode != "RGBA":
            self.__image = self.__image.convert("RGBA")

        img_array = np.array(self.__image, np.uint8)
        img_array[:, :, 3] = np.round(img_array[:, :, 3] * (opacity / 100)).astype(np.uint8)
        
        self.__image = Image.fromarray(img_array)




    def resize(self, width: int, height: int):
        self.__image = self.__image.resize((width, height))



    def blur(self, blur: ImageBlur = ImageBlur.Simple, radius: float = 0.0):
        match blur:
            case ImageBlur.Gaussian:
                self.__image = self.__image.filter(ImageFilter.GaussianBlur(radius))

            case ImageBlur.Box:
                self.__image = self.__image.filter(ImageFilter.BoxBlur(radius))

            case ImageBlur.Simple | _:
                self.__image = self.__image.filter(ImageFilter.BLUR)




    def changeMode(self, mode: str):
        self.__image = self.__image.convert(mode.upper())





    def rotate(self, angle: float, resample: Resampling = Resampling.NEAREST, 
            expand: bool = 0, center: tuple[float, float] = None,
            translate: tuple[float, float] = None
        ):

        self.__image = self.__image.rotate(angle, resample, expand, center, translate)







if __name__ == "__main__":
    im = ImageMan("./img.JPEG", False)
    im.save("./aa.png", quality = 3)