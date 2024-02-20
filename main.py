import cv2 
from image_processing import  getContourByColor, getCard, flipCard, detectText, addCard, colors_
  
vid = cv2.VideoCapture(1)
last_color = None
i = 0
card = None
pos = 0 
freq = 5
while (True): 
    ret, image = vid.read() 

    cv2.imshow('frame', image) 

    if cv2.waitKey(1) & 0xFF == ord('q'): 
        break
    if cv2.waitKey(1) & 0xFF == ord('s'):
        cv2.imwrite("test.png", image) 
        print("image saved")
        break
    

    if cv2.waitKey(1) & 0xFF == ord(' '):
        for color in ["red", "green", "blue", "yellow", "violet"]:
            contour, pos_new = getContourByColor(image, color, masks_json="masks_camera.json")
            if pos_new:
                pos = pos_new
                card = getCard(image, contour)
                if card:
                    box_color = color
                    card_flipped = flipCard(card[0])
                    image = addCard(image, card_flipped, colors_[box_color], pos)

                    detectText(card_flipped)
        cv2.imshow('frame', image)
        cv2.waitKey(0)

    cv2.imshow('frame', image)
    
vid.release() 
cv2.destroyAllWindows() 