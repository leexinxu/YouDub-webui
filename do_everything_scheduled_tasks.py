import time
from youdub.do_everything import do_everything


print("定时执行所有任务，将播放列表的视频下载到本地，然后进行语音分离、语音识别、翻译、语音合成、视频合成、视频信息生成。")
while True:
    do_everything(
        root_folder='videos_20240821',
        url='https://youtube.com/playlist?list=PLxjtcx2z5_439PyJFNx4XOS0qos6en-a-',
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

    print("等待10分钟后再次执行 ...")
    time.sleep(60*10)