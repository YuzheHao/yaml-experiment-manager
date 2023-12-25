'''
09/03/2023, Yuzhe Hao
一些和参数解析有关的操作，主要是对ymal文件进行管理
还有建立opt和ymal config之间的相互检查
'''

import os, sys, yaml
import datetime, socket

Tag = {
    'ok': f"\033[32m｜>>>｜\033[0m", # green
    'x':  f"\033[31m｜×××｜\033[0m", # red
    't':  f"\033[36m｜---｜\033[0m", # cyan
}

def job_stamp():
    git_info = os.popen("git log -1 --pretty=format:'[%h] %s'").read().strip()
    job_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    hostname = socket.gethostname()
    cuda_visible_devices = os.environ.get('CUDA_VISIBLE_DEVICES')

    job_stamp = f'# {job_date} @ {hostname} | GPU:{cuda_visible_devices}\n# Git version: {git_info}\n'
    return job_stamp

def yaml_float_parsing(opt, yaml_dict):
    '''
    用于解析yaml中的float参数，因为yaml中的float可能会被读取成字符串

    这里检测的时候使用的是opt.py里的默认值，因为这个是不会变的
    然后需要处理的是读取的yaml文件中的值，因为ymal中的一些科学计数法可能会被读取成字符串
    '''
    for key, value in yaml_dict.items():
        if key in opt.__dict__:
            if isinstance(opt.__dict__[key], float):
                value = 0 if not value else value
                yaml_dict[key] = float(value)
            elif isinstance(opt.__dict__[key], list) and isinstance(opt.__dict__[key][0], float):
                yaml_dict[key] = [float(item) for item in value]
        elif isinstance(value, dict):
            # 如果值是字典，递归调用yaml_float_parsing
            yaml_dict[key] = yaml_float_parsing(opt, value)

    return yaml_dict

def auto_update_config(opt, new_job_saving=False):
    '''
    根据opt.py中注册的参数，检查config和default_config中的参数
    是否有缺少，如果有缺少则自动用定义中的defaul填充

    这个函数只涉及到yaml config文件的生成，不会对opt这个变量产生
    任何的操作，所以对本次实验的运行不会产生任何影响
    '''
    #~ 检查指定的config文件是否存在
    if os.path.exists(opt.config):
        yamlConfig = yaml.safe_load(open(opt.config))
        yamlConfig = {} if not yamlConfig or not yamlConfig['JOB'] else yamlConfig['JOB']
        yamlConfig = yaml_float_parsing(opt, yamlConfig)
    else:
        if opt.config=='config_default.yaml':
            create_default = input(f"{Tag['x']} Default_config doesn't exist, create? (yes/no): ")
            if create_default.lower() == 'yes':
                yamlConfig = {}
            else:
                raise ValueError(f"{Tag['x']} The defined config file doesn't exist: {opt.config}")
        else:
            raise ValueError(f"{Tag['x']} The defined config file doesn't exist: {opt.config}")
    defaultUpdated = False

    #~ 检查有没有现在已经不用的opt在当前config里
    expired_keys = [item for item in yamlConfig if item not in opt.__dict__]
    expireOp = None
    if len(expired_keys) != 0 and not new_job_saving:
        print(f"{Tag['x']} The current config contains expired opt: {expired_keys}")
        print(f'  1. Terminate runing\n  2. Auto update config file, move the expired opts to the end of config file\n  3. Auto update config file, delete expired opts')
        expireOp = input(f"{Tag['t']} Please choose: (1/2/3): ")
        if expireOp not in ['2','3']:
            sys.exit(f"{Tag['t']} Terminate running due to the expired opts, you can mannually update the config file.")

    #~ 检查有没有现在已经不用的opt在当前config里
    new_keys = [k for k in opt.__dict__ if k not in yamlConfig]
    new_keys = [k for k in new_keys if k not in ['config', 'configNotes']]
    if len(new_keys) != 0:
        newOp = input(f"{Tag['x']} Current config lack the opt: {new_keys}\n  do you want to auto update this opt with its default value? (yes/no): ")
        if newOp.lower() != 'yes':
            sys.exit(f"{Tag['t']} Terminate running due to the lack of opts, you can mannually update the confile file.")

    #~ 新增/更新对应的config文件
    isUpdating = new_job_saving \
        or len(new_keys) != 0 \
        or len(expired_keys) != 0 \
        or opt.config=='config_default.yaml'

    if isUpdating:
        if new_job_saving:
            cfg = open(new_job_saving, 'w+') # 输出到新的保存的config文件
            print(job_stamp(), file=cfg)
        else:
            cfg = open(opt.config, 'w+') # 更新到原config文件上
        print('JOB:', file=cfg)

        for optKey in opt.__dict__:
            if optKey in ['config', 'configNotes']: continue

            #> 创建ymal config的分类注释
            if optKey in list(opt.configNotes):
                if optKey != list(opt.configNotes)[0]: print('', file=cfg) # 如果不是第一行，则需要另起一行
                print(opt.configNotes[optKey], file=cfg)

            #> 输出对应的opt信息到config文件
            optValue = opt.__dict__[optKey]
            if new_job_saving:
                out = optValue if not (optValue is None) else 'null'
                print(f"  {optKey}: {out}", file=cfg)
                continue

            #> (1) 新参数: 不存在于现在的config中
            if optKey not in yamlConfig:
                if not new_job_saving:
                    print(f"{Tag['t']} {optKey} missed, update with default: {optValue}")
                out = optValue if not (optValue is None) else 'null'
            else:
                yamlValue = yamlConfig[optKey]

                #> (2) 已有参数: 更新defaul_config时, 参数存在但是值与default不同
                if opt.config=='config_default.yaml' and yamlValue != optValue:
                    print(f"{Tag['t']} {optKey} updated: {[yamlValue]} -> {[optValue]}")
                    out = optValue if not (optValue is None) else 'null'
                    defaultUpdated = True
                #> (3) 已有参数: 存在于当前config，直接保留
                else:
                    out = yamlValue if not (yamlValue is None) else 'null'

            print(f"  {optKey}: {out}", file=cfg)

        #~ 移动过期opt至config末尾
        if len(expired_keys) != 0:
            if expireOp == '2':
                print('\n#~ Expired optKeys', file=cfg)
                for optkey in expired_keys:
                    print(f"  {optkey}: {yamlConfig[optkey]}", file=cfg)
            elif expireOp == '3':
                print(f"{Tag['t']} Remove the expired opts in config: {expired_keys}")

        if new_job_saving:
            print(f"{Tag['ok']} Save the current job config file: {opt.config}")
            return

        if isUpdating:
            if opt.config=='config_default.yaml' and defaultUpdated:
                print(f"{Tag['ok']} Default_config is updated")
            else:
                print(f"{Tag['ok']} Default_config is the newest~")
            if len(new_keys) != 0:
                print(f"{Tag['ok']} Add new opt: {new_keys}")
            if len(expired_keys) != 0 and expireOp == '3':
                print(f"{Tag['ok']} Remove expired opt: {expired_keys}")
        else:
            print(f"{Tag['ok']} Config is the newest~")

        return

