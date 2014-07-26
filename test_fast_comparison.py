def test_DicomFileDistance():

    from fast_comparison import DicomFileDistance, DicomFilesClustering, group_files
    from os.path import abspath, dirname, join

    datadir = join(abspath(dirname(__file__)), 'dicoms')
    file1 = join(datadir, 'subj1_01.dcm')
    file2 = join(datadir, 'subj2_02.dcm')
    file3 = join(datadir, 'subj3_01.dcm')
    file4 = join(datadir, 'subj3_02.dcm')
    file5 = join(datadir, 'subj3_03.dcm')
    file6 = join(datadir, 'subj3_04.dcm')

    dist = DicomFileDistance()
    # Metemos todos los ficheros que tengamos en una 
    dcm_files = [file1, file2, file3, file4, file5, file6]
    for i in range(5):
        dcm_files.extend(dcm_files)
    #print len(dcm_files)
    
    
    groups = group_files(dcm_files)
    return groups

def test_SimpleDicomFileDistance():

    from fast_comparison import SimpleDicomFileDistance, DicomFilesClustering, group_files
    from os.path import abspath, dirname, join

    datadir = join(abspath(dirname(__file__)), 'dicoms')
    file1 = join(datadir, 'subj1_01.dcm')
    file2 = join(datadir, 'subj2_02.dcm')
    file3 = join(datadir, 'subj3_01.dcm')
    file4 = join(datadir, 'subj3_02.dcm')
    file5 = join(datadir, 'subj3_03.dcm')
    file6 = join(datadir, 'subj3_04.dcm')

    dist = SimpleDicomFileDistance()
    # Metemos todos los ficheros que tengamos en una 
    dcm_files = [file1, file2, file3, file4, file5, file6]
    for i in range(5):
        dcm_files.extend(dcm_files)
    #print len(dcm_files)

    groups = group_files(dcm_files)
    return groups

if __name__ == '__main__':
    groups = test_SimpleDicomFileDistance()
    #groups = test_DicomFileDistance()
