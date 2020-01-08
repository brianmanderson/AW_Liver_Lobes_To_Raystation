__author__ = 'Brian M Anderson'
# Created on 1/8/2020
from Dicom_RT_and_Images_to_Mask.Image_Array_And_Mask_From_Dicom_RT import Dicom_to_Imagestack, np, os
from Dicom_RT_and_Images_to_Mask.Plot_And_Scroll_Images.Plot_Scroll_Images import plot_scroll_Image
'''
This project was halted because it was realized the images might not all be the same size... doing it within Raystation
is just more convenient
'''


def create_RT_On_Primary(path):
    Dicom_reader = Dicom_to_Imagestack(get_images_mask=True)
    for MRN in os.listdir(path):
        MRN_path = os.path.join(path,MRN)
        data_dict = {'Path':[],'Images':[],'Vals':[]}
        exams = []
        for _, exams, _ in os.walk(MRN_path):
            break
        for exam in exams:
            exam_path = os.path.join(MRN_path,exam)
            Dicom_reader.make_array(exam_path)
            Images = Dicom_reader.ArrayDicom
            non_min = np.where(Images>np.min(Images))
            if non_min:
                data_dict['Images'].append(Images)
                data_dict['Vals'].append(len(non_min[0]))
                data_dict['Path'].append(exam_path)
        primary = data_dict['Vals'].index(np.max(data_dict['Vals']))
        out_RT = np.zeros(data_dict['Images'][primary].shape)
        out_RT = np.expand_dims(out_RT, axis=-1)
        out_RT = np.repeat(out_RT, repeats=len(data_dict['Vals']), axis=-1)
        cast_index = 1
        for index in range(len(data_dict['Vals'])):
            if index == primary:
                continue
            Images = data_dict['Images'][index]
            output = np.zeros(Images.shape)
            output[Images>np.min(Images)] = 1
            out_RT[...,cast_index] = output


if __name__ == '__main__':
    pass
