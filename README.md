# Command-Line Tool For Image Manipulation

```
Usage: cli.py [OPTIONS] COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...

Options:
  -i, --input <text>  Input path  [required]
  -o, --out <text>    Output path
  -ow, --overwrite    Overwrites given image
  -p, --preview       Opens image in native Preview application
  -v, --verbose
  -nt, --no-temp      Doesn't save original image in temp dir if it's
                      overwritten
  --help              Show this message and exit.

Commands:
  filter
  im        Image Manipulation
  metadata
  rotate
```

**Note:** Metadata extraction requires ExifTool
