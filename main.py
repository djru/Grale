import argparse
import sys
import numpy as np
from PIL import Image
from typing import List, Tuple

DEFAULTS = {
    '14_pro_max': (2796, 1290),
    '14_pro': (1179, 852),
}

def hex_to_rgb(hex_code):
    """
    Converts a 6-digit hex color code to an RGB integer tuple (0-255).
    Example: 'FFA501' -> (255, 165, 1)
    """
    hex_code = hex_code.lstrip('#').upper()

    if len(hex_code) != 6:
        raise ValueError("Invalid hex code. Must be 6 digits.")

    # Convert two hex digits at a time to their decimal (base 10) value.
    # The '16' in int(..., 16) specifies the input is base 16 (hexadecimal).
    r = int(hex_code[0:2], 16)
    g = int(hex_code[2:4], 16)
    b = int(hex_code[4:6], 16)

    return (r, g, b)


# will be in the form ('#ffffff', 0.1)
def interpolate(points: List[Tuple[str, float]], num_steps: int, debug=False) -> List[Tuple[float, float, float]]:
    points = sorted(points, key=lambda p: p[-1])

    # we need the points to be collectively exhaustive
    # if there is no point on the ends then we must add them
    if points[0][1] != 0.0:
        zero_point = (points[0][0], 0.0)
        points = [zero_point, *points]
    if points[-1][1] != 100.0:
        final_point = (points[-1][0], 1.0)
        points = [*points, final_point]
    
    # convert hex to rgb tuple 
    points = [(hex_to_rgb(p[0]), p[1]) for p in points]


    interpolation = []

    # each row/col will have its color computed individually
    for step in range(0, num_steps):
        progress = step / num_steps
        
        # find out which pair of points this row/col falls between
        upper_point = None
        lower_point = None
        for i in range(len(points)): 
            # first point is ALWAYS 0, first step is 0, so firt point is NEVER the upper bound
            # we go until we find a point that is past this 
            # at the end, the final point is always 1, which is always > our progress
            if points[i][1] > progress:
                upper_point = points[i] 
                lower_point = points[i - 1]
                break
        
        (r1, b1, g1), p1 = lower_point
        (r2, b2, g2), p2 = upper_point

        progress_within_band = round((progress - p1) / (p2 - p1), 2)

        r3 = round(r1 + progress_within_band * (r2 - r1), 2)
        b3 = round(b1 + progress_within_band * (b2 - b1), 2)
        g3 = round(g1 + progress_within_band * (g2 - g1), 2)
        
        if debug:
            print('progress', progress, 'progress in band', progress_within_band, 'lower_point', lower_point, 'upper_point', upper_point, 'actual_point', (r3, b3, g3))

        interpolation.append((r3, b3, g3))
    
    return interpolation

def format_pixels(pixels, height, width, horizontal=False):
    pixels = np.array(pixels).astype(np.uint8)

    if horizontal:
        pixels = pixels[np.newaxis, :, :]
        pixels = np.tile(pixels, (height, 1, 1))
    else:
        pixels = pixels[:, np.newaxis, :]
        pixels = np.tile(pixels, (1, width, 1))

    return pixels

def generate():
    parser = argparse.ArgumentParser(prog='Grale', description='Generates image gradients')
    parser.add_argument('-g', '--gradient')
    parser.add_argument('-d', '--dim', default='512,512')
    parser.add_argument('-p', '--preset')
    parser.add_argument('-r', '--rotate', action='store_true')
    parser.add_argument('-o', '--output', default='/tmp/output.png')
    parser.add_argument('--debug', action='store_true')

    args = parser.parse_args()

    grad = args.gradient.split(',')
    if len(grad) < 2:
        print('Incorrect gradient', grad)
        sys.exit()
    
    # parse the gradient pairs which are passed as a string
    # the user can also give only colors without points, which will result in evenly spaced points
    if '#' in grad[-1]:
        grad = [(grad[i], (i) / (len(grad) - 1)) for i in range(len(grad))]
    else:
        grad = [(grad[i], float(grad[i + 1])) for i in range(0, len(grad), 2)]
    
    # allow the user to pass some pre set dimensions that match common device sizes
    if args.preset:
        if args.preset not in DEFAULTS:
            print('preset not found in defaults:', args.preset)
            print('please select one of these:', list(DEFAULTS.keys()))
            sys.exit()
        height, width = DEFAULTS.get(args.preset)
    else:
        height, width = [int(p) for p in args.dim.split(',')]

    # generate the 2d list of pixels for 1 row or col (depending on vertical or horizontal grad)
    pixels = interpolate(grad, width if args.rotate else height)

    # convert to 3d pixel np array
    pixels = format_pixels(pixels, height, width, args.rotate)

    # output and save
    img = Image.fromarray(pixels, 'RGB')
    img.save(args.output)
    
    print('image stops:', grad)
    print('image shape:', pixels.shape)
    print('image location:', args.output)
    
if __name__ == '__main__':
    main()