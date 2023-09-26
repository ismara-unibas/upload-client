""" Uploads files to ISMARA webserver """

import argparse
import json
import logging
import os
import re
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
                        help='Organism id: human, mouse, rat, zebrafish, yeast, ecoli, arabidopsis or genome versions: hg18, hg19 or hg38 for human, mm9, mm10, mm39 for mouse, rn6 for rat, e_coli for E.coli, sacSer2 for yeast, arTal for Arabidopsis thaliana, dr11 for zebrafish.',
                        dest='organism',
                        choices=["human", "mouse", "rat", "zebrafish", "yeast", "ecoli", "arabidopsis", 'hg18', 'mm9', 'hg19', 'mm10', "rn6", "e_coli", "arTal", "sacSer2", "dr11", "hg38", "mm39"],
                        default='hg38')

    parser.add_argument('--mirna',
                        help='Run with miRNA',
                        dest='use_mirna',
                        action='store_true',
                        default=False)
    
    parser.add_argument('--file-list',
                        help="list of files, ascii text, one line per file path. Supported file formats: .CEL, .FASTQ, .BAM, .BED, .SAM.",
                        dest="file_list",
                        required=True)
    
    args = parser.parse_args()

    # check if files exists
    file_sizes = {}
    with open(args.file_list) as fin:
        files = [line.strip() for line in fin]
    for myfile in files:
        if re.match(r'^SRR\d+$', myfile) or re.match(r'^SRR\d+\s+\S+', myfile):
            continue
        if re.match(r'^(http://|https://|ftp://)', myfile):
            continue
        if not os.path.exists(myfile):
            raise BaseException("File %s does not exist." % myfile)
        file_sizes[myfile] = "%.4f GB"  % (os.path.getsize(myfile)/1024./1024./1024.)
    logging.warning("File list check complete.")
        
    # init session
    upload_session = requests.Session()
    upload_session.verify = True
    upload_session.timeout = (10, 600)
    save_dir = get_sd(upload_session)

    # save user parameters
    organism_map = {"human": "hg38",
                    "mouse": "mm39",
                    "rat": "rn6",
                    "zebrafish": "dr11",
                    "yeast": "sacSer2",
                    "ecoli": "e_coli",
                    "arabidopsis": "arTal"}
    if args.organism in organism_map:
        organism = organism_map[args.organism]
    else:
        organism = args.organism

    job_data = {"email": args.email,
                "project": args.project,
                "type": args.data_type,
                "organism": organism,
                "mirna":  str(args.use_mirna).lower(),
                "files": file_sizes,
                "submission": "uploader"}
    if job_data["organism"] in ["hg19", 'mm10', "hg38", "mm39"]:
        job_data["organism"] += "_f5"

    # save job parameters in advance
    try:
        r =  upload_session.post("https://ismara.unibas.ch/mara/save_json",
                                 data={"sd": save_dir,
                                       "data":json.dumps(job_data)})
    except:
        logging.warning("Error: Could not save user parameters!\n%s!", str(sys.exc_info()))
    
    srr_list = []
    url_list = []
    upload_counter = 1
    for f in files:
        if re.match(r'^SRR\d+$', f) or re.match(r'^SRR\d+\s+\S+', f):
            srr_list.append(f)
            continue
        if re.match(r'^(http://|https://|ftp://)', f):
            url_list.append(f)
            continue
        logging.warning("Uploading %s (%d/%d)." % (f, upload_counter, len(files)))
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
                for i in range(20):
                    try:
                        r =  upload_session.post(UPLOAD_URL, files={"files[]":(file_name, chunk)},
                                                 data={"sd": save_dir})
                        error = ''
                        break
                    except:
                        error = sys.exc_info()[0]
                        logging.warning("Connection problem: %s!!!\nRetrying to re-upload data. Retry %d", str(sys.exc_info()), i+1)
                        time.sleep(i * 60)
                if error != '':
                    logging.warning("Could not upload the data! Please report this id to ISMARA administrators: %s!", save_dir)
        logging.warning("Finished uploading %s (%d/%d)." % (f, upload_counter, len(files)))
        upload_counter += 1


    # init job run after upload
    email = args.email
    project = args.project
    data_type = args.data_type
    use_mirna = str(args.use_mirna).lower()
    r = upload_session.post(RUN_URL, data={"sd": save_dir,
                                           "email": email,
                                           "project": project,
                                           "type": data_type,
                                           "method": "ismara_uploader",
                                           "organism": job_data["organism"],
                                           "url_list": "\n".join(url_list),
                                           "srr_list": "\n".join(srr_list),
                                           "mirna": use_mirna})
    print("\n>>>>>>>>>>\nHere is link to your submission:\n    https:///ismara.unibas.ch%s" % (r.text.strip()))


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
