# Upload client for the ISMARA web-service (www.ismara.unibas.ch)

This is a python script which uploads your files to the ISMARA
web-server and starts the ISMARA analysis.

All you need to do is to download **ismara_uploader.py** script and start using it.

**Important!** This script requires Python3 as well as the *requests* library. If these packages are not available then you can use <a href="https://conda.io">conda</a> to install it.

## Purpose

This script is aimed to users who has their data files stored on remote machines (usually linux) which can use this script to upload their data without use of an internet browser. So you do not need to copy files to your local machine for uploading to the ISMARA server.

We hope to get user feedback to properly shape the further development.

**All feedback is welcome!**

## Usage

```shell
python ismara_uploader.py [-h] [-e EMAIL] [-p PROJECT]
                          [-t {microarray,rnaseq,chipseq}]
                          [-o {human,mouse,rat,zebrafish,yeast,ecoli,arabidopsis,hg18,mm9,hg19,mm10,hg38,mm39,rn6,e_coli,sacSer2,arTal,dr11}] [--mirna] --file-list
                          FILE_LIST
```

### Optional arguments:

* -h, --help :  show this help message and exit
* -e EMAIL |: email address
* -p PROJECT : project name
* -t : data type {microarray,rnaseq,chipseq}, default: rnaseq
* -o : organism id or genome version  {human,mouse,rat,zebrafish,yeast,ecoli,arabidopsis,hg18,mm9,hg19,mm10,rn6,e_coli,sacSer2,arTal,dr11}, default: hg38
* --mirna : Run with miRNA
* --file-list : list of files/links/SRR, ascii text, one line per file path. Supported file formats: .CEL, .FASTQ, .BAM, .BED, .SAM.

### Format of file list
This file contains path to files to upload. One file path per line. You can add also links to external files (http or ftp) or SRR ids (SRA database). In case of SRR id you can add comprehensive name for a sample which should be separated by a space from the SRR id.

Important! For paired-end reads please use suffixes **_R1/_R2** to indicate fastq files with first end reads and second end reads correspondingly.

#### Examples

* File paths
```
/data/expr1/sample1_R1.fastq.gz
/data/expr1/sample1_R2.fastq.gz
/data/expr1/sample2_R1.fastq.gz
/data/expr1/sample2_R2.fastq.gz

```

* Links
```
https://example.com/data/sample1_R1.fastq.gz
https://example.com/data/sample1_R2.fastq.gz
https://example.com/data/sample2_R1.fastq.gz
https://example.com/data/sample2_R2.fastq.gz
```

* SRR ids
```
SRR12345
SRR12346
SRR12347
SRR12348
```

* SRR ids with names
```
SRR12345 3hours_rep1
SRR12346 3hours_rep2
SRR12347 3hours_rep3
SRR12348 6hours_rep1
```

#### ISMARA file format support
The following file formats are supported:
* **microarray** : .cel files
* **rnaseq/chipseq** : .fastq[.gz], .bed[.gz], .bam
* *all* : .zip, .tar.gz archives containing files of the above formats
 

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
nohup python ismara_uploader.py -e user@example.com -p "my cool project" -t rnaseq -o hg19 \
    --mirna --file-list file_list.txt &>ismara_uploader.out &
```

3. When upload is finished, the last lines of the file `ismara_uploader.out` a link to status page of your submission. If you submitted your email address then you will get a notification once your job is finished.

In linux/MacOS systems you can check last messages in `ismara_uploader.out` with command:
```shell
tail ismara_uploader.out
```

