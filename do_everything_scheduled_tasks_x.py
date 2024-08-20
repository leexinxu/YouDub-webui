import time
import gc
import os
import sys

# 用于跟踪当前要执行的任务
flag_file = 'task_flag.txt'


def do_everything_x2zh():
    from youdub.do_everything import do_everything

    print("执行，X译中，任务。。。。。。")
    do_everything(
        root_folder='videos_20240808',
        url='https://www.youtube.com/playlist?list=PLxjtcx2z5_41az-SgsVydfeogWu8nQkMe',
        num_videos=10000,
        resolution='1080p',
        demucs_model='htdemucs_ft',
        device='auto',
        shifts=5,
        whisper_model='distil-large-v2',
        whisper_download_root='models/ASR/whisper',
        whisper_batch_size=16,
        whisper_diarization=False,
        whisper_min_speakers=None,
        whisper_max_speakers=None,
        translation_target_language='简体中文',
        force_bytedance=False,
        subtitles=True,
        speed_up=1.05,
        fps=30,
        target_resolution='1080p',
        max_workers=1,
        max_retries=3,
        auto_upload_video=False
    )

    # 手动触发垃圾回收
    gc.collect()


def do_everything_zh2en():
    from youdub.do_everything_zh2en import do_everything
    
    print("执行，中译英，任务。。。。。。")
    do_everything(
        root_folder='videos_zh2en',
        url='https://www.bilibili.com/list/ml136498038',
        num_videos=10000,
        resolution='1080p',
        demucs_model='htdemucs_ft',
        device='auto',
        shifts=5,
        whisper_model='large',
        whisper_download_root='models/ASR/whisper',
        whisper_batch_size=16,
        whisper_diarization=False,
        whisper_min_speakers=None,
        whisper_max_speakers=None,
        translation_target_language='English',
        force_bytedance=False,
        subtitles=True,
        speed_up=1.05,
        fps=30,
        target_resolution='1080p',
        max_workers=1,
        max_retries=3,
        auto_upload_video=False
    )

    # 手动触发垃圾回收
    gc.collect()


def restart_program():
    """重启当前的 Python 程序"""
    print("\n\n重启，X译X，任务脚本。。。。。。\n\n")
    os.execv(sys.executable, ['python'] + sys.argv)


def get_next_task():
    """确定下一个要执行的任务"""
    if os.path.exists(flag_file):
        with open(flag_file, 'r') as f:
            return f.read().strip()
    else:
        return 'x2zh'  # 默认情况下，先执行 X译中


def set_next_task(task):
    """设置下一个要执行的任务"""
    with open(flag_file, 'w') as f:
        f.write(task)


# 脚本启动时，检查并执行相应的任务
next_task = get_next_task()

if next_task == 'x2zh':
    do_everything_x2zh()
    set_next_task('zh2en')
else:
    do_everything_zh2en()
    set_next_task('x2zh')

# 等待 3 分钟后重启程序
print("等待 3 分钟后重启程序...")
time.sleep(60 * 3)

# 重启脚本以确保内存完全释放
restart_program()