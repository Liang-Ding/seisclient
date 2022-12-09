# SEISClient

![SeisClient Logo](doc/images/seisclient_logo.svg)
SeisClient is a python package to request accurate 3D Greens' function and synthetic waveform from [SeisCloud](https://seis.cloud). 

For basic install:
```shell
git clone https://github.com/Liang-Ding/seisclient.git
cd seisclient
pip install -e .
```
or using pip 
```shell
pip install seisclient
```

## Usage
* Request Greens' function and synthetic waveform: [examples](./examples/request_Greens-function_synthetic-waveform.ipynb)
* Request synthetic waveform from multiple-point source and finite fault: [examples](./examples/request_syn_finite_fault.py)
* The parameters and values in examples are arbitrarily selected as demos only.  