def update_with_config(opt):
    '''
    Update the default exp settings with the cmd input and config file
    Priority: cmd input > yaml config file (cfg) > default (opt.py)

    Args:
        opt: the parsed args from opts.py

    Returns:
        opt: the updated opts
        updatedOptKeys: a list of updated param's keys
    '''
    auto_update_config(opt)

    cmd_inputs = [arg[2:] for arg in sys.argv[1:] if arg[:2] == '--']
    cfg = yaml.safe_load(open(opt.config))['JOB']
    cfg = yaml_float_parsing(opt, cfg)
    updatedOptKeys = []

    for optKey in opt.__dict__:
        if optKey in ['config', 'configNotes']:
            continue

        #> cmd input param (most-priority)
        if optKey in cmd_inputs:
            updatedOptKeys.append(optKey)

        #> config file param (if no cmd input)
        else:
            if opt.__dict__[optKey] != cfg[optKey]:
                opt.__dict__[optKey] = cfg[optKey]
                updatedOptKeys.append(optKey)

    return opt

def check_job_path(opt):
    '''
    Check if the experiment's saving path is existed, if not, create it.
    If it is created, then check whether this is finsihed job. If has, the program will ask user if continue.

    Args:
        opt: the parsed args from opts.py
    '''
    if os.path.exists(f'{opt.result_path}/{opt.task}/{opt.log_time}'):
        #> if detected a finished job, ask user if continue
        if os.path.exists(f'{opt.result_path}/{opt.task}/{opt.log_time}/.FINISHED_JOB'):
            user_input = input(f"A Finished job [{opt.task}-{opt.log_time}] is already existed.\nIf continue the previous checkpoint may be overwritten.\nDo you really want to continue? (yes/no): ")
            if user_input.lower() != "yes":
                print("The job have stopped, you can re-run this script with a new task name or a new log time.")
                sys.exit()
    else:
        os.makedirs(f'{opt.result_path}/{opt.task}/{opt.log_time}')

def save_job_config(opt):
    '''
    Save the job config file of this job.
    The job can be re-run with this saved config file.

    Args:
        opt: the parsed args from opts.py
        updatedOptKeys: a list of updated param's keys from check_updated_opts()
    '''
    check_job_path(opt)

    if 'noun_only' in opt.__dict__:
        if opt.noun_only: NorV = '-N'
        elif opt.verb_only: NorV = '-V'
        else: raise ValueError(f"{Tag['x']} noun/verb task is not defined")
    else:
        NorV = ''

    save_path = f'{opt.result_path}/{opt.task}/{opt.log_time}/{opt.log_time}-{opt.task}{NorV}.yaml'
    auto_update_config(opt, new_job_saving=save_path)