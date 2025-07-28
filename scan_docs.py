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
from torch.utils.benchmark.op_fuzzers.spectral import power_range

ptes.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class ImgScaner():
    def __init__(self, photo_path: str):
        self.photo_path = photo_path
        self.img = self.get_img(self.photo_path)
        self.areas = self.get_ROIs()

    def get_ROIs(self):
        with open(r'ROIs.json', 'r', encoding='utf-8') as file:
            areas = json.load(file)
        return areas

    def correct_data(self):
        pass


    def get_img(self, photo_path):
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


    def get_structure_data(self):
        k_work = 6
        k_numb = 6
        img = self.img
        areas = self.areas

        x, y, w, h = areas['id_exp']
        roi_exp = img[y:y + h, x:x + w]
        id_exp = self.get_text(roi_exp).replace('\n', '')

        result = [id_exp, dict()]

        for work_n in range(1, k_work):

            values = areas[f'work{work_n}']
            x, y, w, h = values['id']
            work_id_roi = img[y:y + h, x:x + w]
            work_id_text = self.get_text(work_id_roi).replace('\n', '')

            result[1][work_id_text] = {f'{n}': None for n in range(1, k_numb + 1)}

            for numb in range(1, k_numb + 1):

                x, y, w, h = values[f'{numb}']
                numb_roi = img[y:y + h, x:x + w]
                values[f'{numb}'] = self.get_text(numb_roi)

                result[1][work_id_text][f'{numb}'] = self.get_text(numb_roi).replace('\n', '')

                cv2.imwrite(f'nums/1/{work_n}_{numb}.jpg', numb_roi)

        return result
    pass

def main():

    all_scans_data = []
    k_scans = 2

    for n_file in range(1, k_scans+1):
        file_path = rf"scans\{n_file}.jpg"
        scan_object = ImgScaner(file_path)
        all_scans_data.append(scan_object.get_structure_data())


    print(all_scans_data)
    return all_scans_data
    # plt_pic = plt.imread(r'C:\Users\us3r02\PycharmProjects\ege_doc_scan\scans\1.jpg')
    # im = plt.imshow(plt_pic)
    # plt.show()
    # im = plt.imshow(np.flipud(plt.imread('new_pic.jpg')), origin='lower')
    # plt.show()


if __name__ == "__main__":
    main()