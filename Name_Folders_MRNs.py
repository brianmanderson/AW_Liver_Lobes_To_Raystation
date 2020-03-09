import pydicom
import os
from threading import Thread
from multiprocessing import cpu_count
from queue import *


def moveTree(sourceRoot, destRoot):
    if not os.path.exists(destRoot):
        return False
    ok = True
    for path, dirs, files in os.walk(sourceRoot):
        relPath = os.path.relpath(path, sourceRoot)
        destPath = os.path.join(destRoot, relPath)
        if not os.path.exists(destPath):
            os.makedirs(destPath)
        for file in files:
            destFile = os.path.join(destPath, file)
            if os.path.isfile(destFile):
                os.remove(destFile)
                print("Deleting existing file: " + destFile)
                ok = False
            srcFile = os.path.join(path, file)
            os.rename(srcFile, destFile)
    for path, dirs, files in os.walk(sourceRoot, False):
        if len(files) == 0 and len(dirs) == 0:
            os.rmdir(path)
    return ok


def run_main(A):
    input_path, header_folder = A
    print(header_folder)
    MRN_val = []
    if os.path.exists(os.path.join(input_path,header_folder,'MRN.txt')):
        fid = open(os.path.join(input_path,header_folder,'MRN.txt'))
        MRN_val = fid.readline()
        fid.close()
    else:
        go_on = False
        for folder in os.listdir(os.path.join(input_path,header_folder)):
            if go_on:
                break
            for file in os.listdir(os.path.join(input_path, header_folder, folder)):
                if file.find('.dcm') != -1:
                    ds = pydicom.read_file(os.path.join(input_path, header_folder, folder, file))
                    MRN_val = str(ds.PatientID)
                    fid = open(os.path.join(input_path, header_folder, 'MRN.txt'), 'w+')
                    fid.write(MRN_val)
                    fid.close()
                    go_on = True
                    break
    if MRN_val:
        if os.path.join(input_path,header_folder) != os.path.join(input_path,MRN_val) and os.path.exists(os.path.join(input_path,MRN_val)):
            moveTree(os.path.join(input_path,header_folder), os.path.join(input_path,MRN_val))
        elif os.path.join(input_path,header_folder) != os.path.join(input_path,MRN_val):
            os.rename(os.path.join(input_path,header_folder), os.path.join(input_path,MRN_val))
    if os.path.exists(os.path.join(input_path,header_folder)) and len(os.listdir(os.path.join(input_path,header_folder))) == 0:
        os.removedirs(os.path.join(input_path,header_folder))
    print('Finished')
    return None


def worker_def(q):
    objective = run_main
    while True:
        item = q.get()
        if item is None:
            break
        else:
            objective(item)
            q.task_done()


class Down_Folder(object):
    def __init__(self,input_path):
        thread_count = int(cpu_count() * .75 - 1)
        print('Running on {} threads'.format(thread_count))
        q = Queue(maxsize=thread_count)
        threads = []
        for worker in range(thread_count):
            t = Thread(target=worker_def, args=(q,))
            t.start()
            threads.append(t)
        self.input_path = input_path
        header_folders = []
        for _, header_folders, files in os.walk(input_path):
            break
        for header_folder in header_folders:
            q.put([input_path,header_folder])
        for i in range(thread_count):
            q.put(None)


def delete_empty_folder(sourceRoot):
    for path, dirs, files in os.walk(sourceRoot, False):
        for dir_val in dirs:
            delete_empty_folder(os.path.join(path,dir_val))
    for path, dirs, files in os.walk(sourceRoot, False):
        if len(files) == 0 and len(dirs) == 0:
            os.rmdir(path)


class Down_Folder_new(object):
    def __init__(self,input_path):
        self.input_path = input_path
        header_folders = []
        files = []
        for root, header_folders, files in os.walk(input_path):
            break
        for header_folder in header_folders:
            if len(header_folder) > 10:
                delete_empty_folder(os.path.join(root,header_folder))


if __name__ == '__main__':
    pass
