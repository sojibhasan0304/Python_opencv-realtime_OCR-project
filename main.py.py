import cv2 #this is for loade the OpenCV library for image, camera
import pytesseract #This is another library for OCR or text detaction for read the text

# I am Seting Tesseract path which in my c deive 
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe" 

# now the ORC function start. This ORC function give us a frame on our screen.
# This frame for an image which actully we want to raed. And this triple quotes shows what it will do. 
def run_ocr_on_frame(frame):
    """
    Run Tesseract OCR on a single frame (ROI) and return the text.
    This expects only the region of interest (ROI), not the full camera frame.
    """
    # Convert to grayscale
    # "cv2.cvtColor" will converts the image from one color format to another one.
    # Here BGR color ot Gray it's means gray is not recognizable color. 
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Slight blur to reduce small noise
    # I had used the Gaussian blur filter. which is very small  kernel. size:3×3 filter.
    # And "0" for automatically calculates the noise by OpenCV .
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    # Adaptive threshold – helps for uneven lighting
    # this stpe for converting the grayscale image into a pure black & white image
    gray = cv2.adaptiveThreshold(
        gray,#the input grayscale image
        255, #value for white pixelsq
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,#type of thresholdingq
        31,   #block size (odd number)
        10    #constant subtracted from mean
    )

    # This part for better reading where we will enlarge the image to make text bigger before sending to Tesseract.
    # I have used fx=2.0 and fy=2.0 that means the size of scale width and height.
    # Alos inter cubic is a function that has high-quality for interpolation method. 
    gray = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)

    # Tesseract config
    #  I wnat to read only english so I had added -l eng for text in English
    config = "--oem 3 --psm 6 -l eng"
    text = pytesseract.image_to_string(gray, config=config)

    return text.strip()


def main():
    # I Created a VideoCapture object to access my webcam.
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened(): # if it's not work It will show "cannot open camre"
        print("❌ Cannot open camera.")
        return

    print("📷 Real-Time OCR with Tesseract (Zoom Box Version)")
    print("Controls:")
    print("  ➜ Click once on the camera window so it gets keyboard focus.")
    # this for capture photo which I need to press 
    print("  ➜ Press 'o' to run OCR inside the green box.")
    # and this is a keyboard interption so that I can exit any time I want. and the program will off.
    print("  ➜ Press 'q' or ESC to quit.\n")

    # It will store last text what was in screen
    last_text = ""
     # This is my main loop: it will continuously grab the frames from the camera and process them for showing 
    while True:
        ret, frame = cap.read()
        # if it's failed it will disconnect
        if not ret:
            print("❌ Failed to grab frame.")
            break

        # This is for the littel windows. and I have fixed this hight and wight. 
        h, w = frame.shape[:2]

    
        box_w = int(w * 0.5)  # width is 50% of frame width and
        box_h = int(h * 0.4)  # height is  40% of frame height

        x1 = w // 2 - box_w // 2
        y1 = h // 2 - box_h // 2
         #  for computing bottom-right coordinates
        x2 = x1 + box_w
        y2 = y1 + box_h

        # for drawing the green rectangle box
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # it will show the last OCR result on the frame
        if last_text:
            y0 = 30
            for i, line in enumerate(last_text.split("\n")):
                y = y0 + i * 30
                cv2.putText(
                    frame,
                    line,
                    (10, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )

        # for showing main camera frame
        cv2.imshow("Tesseract OCR (o = OCR in box, q/ESC = quit)", frame)

        # Also this function for show a zoom box to preview the box area
        roi = frame[y1:y2, x1:x2]
        roi_zoom = cv2.resize(roi, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_LINEAR)
        cv2.imshow("Zoom Area (scanned region)", roi_zoom)

        key = cv2.waitKey(1) & 0xFF

        # to exit on 'q' or ESC (27)
        if key == ord('q') or key == 27:
            print("⛔ Exit key pressed. Exiting.")
            break

        # Run OCR on the ROI when 'o' is pressed
        if key == ord('o'):
            print("📖 Running OCR on the zoom box region")
            last_text = run_ocr_on_frame(roi)

            print("\nEXTRACTED TEXT (from zoom box)\n")
            print(last_text)
            print("\n(Press 'o' again for new OCR, 'q' or ESC to quit.)\n")

    # for releasing the camrea 
    cap.release()
    # for closing all windows 
    cv2.destroyAllWindows()
    print("✅ Camera released. Program ended.")

#This function makes sure us that 'main()' runs only when this file is executed directly,
if __name__ == "__main__":
    main()
