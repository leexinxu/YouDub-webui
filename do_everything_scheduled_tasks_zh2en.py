import time
from youdub.do_everything_zh2en import do_everything
from datetime import datetime

# %%
def log(message):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{current_time} - {message}")

log("执行，中译英，任务。")
while True:
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

    log("等待10分钟后再次执行 ...")
    time.sleep(60*10)