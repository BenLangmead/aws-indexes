#!/bin/bash

DATE="$1"

[[ -z "${DATE}" ]] && echo "Must give YYYYMMDD date as argument" && exit 1

# Note: "microbial" not in this list
for c in viral minusb \
    pluspf pluspf08gb pluspf16gb \
    pluspfp pluspfp08gb pluspfp16gb \
    standard standard08gb standard16gb
do
    NAME="${c}_${DATE}"
    AR_NAME="k2_${NAME}.tar.gz"
    cc=$(echo "${c}" | sed 's/08gb/_08gb/' | sed 's/16gb/_16gb/')
    echo "Name: ${c}, corrected: ${cc}"
    [[ ! -f "${c}/${AR_NAME}" ]] && echo "Could not find ${c}/${AR_NAME}" && exit 1
    cmd="aws s3 --profile data-langmead cp \"${c}/${AR_NAME}\" \"s3://genome-idx/kraken/k2_${cc}_${DATE}.tar.gz"
    echo "${cmd}"
    ${cmd}
    for fn in database100mers.kmer_distrib \
        database150mers.kmer_distrib \
        database200mers.kmer_distrib \
        database250mers.kmer_distrib \
        database300mers.kmer_distrib \
        database50mers.kmer_distrib \
        database75mers.kmer_distrib \
        "${c}.md5" \
        hash.k2d \
        inspect.txt \
        ktaxonomy.tsv \
        opts.k2d \
        library_report.tsv \
        seqid2taxid.map \
        names.dmp \
        nodes.dmp \
        taxo.k2d
    do
        [[ ! -f "${c}/${fn}" ]] && echo "Could not find ${c}/${fn}" && exit 1
        cmd2="aws s3 --profile data-langmead cp \"${c}/${fn}\" \"s3://genome-idx/kraken/${cc}_${DATE}/${fn}\""
        echo "${cmd2}"
        ${cmd2}
    done
done
