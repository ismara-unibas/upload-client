""" Uploads files to ISMARA webserver """

import argparse
import logging
import os
import requests
import sys

UPLOAD_URL = "https://ismara.unibas.ch/mara/upload"
RUN_URL = "https://ismara.unibas.ch/mara/run"

def main():
    parser = argparse.ArgumentParser(
        description='Uploads files to ISMARA webserver')
    parser.add_argument('-e',
                        help='email address',
                        dest='email',
                        default='')
    parser.add_argument('-p',
                        help='project name',
                        dest='project',
                        default='')
    parser.add_argument('-t',
                        help='data type',
                        dest="data_type",
                        choices=['microarray', 'rnaseq', 'chipseq', 'cage'],
                        default='microarray')
    parser.add_argument('-o',
                        help='Organism id',
                        dest='organism',
                        choices=['hg18', 'mm9', 'hg19', 'mm10'],
                        default='hg19')

    parser.add_argument('--mirna',
                        help='Run with miRNA',
                        dest='use_mirna',
                        action='store_true',
                        default=False)
    parser.add_argument('--file-list',
                        help="list of files, ascii text, one line per file path",
                        dest="file_list",
                        required=True)
    
    args = parser.parse_args()

    upload_session = requests.Session()
    upload_session.verify = False
    upload_session.timeout = (10, 600)
    save_dir = get_sd(upload_session)
    with open(args.file_list) as fin:
        files = [line.strip() for line in fin]
    for f in files:
        with open(f, 'rb') as fin:
            index=0
            headers={}
            content_size = os.path.getsize(f)
            file_name = os.path.basename(f)
            for chunk in read_in_chunks(fin):
                offset = index + len(chunk)
                headers['Content-Type'] = 'application/octet-stream'
                headers['Content-length'] = str(content_size)
                headers['Content-Range'] = 'bytes %s-%s/%s' % (index, offset, content_size)
                index = offset
                try:
                    r =  upload_session.post(UPLOAD_URL, files={"files[]":(file_name, chunk)}, data={"sd": save_dir})
                except requests.exceptions.Timeout:
                    print("Connection timeout! Could not establish connection in a reasobable time.")
                except:
                    print (sys.exc_info()[0])
                    return

    # init job run after upload
    email = args.email
    project = args.project
    data_type = args.data_type
    organism = args.organism
    if organism in ["hg19", 'mm10']:
        organism += "_f5"
    use_mirna = str(args.use_mirna).lower()
    r = upload_session.post(RUN_URL, data={"sd": save_dir,
                                           "email": email,
                                           "project": project,
                                           "type": data_type,
                                           "organism": organism,
                                           "mirna": use_mirna})
    print("\n>>>>>>>>>>\nHere is link to your results:\n    https:///ismara.unibas.ch%s" % (r.text.strip()))

def get_sd(mysession):
    """ get name of working directory for a project """
    url = "https://ismara.unibas.ch/mara/get_sd"
    res = mysession.get(url)
    res = [x for x in res.iter_lines()][0].decode("utf-8")
    return(res)


def read_in_chunks(file_object, chunk_size=50000000):
    """ Read file in chuncks """
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


if __name__ == "__main__":
    main()
