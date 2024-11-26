from image_manipulation import ImageMan, ImageBlur

from sys import exit as sys_exit
import click



class ImageManCLI(ImageMan):
    def __init__(self, path: str, save_temp: bool = True):
        try:
            super().__init__(path, save_temp)
        except FileNotFoundError:
            click.echo("Load error: Image not found.", err = True)
            click.echo("          - Check the input path.")
            sys_exit(1)

        self.cli_overwrite: bool = False
        self.cli_preview: bool = False
        self.cli_verbose: bool = False
        self.cli_save: str = None

pass_imc = click.make_pass_decorator(ImageManCLI, ensure=True)





@click.group(chain = True)
@click.option("--input", "-i", type = click.STRING, metavar = "<text>", help = "Input path", required = True)
@click.option("--out", "-o", type = click.STRING, metavar = "<text>", help = "Output path")
@click.option("--overwrite", "-ow", is_flag = True, help = "Overwrites given image")
@click.option("--preview", "-p", is_flag = True, help = "Opens image in native Preview application")
@click.option("--verbose", "-v", is_flag = True)
@click.option("--no-temp", "-nt", is_flag = True, help = "Doesn't save original image in temp dir if it's overwritten")
@click.pass_context
def man(ctx, input, no_temp, verbose, preview, out, overwrite):
    if input is None:
        click.echo("Please provide input path with --input or -i")
        sys_exit(1)

    imc = ImageManCLI(input, not no_temp)
    imc.cli_preview = preview
    imc.cli_verbose = verbose
    imc.cli_save = out
    imc.cli_overwrite = overwrite

    ctx.obj = imc
    ctx.call_on_close(call_on_close)





@man.command(help = "Image Manipulation")
@click.option("--width", "-w", type = click.INT, metavar = "<int>")
@click.option("--height", "-h", type = click.INT, metavar = "<int>")
@click.option("--opacity", "-op", type = click.FLOAT, metavar="<float>", help = "Change image opacity. Input: percentage [0.0 - 100.0]")
@click.option("--mode", "-m", type = click.STRING, metavar = "<text>", help = "Change image mode (ex: RGB -> RGBA). Input: [rgb, rgba, l, cmyk, ...]")
@pass_imc
def im(imc: ImageManCLI, width, height, opacity, mode):

    if width is not None or height is not None:

        # Calculate another argument if only one is provided
        # to keep original aspect ratio
        if width is None:
            width  = height * imc.size[0] // imc.size[1]
        elif height is None:
            height = width * imc.size[1] // imc.size[0]

        imc.resize(width, height)

        if imc.cli_verbose:
            click.echo("Image resized:")
            click.echo(f"    - Width: {width}")
            click.echo(f"    - Height: {height}")

    
    if opacity is not None:
        imc.changeOpacity(opacity)

        if imc.cli_verbose:
            click.echo(f"Opacity changed: {opacity}%")

    if mode is not None:
        try:
            p_mode = imc.mode
            imc.changeMode(mode)

            if imc.cli_verbose:
                click.echo(f"Image converted: {p_mode} -> {mode.upper()}")

        except ValueError as e:
            click.echo(f"Conversion Error: {e}", err = True)
            sys_exit(1)





@man.command()
@click.option("--blur-simple", "-bs", is_flag = True)
@click.option("--blur-box", "-bb", type = click.INT, metavar = "<int>", default = 0, help = "Input: radius")
@click.option("--blur-guassian", "-bg", type = click.INT, metavar = "<int>", default = 0, help = "Input: radius")
@pass_imc
def filter(imc: ImageManCLI, blur_simple, blur_box, blur_guassian):
    if blur_simple:
        imc.blur()
        
        if imc.cli_verbose:
            click.echo("Filter Applied: Simple Blur")

    if blur_box > 0:
        imc.blur(ImageBlur.Box, blur_box)

        if imc.cli_verbose:
            click.echo(f"Filter Applied: Box Blur (radius = {blur_box})")

    if blur_guassian > 0:
        imc.blur(ImageBlur.Gaussian, blur_guassian)

        if imc.cli_verbose:
            click.echo(f"Filter Applied: Guassian Blur (radius = {blur_guassian})")





# EXTRACT METADATA WITH EXIFTOOL
@man.command()
@pass_imc
def metadata(im: ImageManCLI):
    elements, max_str = im.getMetaDataWithExifTool()

    if elements is None:
        click.echo("No Metadata")
        sys_exit(1)


    def format_string(data, max_str, el_size):
        if el_size == 1:
            return f"    {data[0]}: {data[1]}"
        else:
            return f"    {data[0]:{max_str}}: {data[1]}"


    el_size = len(elements["0-kwargs"])
    str_size = max_str["0-kwargs"] + 3
    for data in elements["0-kwargs"]:
        click.echo(format_string(data, str_size, el_size))
    click.echo("\n", nl = False)

    for e in elements:
        if e != "0-kwargs":
            el_size = len(elements[e])
            str_size = max_str[e] + 3
            click.echo(e)
            for data in elements[e]:
                click.echo(format_string(data, str_size, el_size))
            click.echo("\n", nl = False)





@man.command()
@click.option("--angle", "-a", required = True, type = click.FLOAT, metavar="<float>", help = "In degrees counter clockwise")
@click.option("--expand", "-e", is_flag = True, help = "Optional expansion flag")
@click.option("--center", "-c", nargs = 2, type = click.FLOAT, metavar="<float> <float>", help = "Optional center of rotation")
@click.option("--translate", "-t", nargs = 2, type = click.FLOAT, metavar="<float> <float>", help = "An optional post-rotate translation")
@pass_imc
def rotate(imc: ImageManCLI, angle, expand, center, translate):
    imc.rotate(angle = angle, expand = expand, center = center, translate = translate)





@pass_imc
def call_on_close(imc: ImageManCLI):
    if imc.cli_preview:
        imc.preview()

    if imc.cli_save is not None:
        try:
            imc.save(imc.cli_save, imc.cli_overwrite)
        except FileExistsError:
            click.echo()
            click.echo("Save error: Image already exists.", err = True)
            click.echo("          - You can overwrite it with '--overwrite' or '-ow' command")
            sys_exit(1)

        if imc.cli_verbose:
            click.echo(f"Image has been saved [{imc.cli_save}]")

    elif imc.cli_overwrite:
        imc.save(overwrite=imc.cli_overwrite)

        if imc.cli_verbose:
            click.echo(f"Image has been overwritten")

            if imc.tempPath != "":
                click.echo(f"   - Original image has been saved at: {imc.tempPath}")




if __name__ == "__main__":
    import sys
    if getattr(sys, 'frozen', False):
        man(sys.argv[1:])
    else:
        man()