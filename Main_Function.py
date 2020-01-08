__author__ = 'Brian M Anderson'
# Created on 1/8/2020
from Name_Folders_MRNs import Down_Folder, os
from Identify_Primary_Map_RTs_On import create_RT_On_Primary


path = r'K:\Morfeus\BMAnderson\Pacs_Brandy_Patients'
'''
First, rename folders to reflect the actual MRNs of the patient info within them
'''
Down_Folder(path)
# create_RT_On_Primary(path)
'''
Easier to just pull them into Raystation, but we have to trick Raystation to take them
Run 'Prep_Dicom_GUI.exe' and select pre-separated
'''
# Uploading patients to Raystation
'''
Now that they're uploaded, run Map_Segments_Onto_Primary in Raystation
This will create 'Threshold_Liver_Segments' onto the primary image
'''