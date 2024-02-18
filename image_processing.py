import cv2
import numpy as np
import json
from random import randint 
import easyocr

def sortPointsOfContourForAT(contour: np.array)->np.array:
    ret = np.reshape(contour, (4, 2)).astype(np.float32)
    a = ret[0]
    c, b = sorted(ret, key = lambda x: np.linalg.norm(x-a))[1:3]
    return np.float32([a, b, c])


def simplifyContour(contour:np.array, n_corners: int=4, max_iter: int=100)->np.array:
    lb, ub = 0., 1.
    for _ in range(max_iter):
        k = (lb + ub)/2.
        eps = k*cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, eps, True)

        if len(approx) > n_corners:
            lb = (lb + ub)/2.
        elif len(approx) < n_corners:
            ub = (lb + ub)/2.
        else:
            return approx
    return contour


def getContourByColor(image: np.array, color: str, masks_json: str="masks_test.json", show: bool=False)->tuple:
    image = image.copy()
    with open(masks_json, 'r', encoding='utf-8') as json_file:
        colors = json.load(json_file)

    assert color in colors, f"COLOR ERROR: color must be among: {list(colors.keys())}!"
    
    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    THRESH = cv2.inRange(image_hsv, np.asarray(colors[color]["low"], dtype=np.uint8), np.asarray(colors[color]["high"], dtype=np.uint8))

    CONTOURS, _  = cv2.findContours(THRESH.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    
    cntr = max(CONTOURS, key = lambda x: cv2.contourArea(x))   
    
    cntr = cv2.convexHull(cntr)
    cntr = simplifyContour(cntr)
    x, y, _ = image.shape
    image_corners = [
        (x, 0),
        (0, 0),
        (0, y),
        (x, y)
        ]
    pos = image_corners.index(max(image_corners, key=lambda x: np.linalg.norm(cntr-x)))+1
    if show:
        cv2.drawContours(image, [cntr], -1, (0, 255, 0), 2)
        cv2.imshow("Contours", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    return cntr, pos
    
    
def getCard(image: np.array, contour: np.array, show=False)->np.array:
    x, y, _ = image.shape
    pts1 = sortPointsOfContourForAT(contour)
    pts2 = np.float32([[[20, 20]], [[250, 20]], [[20, 150]]])
    M = cv2.getAffineTransform(pts1,pts2)
    dst = cv2.warpAffine(image,M,(y, x))
    dst = dst[20:150, 20:250]
    if show:
        cv2.imshow("Card", dst)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    return dst


def addCard(image: np.array, card: np.array, color: tuple, qarter: int, show: bool=False)->np.array:
    ret = image.copy()
    x_i, y_i, _ = image.shape
    x_c, y_c, _ = card.shape
    offset = 5
    assert 0 < qarter and qarter < 5, "qarter must be between 1 and 4"
    if qarter == 1:
        pts = np.array([[-offset+y_i-y_c, offset], [-offset+y_i-y_c, x_c+offset], [-offset+y_i, x_c+offset], [-offset+y_i, offset]], np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.polylines(ret, [pts], isClosed=True, color=color, thickness=10)
        ret[0+offset:x_c+offset, y_i-y_c-offset:y_i-offset] = card
    elif qarter == 2:
        pts = np.array([[offset, offset], [offset, x_c+offset], [y_c+offset, x_c+offset], [y_c+offset, offset]], np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.polylines(ret, [pts], isClosed=True, color=color, thickness=10)
        ret[0+offset:x_c+offset, offset:y_c+offset] = card
    elif qarter == 3:
        pts = np.array([[offset, -offset+x_i-x_c], [offset, -offset+x_i], [y_c+offset, -offset+x_i], [y_c+offset, -offset+x_i-x_c]], np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.polylines(ret, [pts], isClosed=True, color=color, thickness=10)
        ret[x_i-x_c-offset:x_i-offset, offset:y_c+offset] = card
    elif qarter == 4:
        pts = np.array([[-offset+y_i-y_c, -offset+x_i-x_c], [-offset+y_i-y_c, -offset+x_i], [-offset+y_i, -offset+x_i], [-offset+y_i, -offset+x_i-x_c]], np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.polylines(ret, [pts], isClosed=True, color=color, thickness=10)
        ret[x_i-x_c-offset:x_i-offset, y_i-y_c-offset:y_i-offset] = card
    if show:
        cv2.imshow("Adding card", ret)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    return ret 
    
    
def detectText(image: np.array) -> np.array:
    reader = easyocr.Reader(['en'], gpu=False)
    text = reader.readtext(image)
    print(max(text, key = lambda x: x[-1])[1])
    

def flipCard(card: np.array) -> np.array:
    gray = cv2.cvtColor(card, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, threshold1=30, threshold2=100)
    x, y = edges.shape
    x_offset, y_offset = np.asarray(np.asarray(edges.shape)*0.05).astype(np.int32)
    
    right_top = cv2.countNonZero(edges[x_offset:x//2-x_offset, y//2+y_offset:y-y_offset])
    right_bottom = cv2.countNonZero(edges[x_offset+x//2:x-x_offset, y//2+y_offset:y-y_offset])
    left_top = cv2.countNonZero(edges[x_offset:x//2-x_offset, y_offset:y//2-y_offset])
    left_bottom = cv2.countNonZero(edges[x_offset+x//2:x-x_offset, y_offset:y//2-y_offset])
    
    list_val = [right_top, left_top, left_bottom, right_bottom]
    smallest = list_val.index(min(list_val))
    
    if smallest == 0:
        # right_top
        return card
    elif smallest == 1:
        # left_top
        return cv2.flip(card, 1)
    elif smallest == 2:
        # left_bottom
        return cv2.flip(cv2.flip(card, 0), 1)
    elif smallest == 3:
        # right_bottom
        return cv2.flip(card, 0)
    return card 


colors_ = {
    "red": (0,0,255), 
    "green": (0,255,0), 
    "blue": (255,0,0), 
    "yellow": (0,200,255), 
    "violet": (255,0,100)
}

if __name__ == "__main__":
    for color in ["red", "green", "blue", "yellow", "violet"]:
        image = cv2.imread(f"images/test/{color}.png")
        contour, pos = getContourByColor(image, color)
        card = getCard(image, contour)
        card = flipCard(card)
        # detectText(card)
        addCard(image, card, colors_[color], pos, 1)
    