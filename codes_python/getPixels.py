import numpy as np


def get_pixels(cent_x, cent_y, A, B, alpha, image):
    def compute_bounding_lines(A, B, cent_x, cent_y, alpha):
        vecR = np.array([cent_x, cent_y])
        vecA = np.array([A * np.cos(alpha), A * np.sin(alpha)])
        vecB = np.array([B * np.cos(alpha + np.pi / 2), B * np.sin(alpha + np.pi / 2)])
        # four corners of the box
        TL = vecR - vecA + vecB
        TR = vecR + vecA + vecB
        BL = vecR - vecA + vecB
        BR = vecR + vecA + vecB
        # define four bounding lines
        if abs(np.tan(alpha)) > 0:
            tgA = np.tan(alpha)
            tgA2 = np.tan(alpha + np.pi / 2)
            L1 = np.array([tgA, -1, TR[1] - tgA * TR[0]])
            L2 = np.array([tgA, -1, BL[1] - tgA * BL[0]])
            L3 = np.array([tgA2, -1, BL[1] - tgA2 * BL[0]])
            L4 = np.array([tgA2, -1, TR[1] - tgA2 * TR[0]])
        else:
            L1 = np.array([0, 1, -TR[1]])
            L2 = np.array([0, 1, -BL[1]])
            L3 = np.array([1, 0, -BL[0]])
            L4 = np.array([1, 0, -TR[0]])
        return BL, BR, L1, L2, L3, L4, TL, TR

    def isect(a, b, c):
        return (c - b) / a

    def compute_x_on_line(BL, L1, L2, L3, L4, TR, line, alpha):
        if abs(np.tan(alpha)) > 0:
            x1 = isect(L1[0], L1[2], line)
            x2 = isect(L2[0], L2[2], line)
            x3 = isect(L3[0], L3[2], line)
            x4 = isect(L4[0], L4[2], line)
        else:
            x1 = -np.inf
            x2 = np.inf
            x3 = BL[0]
            x4 = TR[0]
        # remove min and max
        x = sorted([x1, x2, x3, x4])[1:-1]
        return x

    def get_left_right_x_from_cornerpoints(x_bot, x_top):
        x_sort = np.ceil(sorted(x_top + x_bot)).astype(int)
        x_lef = x_sort[0]
        x_rig = x_sort[-1]
        return x_lef, x_rig

    def get_pixels_from_row(x_lef, x_rig, y):

        x_lef = 0 if x_lef < 0 else x_lef
        x_lef = ncol if x_lef > ncol else x_lef

        x_rig = 0 if x_rig < 0 else x_rig
        x_rig = ncol if x_rig > ncol else x_rig

        res1 = np.concatenate((X_pixels, np.array([x for x in range(x_lef, x_rig + 1)])))
        res2 = np.concatenate((Y_pixels, np.array([y for _ in range(x_rig - x_lef + 1)])))
        res3 = np.concatenate((Z_pixels, image[y, x_lef:x_rig + 1]))

        return res1, res2, res3


    X_pixels = np.array([])
    Y_pixels = np.array([])
    Z_pixels = np.array([])

    nrow, ncol = image.shape[:2]

    BL, BR, L1, L2, L3, L4, TL, TR = compute_bounding_lines(A, B, cent_x, cent_y, alpha)

    # define box pixel borders (four lines perpendicular to axes and passing through box four corners)
    box_top = np.floor(np.max([TL[1], TR[1], BL[1], BR[1]])).astype(int)  # first horizontal line from the top to cut the box
    box_bot = np.ceil(np.min([TL[1], TR[1], BL[1], BR[1]])).astype(int)  # first horizontal line from the bottom to cut the box

    y = np.min([box_top, nrow - 1]).astype(int)

    if y < 0:
        return X_pixels, Y_pixels, Z_pixels

    line_top, line_bot = y - 1, y - 1

    # intersect with all four lines
    x_top = compute_x_on_line(BL, L1, L2, L3, L4, TR, line_top, alpha)
    x_bot = x_top[:]

    # align with pixels
    x_lef, x_rig = get_left_right_x_from_cornerpoints(x_bot, x_top)

    if (x_lef < 0 and x_rig) < 0 or (x_lef > ncol and x_rig > ncol):
        return X_pixels, Y_pixels, Z_pixels

    X_pixels, Y_pixels, Z_pixels = get_pixels_from_row(x_lef,x_rig,y)

    beg = y

    if y == 0 or box_bot > nrow:
        return X_pixels, Y_pixels, Z_pixels

    # INTERMEDIATE PIXELS
    # cycle through pixels from top to bottom
    start = max(max(box_bot, 0), beg)
    end = min(max(box_bot, 0), beg) - 1

    for y in range(start, end, -1):
        # for each y we need to determine the left and right border
        # intersections from previous round
        x_top = x_bot

        # pixel line

        line_top = line_bot
        line_bot = line_top - 1

        # do only intersection with bottom line
        x_bot = compute_x_on_line(BL, L1, L2, L3, L4, TR, line_bot, alpha)

        # align with pixels
        x_lef, x_rig = get_left_right_x_from_cornerpoints(x_bot, x_top)
        X_pixels, Y_pixels, Z_pixels = get_pixels_from_row(x_lef, x_rig, y)

        # LAST LINE OF PIXELS

        if y != 0:
            y = box_bot
            x_top = x_bot
            # align with pixels
            x_lef, x_rig = get_left_right_x_from_cornerpoints(x_bot, x_top)

            X_pixels, Y_pixels, Z_pixels = get_pixels_from_row(x_lef, x_rig, y)

    return X_pixels, Y_pixels, Z_pixels


if __name__ == "__main__":
    image = np.random.rand(10, 10)

    cent_x = 4
    cent_y = 4
    A, B = 2, 2
    alpha = np.pi/2

    r = get_pixels(cent_x, cent_y, A, B, alpha, image)
    print(r)
    for i in r:
        print(i.shape)