import time
from youdub.do_everything import do_everything
from datetime import datetime

# %%
def log(message):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{current_time} - {message}")

log("定时执行所有任务，将播放列表的视频下载到本地，然后进行语音分离、语音识别、翻译、语音合成、视频合成、视频信息生成。")
while True:
    do_everything(
        root_folder='videos',
        url='https://youtube.com/playlist?list=PLxjtcx2z5_40UUWaDpcYGMrBnO5ahON4U,https://youtube.com/playlist?list=PLxjtcx2z5_42a0Yg4OTTvpjwrdTWX7t2g,https://youtube.com/playlist?list=PLxjtcx2z5_42oMZU6Fo8QbS-INscLa-nD,https://youtube.com/playlist?list=PLxjtcx2z5_42mqzz6ceEuRRkOWacgN_4p,https://youtube.com/playlist?list=PLxjtcx2z5_434zKqK9PKSJocH9JVLFAOV,https://youtube.com/playlist?list=PLxjtcx2z5_42UfWZh1TMm1q1q3dpFq3L-,https://youtube.com/playlist?list=PLxjtcx2z5_421o4PXGzhUeRDNf8Z31gA1',
        num_videos=10000,
        resolution='1080p',
        demucs_model='htdemucs_ft',
        device='auto',
        shifts=5,
        whisper_model='large-v3',
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

    log("等待10分钟后再次执行 ...")
    time.sleep(60*10)