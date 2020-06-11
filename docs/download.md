You can use the `wget` or `curl` command-line tools to download files from the AWS data registry.  The URLs will have this form:

* `https://` (TBD)

So an example command would be:

```buildoutcfg
$ wget https://
$ unzip rn4.zip
$ ls rn4
```

Note that you can download Bowtie 2 index files altogether a `zip` file, or separately.  For example, if you only need the forward version of the genome index (e.g. you are doing only exact matching), then you can limit your download to just the first 4 files in the index:

```buildoutcfg
$ for i in 1 2 3 4 ; do wget https://...${i}.bt2 ; done
$ ls
``` 
