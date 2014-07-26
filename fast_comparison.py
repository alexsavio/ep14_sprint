
import os
import logging
import numpy as np
from copy import copy

from more_collections import DefaultOrderedDict
from config import DICOM_FIELD_WEIGHTS

from utils import DicomFile
from sets import DicomsGenericSet

log = logging.getLogger(__name__)

class DistanceMeasure(object):
    #TODO
    #will be declared in ..classification.distance
    #currently from another branch
    pass

class DicomFileDistance(DistanceMeasure):

    import Levenshtein

    field_weights = DICOM_FIELD_WEIGHTS
    similarity_measure = Levenshtein.ratio
    inv_sum_weights = 1/sum(field_weights.values())

    def __init__(self):
        self.dcmf1 = None
        self.dcmf2 = None

    def fit(self, dcm_file1, dcm_file2):
        """

        :param dcm_file1: str (path to file) or DicomFile or namedtuple

        :param dcm_file2: str (path to file) or DicomFile or namedtuple
        """
        self.set_dicom_file1(dcm_file1)
        self.set_dicom_file2(dcm_file2)

    def set_dicom_file1(self, dcm_file):
        """
        :param dcm_file: str (path to file) or DicomFile or namedtuple
        """
        self.dcmf1 = self._read_dcmfile(dcm_file)

    def set_dicom_file2(self, dcm_file):
        """
        :param dcm_file: str (path to file) or DicomFile or namedtuple
        """
        self.dcmf2 = self._read_dcmfile(dcm_file)

    def _read_dcmfile(self, dcm_file):
        """

        :param dcm_file:
        :return:
        """
        if isinstance(dcm_file, str):
            return DicomFile(dcm_file)
        else:
            return dcm_file

    def fit_transform(self, file_path1, file_path2):
        self.fit(file_path1, file_path2)
        return self.transform()

    def transform(self):

        if self.dcmf1 is None or self.dcmf2 is None:
            return np.inf

        if len(self.field_weights) == 0:
            log.exception('Field weights are not set.')

        try:
            dist = 0
            for field_name in self.field_weights:
                str1 = str(getattr(self.dcmf1, field_name))
                str2 = str(getattr(self.dcmf2, field_name))

                if not str1 or not str2:
                    continue

                weight = self.field_weights[field_name]
                simil = self.similarity_measure(str1, str2)

                if simil > 0:
                    dist += (1/simil) * weight

            return dist/len(self.field_weights) * self.inv_sum_weights

        except Exception as exc:
            log.exception('Error calculating DICOM file distance.')


class SimpleDicomFileDistance(DicomFileDistance):

    field_weights = DICOM_FIELD_WEIGHTS

    def transform(self):
        """
        Checks the field values in self.dcmf1 and self.dcmf2 and returns True
        if all the field values are the same, False otherwise.

        :return: bool
        """
        if self.dcmf1 is None or self.dcmf2 is None:
            return np.inf

        try:
            for field_name in self.field_weights:
                if (str(getattr(self.dcmf1, field_name, '')) != str(getattr(self.dcmf2, field_name, ''))):
                    return False
                
            return True

        except Exception as exc:
            log.exception('Error calculating DICOM file distance.')
            

def group_files_alex(file_list):
    """
    Gets a list of DICOM file absolute paths and returns a list of lists of DICOM 
    file paths. Each group contains a set of DICOM files that have
    exactly the same headers.

    :param file_list: list of file paths
    
    """
    dist = SimpleDicomFileDistance()

    list_of_lists = []
    while len(file_list)>0:
        file_path1 = []
        file_path1.append(file_list.pop())

        dist.set_dicom_file1(file_path1[0])
        aux_list = copy(file_path1)
        j = len(file_list)-1

        while j>0:
            file_path2 = file_list[j]
            dist.set_dicom_file2(file_path2)

            if dist.transform():
                aux_list.append(file_path2)
                #file_list.remove(file_path2)
                file_list.pop(j)
                
            j-=1
            
        list_of_lists.append(aux_list)
        
