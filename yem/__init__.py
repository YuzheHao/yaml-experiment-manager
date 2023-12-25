import argparse
from yem.utils import update_with_config, save_job_config

def parse_opts():
    optNotes = {}
    parser = argparse.ArgumentParser()

    parser.add_argument('--config', type=str,
        default='config_default.yaml',
        help= 'the config yaml file, load all the options from this entry')


    optNotes['task'] = '#~ task basic information'
    parser.add_argument('--task', type=str,
        default='NewTask',
        help='the name of task')

    parser.add_argument('--log_time', type=str,
        default='NOW',
        help='Start time, usaully will be manullay set')

    parser.add_argument('--result_path', type=str,
        default='experiments/runs',
        help='Result directory path')

    parser.add_argument('--comment', type=str,
        default=None,
        help='Some comments about this experiment')


    optNotes['param_A'] = '#~ task 123 information'
    parser.add_argument('--param_A', type=str,
        default='AAA',
        help='YourParameter')

    parser.add_argument('--param_B', type=str,
        default='BBB',
        help='YourParameter2')

# ------------------------------------------------ #

    #~ Load exp settings
    opt = parser.parse_args() # 这里得到的opt是已经default的基础上获取了cmd input的opt
    opt.configNotes = optNotes

    #~ Update with config
    opt = update_with_config(opt) # 使用config文件更新opt，如果有cmd input的key会被跳过

    #~ Creath directory and Save job config
    save_job_config(opt)

    return opt