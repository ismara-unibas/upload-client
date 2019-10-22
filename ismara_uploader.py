""" Uploads files to ISMARA webserver """

import argparse
import json
import logging
import os
import requests
import time
import sys

UPLOAD_URL = "https://ismara.unibas.ch/mara/upload"
RUN_URL = "https://ismara.unibas.ch/mara/run"

def main():
    parser = argparse.ArgumentParser(
        description='Uploads files to ISMARA webserver. Please take in account that fastq support is not implemented for hg18 and mm9 genome versions.')
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
                        choices=['microarray', 'rnaseq', 'chipseq'],
                        default='rnaseq')
    parser.add_argument('-o',
                        help='Organism id: hg18 or hg19 for human, mm9 or mm10 for mouse, rn6 for rat, e_coli for E.coli..',
                        dest='organism',
                        choices=['hg18', 'mm9', 'hg19', 'mm10', "rn6", "e_coli"],
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
    upload_session.verify = True
    upload_session.timeout = (10, 600)
    save_dir = get_sd(upload_session)

    # save user parameters
    job_data = {"email": args.email,
                "project": args.project,
                "type": args.data_type,
                "organism": args.organism,
                "mirna":  str(args.use_mirna).lower(),
                "submission": "uploader"}
    if job_data["organism"] in ["hg19", 'mm10']:
        job_data["organism"] += "_f5"

    # save job parameters in advance
    try:
        r =  upload_session.post("https://ismara.unibas.ch/mara/save_json",
                                 data={"sd": save_dir,
                                       "data":json.dumps(job_data)})
    except:
        logging.warning("Error: Could not save user parameters!\n%s!", str(sys.exc_info()))

    
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
                error = ''
                for i in range(5):
                    try:
                        r =  upload_session.post(UPLOAD_URL, files={"files[]":(file_name, chunk)},
                                                 data={"sd": save_dir})
                        error = ''
                        break
                    except:
                        error = sys.exc_info()[0]
                        logging.warning("Error: %s!!!\nRetrying to re-upload data. Retry %d", str(sys.exc_info()), i+1)
                        time.sleep(60)
                if error != '':
                    logging.warning("Could not upload the data! Please report this id to ISMARA administrators: %s!", save_dir)



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
                                           "method": "ismara_uploader",
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
