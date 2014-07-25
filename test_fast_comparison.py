

def test_SimpleDicomFileDistance():

    from fast_comparison import SimpleDicomFileDistance, DicomFilesClustering
    from os.path import abspath, dirname

    datadir = os.path.join(abspath(dirname(__file__)), 'dicoms')
    file1 = os.path.join(datadir, 'subj1_01.dcm')
    file2 = os.path.join(datadir, 'subj2_02.dcm')
    file3 = os.path.join(datadir, 'subj3_01.dcm')
    file4 = os.path.join(datadir, 'subj3_02.dcm')
    file5 = os.path.join(datadir, 'subj3_03.dcm')
    file6 = os.path.join(datadir, 'subj3_04.dcm')

    dist = SimpleDicomFileDistance()
    # Metemos todos los ficheros que tengamos en una 
    dcm_files = [file1, file2, file3, file4, file5, file6]

    groups = group_files(dcm_files)
    return groups

    #dcmclus = DicomFilesClustering(groups_leaders)
    #dcmclus._calculate_file_distances()
    #return dcmclus

if __name__ == '__main__':
    groups = test_DicomFileDistance()

