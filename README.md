# ashes-and-dust-cli

## CLI structure

aad - ashes and dust

### download
download all the the data for a given time range.
the data should be downlaoded to a new directory
#### syntax
```aad --download -d1 <first date> -d2 <last date>```

#### nice to have
add support for download of sepecific data

### preprocess
preprocess the data - fix coordinate system, clip data to shape
#### syntax
```aad --preprocess -d <dir of data>```

#### nice to have
add support for preprocessing of sepecific data

### create a model
generate the model 
#### syntax
```aad --generate -d <dir of processed data>```

### help
#### syntax
```aad --help```
