# YEM (Yaml-Experiment-Manager)
A program to manage your experiments with yaml config file.  
* auto add the new registered parameters on the history yaml job.
* auto remove the deleted parameters in the yaml config.
* add comments on the yaml config file.

运行的实验太多，hparams管理不过来？  
想要运行旧的实验，但是还要手动找参数列表然后手动创建job？  
每次新增一个param时，还需要手动在之前的job文件里添加新的参数？  
过期的参数在job文件里堆积？删除还要手动一个一个找？  

太麻烦了！！试试这个简单的用yaml管理各种实验的小工具吧！

## Add yem to project
把yem包放到你的项目目录下：  
Put the `yem` directory to the root of your project.  
```
YourProject
  ├ yem 🆕
  ├ ...
  ├ model.py
  └ main.py
```

## Register your parameters
所有需要读取的参数应该在`yem/__init__.py`里注册  
你可以在一些特定的opt前面增加注释，注意这会造成空一个新行的效果，所以最好只用它来对参数分组  
All the parameters you want to read should be registered in `yem/__init__.py`.  
You can add comments before some specific opt, but this will cause a new line, so it's better to use it to group parameters.  
```python
optNotes['optA'] = '# 这句注释会被添加在yaml文件中对应参数的前面, This comment will be added before the opt in the yaml file'
parser.add_argument('--optA', type=str,
    default='Kobe',
    help='a test opt')
```

## Use yem's parser in your `main`
把`yem.parse_opts()`写在你`main.py`的入口部分，它会返回一个`opt`对象，你可以通过`opt.param_A`来访问所有从yaml Config文件中写入的参数  
Put `yem.parse_opts()` in the entry of your `main.py`, it will return an `opt` object, you can access all the parameters written in the yaml config file through `opt.param_A`.  
```python
from yem import parse_opts

if __name__ == '__main__':
    opt = parse_opts()
    '''
    Write your code after here
    model = ResNet(opt.param_A, opt.param_B)
    '''
```

## Run experiment with specified config
```sh
python main.py --config YourConfig.yaml
```
本次运行的的job的config会被额外保存在`results_path`下，并带有一个运行信息相关的title  
The config of this job will be saved in `results_path` with a title related to the running information.  
```
# 2023-12-25 10:57:15 @ mostima | GPU:0
# Git version: [1d27246] 🐛 fix config comments
```

