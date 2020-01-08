from connect import *
import os, copy
# import numpy as np


def down_folder_Secondary(output,input_path):
    folders = []
    files = []
    for _, folders, files in os.walk(input_path):
        break
    # if 'imported.txt' in files and 'primary_CT.txt' not in files:
    #     output.append(input_path)
    if 'primary_CT.txt' not in files:
        output.append(input_path)
    for directory in folders:
        new_directory = input_path + directory + '\\'
        down_folder_Secondary(output,new_directory)
    return output
def down_folder_primary(output,input_path):
    folders = []
    files = []
    for _, folders, files in os.walk(input_path):
        break
    # if 'imported.txt' in files and 'primary_CT.txt' not in files:
    #     output.append(input_path)
    if 'primary_CT.txt' in files:
        output.append(input_path)
    for directory in folders:
        new_directory = input_path + directory + '\\'
        down_folder_primary(output,new_directory)
    return output
class Make_Segments_Of_Non_Primary():
    def __init__(self, MRNs = []):
        self.patient_db = get_current("PatientDB")
        self.path_base = '\\\\mymdafiles\\di_data1\\Morfeus\\bmanderson\\Pacs_copy_3\\'
        self.no_primary_base = '\\\\mymdafiles\\di_data1\\Morfeus\\bmanderson\\Pacs_No_Primary\\'
        self.temp_color_list = []
        self.color_list = ['#800000','#9A6324','#ffe119','#e6194B','#f58321','#4363d8','#911eb4','#a9a9a9']
        self.redo = True
        for self.MRN in MRNs:
            try:
                self.run_on_pat()
                self.case.PatientModel.RegionsOfInterest['test_primary'].DeleteRoi()
                self.patient.Save()
            except:
                print('error')
                continue
    def run_on_pat(self):
        found_primary = True
        self.path = self.path_base + self.MRN + '\\'
        if os.path.exists(self.path + 'made_segments.txt') and not self.redo:
            return None
        try:
            self.ChangePatient_8B()
        except:
            return None
        for self.case in self.patient.Cases:
            xxx = 1
        # self.case.SetCurrent()
        '''
        This is to identify the primary images
        '''
        self.rois_in_case = []
        for roi in self.case.PatientModel.RegionsOfInterest:
            self.rois_in_case.append(roi.Name)
        Frame_Of_Reference_Exams = {}
        for exam in self.case.Examinations:
            if exam.EquipmentInfo.FrameOfReference not in Frame_Of_Reference_Exams.keys():
                Frame_Of_Reference_Exams[exam.EquipmentInfo.FrameOfReference] = [exam]
            else:
                Frame_Of_Reference_Exams[exam.EquipmentInfo.FrameOfReference].append(exam)
        FoR_Index = -1
        self.segment = 1
        for FoR in Frame_Of_Reference_Exams.keys():
            print(FoR)
            self.threshold_name = 'test_primary'
            primary_exams = []
            secondary_exams = []
            FoR_Index += 1
            Examinations = Frame_Of_Reference_Exams[FoR]
            self.threshold_name = 'test_primary'
            for self.exam in Examinations:
                self.Exam = self.exam.Name
                has_roi = False
                if self.threshold_name in self.rois_in_case and \
                        self.case.PatientModel.StructureSets[self.exam.Name].RoiGeometries[
                            self.threshold_name].HasContours():
                    has_roi = True
                if not has_roi:
                    self.make_threshold()
            volume_dict = {}
            for exam in Examinations:
                if self.case.PatientModel.StructureSets[exam.Name].RoiGeometries[
                            self.threshold_name].HasContours():
                    volume = self.case.PatientModel.StructureSets[exam.Name].RoiGeometries[self.threshold_name].GetRoiVolume()
                    volume_dict[exam.Name] = volume
                    if volume > 10000:
                        primary_exams.append(exam.Name)
                    else:
                        secondary_exams.append(exam.Name)
            '''
            This is to make a thresholded roi called 'Threshold_Liver_Segment on each of the non-primary images
            '''
            if not primary_exams:
                fid = open(self.no_primary_base + self.MRN, 'w+')
                fid.close()
                self.patient.Save()
                found_primary = False
            for self.Exam in secondary_exams:
                has_roi = False
                for roi in self.rois_in_case:
                    if roi.find('Threshold_Liver_Segment') == 0 and self.case.PatientModel.StructureSets[self.Exam].RoiGeometries[roi].HasContours():
                        self.threshold_name = roi
                        has_roi = True
                        break
                if not has_roi:
                    while 'Threshold_Liver_Segment' + str(self.segment) in self.rois_in_case:
                        self.segment += 1
                    self.threshold_name = 'Threshold_Liver_Segment' + str(self.segment)
                    self.make_threshold()
                    self.segment += 1
                if primary_exams:
                    self.case.PatientModel.CopyRoiGeometries(SourceExamination=self.case.Examinations[self.Exam],
                                                             TargetExaminationNames=primary_exams,
                                                             RoiNames=[self.threshold_name])

            if len(primary_exams) > 3:
                self.make_folder(primary_exams, 'Primary_Images' + str(FoR_Index))
            if len(secondary_exams) > 1:
                self.make_folder(secondary_exams,'Secondary_Images' + str(FoR_Index))
            '''
            If we have primary exams, map the secondary exam ROIs over onto it
            '''
            # if primary_exams:
            #     self.case.PatientModel.CopyRoiGeometries(SourceExamination=self.case.Examinations[self.Exam],
            #                                         TargetExaminationNames=primary_exams,
            #                                         RoiNames=self.threshold_names)
        self.patient.Save()
        if found_primary:
            if not os.path.exists(self.path):
                os.makedirs(self.path)
            fid = open(self.path + 'made_segments.txt', 'w+')
            fid.close()
    def make_folder(self, exams, name):
        for examination_group in self.case.ExaminationGroups:
            if examination_group.Name == name:
                for Item in examination_group.Items:
                    if Item.Examination.Name in exams:
                        del exams[exams.index(Item.Examination.Name)]
        if exams:
            self.case.CreateExaminationGroup(ExaminationGroupName=name,
                                             ExaminationGroupType='Collection4dct',
                                             ExaminationNames=exams)
    def make_threshold(self):
        if not self.temp_color_list:
            self.temp_color_list = copy.deepcopy(self.color_list)
        # color_int = np.random.randint(len(self.temp_color_list))-1
        color_int = 0

        if self.threshold_name not in self.rois_in_case:
            self.case.PatientModel.CreateRoi(Name=self.threshold_name, Color=self.temp_color_list[color_int], Type="Organ", TissueName="",
                                             RbeCellTypeName=None, RoiMaterial=None)
            self.rois_in_case.append(self.threshold_name)
            del self.temp_color_list[color_int]
        self.case.PatientModel.RegionsOfInterest[self.threshold_name].GrayLevelThreshold(Examination=self.case.Examinations[self.Exam],
                                                                                               LowThreshold=-1000,HighThreshold=9999,PetUnit="",CbctUnit=None,
                                                                                               BoundingBox=None)
    def ChangePatient_8B(self):
        info_all = self.patient_db.QueryPatientInfo(Filter={"PatientID": self.MRN})
        # If it isn't, see if it's in the secondary database
        if not info_all:
            info_all = self.patient_db.QueryPatientInfo(Filter={"PatientID": self.MRN}, UseIndexService=False)
        info = []
        for info_temp in info_all:
            if info_temp['PatientID'] == self.MRN:
                info = info_temp
                break
        self.patient = self.patient_db.LoadPatient(PatientInfo=info, AllowPatientUpgrade=False)
    def ChangePatient(self):
        info_all = self.patient_db.QueryPatientInfo(Filter={"PatientID": self.MRN}, UseIndexService=False)
        if not info_all:
            info_all = self.patient_db.QueryPatientInfo(Filter={"PatientID": self.MRN}, UseIndexService=True)
        info = []
        for info_temp in info_all:
            if info_temp['PatientID'] == self.MRN:
                info = info_temp
                break
        self.patient = self.patient_db.LoadPatient(PatientInfo=info, AllowPatientUpgrade=True)

if __name__ == '__main__':
    path = r'\\mymdafiles\di_data1\Morfeus\BMAnderson\Pacs_Brandy_Patients'
    MRNs = []
    for _, MRNs, _ in os.walk(path):
        break
    Make_Segments_Of_Non_Primary(MRNs)