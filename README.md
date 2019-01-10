# Upload client for the ISMARA web-service (www.ismara.unibas.ch)

This is a pyhton script which uploads your files to the ISMARA
web-server and starts the ISMARA analysis.

All you need to do is to download **ismara_uploader.py** script and start using it.

**Important!** This script requires Python3!

## Purpose

This script is aimed to users who has their data files stored on remote machines (usually linux) which can use this script to upload their data without use of an internet browser. So you do not need to copy files to your local machine for uploading to the ISMARA server.

This is just alpha version to see if there are people interested in such application, We hope to get user feedback to properly shape the further development.

Here is lit of features we plan for the uploader script:
* resumable upload
* metadata upload along with data files (sample names, multiple files per sample, predefined groups for averaging)

**All feedback is welcome!**

## Usage

```shell
python ismara_uploader.py [-h] [-a email_address][-e EMAIL] [-p PROJECT]
                          [-t {microarray,rnaseq,chipseq,cage}]
                          [-o {hg18,mm9,hg19,mm10}] [--mirna] --file-list
                          FILE_LIST
```

### Optional arguments:

* -h, --help :  show this help message and exit
* -e EMAIL |: email address
* -p PROJECT : project name
* -t : data type {microarray,rnaseq,chipseq,cage}, default: microarray
* -o : organism ID {hg18,mm9,hg19,mm10}, default: hg19
* --mirna : Run with miRNA
* --file-list : list of files, ascii text, one line per file path

#### File format support
The following file formats are supported:
* **microarray** : .cel files
* **rnaseq/chipseq** : .fastq[.gz], .bed[.gz], .bam
* *all* : .zip, .tar.gz archives containing files of above formats
 

### Example

Let's assume that you have three fastq files with human rnaseq data.
1. We create a text file which contains paths to your files ("file_ist.txt")
```
/path/Sample1.fastq.gz
/path/Sample2.fastq.gz
/path/Sample3.fastq.gz
```

2. We run the script in background:
```shell
python ismara_uploader.py -a user@example.com -p "my cool project" -t rnaseq -o hg19 \
    --mirna --file-list file_list.txt 1>ismara_uploader.out 2>ismara_uploader.err &
```

3. In the file ismara_uploader.out the last lines contain a link to status page of your submission. If you submitted your email address then you will get a notification once your job is finished.

Please not that right now there is a lot of messages about insecure connection in error log file. This is because of problem with self-signed server certificate which should resolved very soon.
