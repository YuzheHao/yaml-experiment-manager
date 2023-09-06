# YEM (Yaml-Experiment-Manager)
运行的实验太多，hparams管理不过来？
想要运行旧的实验，但是还要手动找参数列表然后手动创建job？
每次新增一个param时，还需要手动在之前的job文件里添加新的参数？
过期的参数在job文件里堆积？删除还要手动一个一个找？

太麻烦了！！试试这个简单的用yaml管理各种实验的小工具吧！

## 添加yem到project
把yem包放到你的项目目录下：
```
YourProject
  ├ yem 🆕
  ├ ...
  ├ model.py
  └ main.py
```

## 参数注册
所有需要读取的参数应该在`yem/__init__.py`里注册
你可以在一些特定的opt前面增加注释，注意这会造成空一个新行的效果，所以最好只用它来对参数分组
```python
optNotes['optA'] = '# 这句注释会被添加在yaml文件中对应参数的前面'
parser.add_argument('--optA', type=str,
    default='Kobe',
    help='a test opt')
```

## 在main中调用yem的parser函数
把`yem.parse_opts()`写在你`main.py`的入口部分，它会返回一个`opt`对象，你可以通过`opt.param_A`来访问所有从yaml Config文件中写入的参数
```python
from yem import parse_opts

if __name__ == '__main__':
    opt = parse_opts()
    '''
    Write your code after here
    model = ResNet(opt.param_A, opt.param_B)
    '''
```

## 指定config运行试验
```sh
python main.py --config YourConfig.yaml
```
```
