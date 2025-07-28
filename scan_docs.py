# # import cv2
# # import numpy
# # import matplotlib
# # import pytesseract
# # from matplotlib import pyplot as plt
# #
# #
# # def better_img(img):
# #     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# #
# #
# #
# # img = cv2.imread(r'scans\photo_2025-05-31_19-48-10.jpg')
# # img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
# #
# #
# #
# # cv2.waitKey(0)
# from idlelib.outwin import file_line_pats
import pytesseract.pytesseract as ptes
import matplotlib.pyplot as plt
import cv2
import json
import numpy as np
from fontTools.varLib.builder import buildMultiVarData
from skimage.io import imread
from skimage.morphology import area_closing

ptes.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class ImgScaner():
    def __init__(self, photo_path):



    def get_img(photo_path):
        img = cv2.imread(photo_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        # img = cv2.resize(img, (1920, 1080))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        kernel = np.ones((2, 2), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        # thresh = cv2.resize(thresh, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        # cv2.imshow('name', img)
        return thresh

    def get_text(self, img):
        config = r'--oem 3 --psm 6'
        # text = ptes.image_to_string(img,config = config,  lang='rus')
        # data = ptes.image_to_data(img, config= config, lang='rus')
        text = ptes.image_to_string(img, config="--oem 3 --psm 6   -c tessedit_char_whitelist=1234567890оОOoxXхХiI!|")
        return text


    def get_structure_data(self, img, areas, page_num):
        k_work = 6
        k_numb = 6

        x, y, w, h = areas['id_exp']
        roi_exp = img[y:y + h, x:x + w]
        id_exp = get_text(roi_exp).replace('\n', '')
        result = [id_exp, dict()]
        for work_n in range(1, k_work):
            values = areas[f'work{work_n}']
            print(1)
            x, y, w, h = values['id']
            work_id_roi = img[y:y + h, x:x + w]
            work_id_text = get_text(work_id_roi).replace('\n', '')

            result[1][work_id_text] = {f'{n}': None for n in range(1, k_numb + 1)}
            for numb in range(1, k_numb + 1):
                x, y, w, h = values[f'{numb}']
                numb_roi = img[y:y + h, x:x + w]
                values[f'{numb}'] = get_text(numb_roi)
                result[1][work_id_text][f'{numb}'] = get_text(numb_roi).replace('\n', '')
                cv2.imwrite(f'nums/{page_num}/{work_n}_{numb}.jpg', numb_roi)

        print('----------------------------------')

        return result
    pass









def get_ROIs(path:str):
    with open(path,'r', encoding='utf-8') as file:
        areas = json.load(file)
    return areas


def correct_data():
    pass



def main():
    file_path = r"C:\Users\us3r02\PycharmProjects\ege_doc_scan\scans\1.jpg"

    img = get_img(file_path)

    areas = get_ROIs('ROIs.json')
    x, y, w, h = areas[f'work{1}']['id']
    roi = img[y:y+h, x:x+w]

    roi = cv2.resize(roi, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    kernel = np.ones((2, 2), np.uint8)
    roi = cv2.convertScaleAbs(roi, alpha=1.5, beta=-50)
    roi = cv2.morphologyEx(roi, cv2.MORPH_OPEN, kernel)


    print(*get_structure_data(img, areas, 1), sep='\n')
    print(get_text(roi))
    cv2.imshow('name', roi)


    plt_pic = plt.imread(r'C:\Users\us3r02\PycharmProjects\ege_doc_scan\scans\1.jpg')
    im = plt.imshow(plt_pic)
    plt.show()
    # im = plt.imshow(np.flipud(plt.imread('new_pic.jpg')), origin='lower')
    # plt.show()


if __name__ == "__main__":
    main()