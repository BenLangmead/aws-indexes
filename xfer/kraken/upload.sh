#!/bin/bash

DATE="$1"

[[ -z "${DATE}" ]] && echo "Must give YYYYMMDD date as argument" && exit 1

# AWS profile used for the S3 writes. Default is the role-chained "index-zone-s3"
# profile, which works for anyone in the IndexZoneS3Assumers group (langmead,
# rcharles) once their base profile is authenticated (see UPLOADING_K2_INDEXES.md).
# Override with e.g. AWS_UPLOAD_PROFILE=data-langmead ./upload.sh YYYYMMDD
PROFILE="${AWS_UPLOAD_PROFILE:-index-zone-s3}"

# Note: "microbial" not in this list
for c in viral minusb \
    pluspf pluspf08gb pluspf16gb \
    pluspfp pluspfp08gb pluspfp16gb \
    standard standard08gb standard16gb
do
    NAME="${c}_${DATE}"
    AR_NAME="k2_${NAME}.tar.gz"
    # Local build dirs use e.g. "standard08gb"; the published S3 keys use
    # "standard_08_GB" (this naming switched at the July 2025 release). Map the
    # local name to the S3 name here so archives, directories, and the per-db
    # .md5 all land under the correct key.
    cc=$(echo "${c}" | sed 's/08gb/_08_GB/' | sed 's/16gb/_16_GB/')
    echo "Name: ${c}, corrected: ${cc}"
    [[ ! -f "${c}/${AR_NAME}" ]] && echo "Could not find ${c}/${AR_NAME}" && exit 1
    cmd="aws s3 --profile ${PROFILE} cp \"${c}/${AR_NAME}\" \"s3://genome-idx/kraken/k2_${cc}_${DATE}.tar.gz"
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
        # The per-db md5 is named after the local dir (e.g. "standard08gb.md5");
        # rename it to the S3 name (e.g. "standard_08_GB.md5") on the way up so it
        # matches the website's link. All other files keep their fixed names.
        dest_fn="${fn}"
        [[ "${fn}" == "${c}.md5" ]] && dest_fn="${cc}.md5"
        cmd2="aws s3 --profile ${PROFILE} cp \"${c}/${fn}\" \"s3://genome-idx/kraken/${cc}_${DATE}/${dest_fn}\""
        echo "${cmd2}"
        ${cmd2}
    done
done