#    groups_leaders = []
#    for i in range(len(list_of_lists)):
#        groups_leaders.append(list_of_lists[i][0])
    
    return list_of_lists


def group_files_borja(dcm_files):
    """
    Gets a list of DICOM file absolute paths and returns a list of lists of DICOM
    file paths. Each group contains a set of DICOM files that have
    exactly the same headers.

    :param file_list: list of file paths
    """

    dist = SimpleDicomFileDistance()

    remainers = copy(dcm_files)

    dcm_groups = DefaultOrderedDict(set)
    while len(remainers) > 0:
        dcmf1 = remainers.pop()
        dcm_groups[dcmf1].add(dcmf1)

        j = len(dcm_files)-1
        dist.set_dicom_file1(dcmf1)
        while j > 0:
            dcmf2 = dcm_files[j]
            dist.set_dicom_file2(dcmf2)

            if dist.transform():
                dcm_groups[dcmf1].add(dcmf2)
                dcm_files.pop(j)
            j -= 1

    return dcm_groups

class DicomFilesClustering(object):
    """A self-organizing set of DICOM files.
    It uses macuto.dicom.comparison.DicomDistanceMeasure to compare
    all DICOM files within a set of folders and create clusters of DICOM files
    that are similar.

    This has been created to automatically generate sets of files for different
    subjects.

    Set the fields/weights in DICOM_FIELD_WEIGHTS to adjust this.
    """

    def __init__(self, file_list, header_fields=None):
        """

        :param folders: str or list of str
        Paths to folders containing DICOM files.
        If None, won't look for files anywhere.

        :param store_metadata: bool
        If True, will either make a list of DicomFiles, or
        a simple DICOM header (namedtuples) with the fields specified
        in header_fields.

        :param header_fields: set of strings
        Set of header fields to be stored for each DICOM file.
        If store_metadata is False, this won't be used.

        """
        self._file_dists = None
        self._dicoms = file_list

    def _update(self):
        self._calculate_file_distances()
        #self._update_subjs_dict()
        #self._reorder_file_list()

    def _calculate_file_distances(self):
        """
        """
        n_files = len(self._dicoms)
        log.info('Calculating distance between {0} DICOM '
                 'files.'.format(n_files))

        dist_dtype = np.float16

        dist_method = DicomFileDistance()

        try:
            self._file_dists = np.zeros((n_files, n_files), dtype=dist_dtype)
        except MemoryError as mee:
            import scipy.sparse
            self._file_dists = scipy.sparse.lil_matrix((n_files, n_files),
                                                       dtype=dist_dtype)

        for idxi in range(n_files):
            dist_method.set_dicom_file1(self._dicoms[idxi])

            for idxj in range(idxi+1, n_files):
                dist_method.set_dicom_file2(self._dicoms[idxj])

                if idxi != idxj:
                    self._file_dists[idxi, idxj] = dist_method.transform()

    @staticmethod
    def plot_file_distances(dist_matrix):
        if dist_matrix is None:
            log.error('File distances have not been calculated.')

        import matplotlib.pyplot as plt
        fig = plt.figure()
        ax = fig.add_subplot(111)

        ax.matshow(dist_matrix, interpolation='nearest',
                   cmap=plt.cm.get_cmap('PuBu'))

        #all_patients = np.unique([header.PatientName for header in self._dicoms])
        #ax.set_yticks(list(range(len(all_patients))))
        #ax.set_yticklabels(all_patients)

    def from_dicom_set(self, dicom_set):
        self._dicoms = dicom_set

    def _update_subjs_dict(self):
        raise NotImplementedError
        #TODO

    def _reorder_file_list(self):
        raise NotImplementedError
        #TODO
        #mylist=['a','b','c','d','e']
        #myorder=[3,2,0,1,4]
        #mylist = [ mylist[i] for i in myorder]
        #print mylist

