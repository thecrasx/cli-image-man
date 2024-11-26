from setuptools import setup

setup(
    name = "cli_img_man",
    version = "0.5",
    description = "CLI application for image manipulation",
    py_modules = ["cli", "image_manipulation"],
    install_requires = [
        "Click",
        "Pillow",
        "PyExifTool"
    ],
    entry_points={
        'console_scripts': [
            'cli = cli:cli',
        ],
    }
)