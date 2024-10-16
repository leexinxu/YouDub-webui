from pathlib import Path
import requests
from rich import print as rprint
import os, sys
import requests
import time  # 用于重试间隔

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

def check_lang(text_lang, prompt_lang):
    #TODO 可以考虑用ask gpt来判断语言
    if any(lang in text_lang.lower() for lang in ['zh', 'cn', '中文', 'chinese']):
        text_lang = 'zh'
    elif any(lang in text_lang.lower() for lang in ['en', '英文', '英语', 'english']):
        text_lang = 'en'
    elif prompt_lang not in ['yue', 'ja', 'ko']:
        text_lang = 'auto'
    
    if 'en' in prompt_lang.lower():
        prompt_lang = 'en'
    elif any(lang in prompt_lang.lower() for lang in ['zh', 'cn', '中文', 'chinese']):
        prompt_lang = 'zh'
    elif prompt_lang not in ['yue', 'ja', 'ko']:
        prompt_lang = 'auto'
    
    return text_lang, prompt_lang


def gpt_sovits_tts(text, text_lang, save_path, ref_audio_path, prompt_lang, prompt_text, max_retries=3, retry_delay=2):
    text_lang, prompt_lang = check_lang(text_lang, prompt_lang)

    current_dir = Path.cwd()

    payload = {
        'text': text,
        'text_lang': text_lang,
        'ref_audio_path': str(Path(process_ref_audio(ref_audio_path)).resolve()),
        'prompt_lang': prompt_lang,
        'prompt_text': prompt_text,
        "speed_factor": 1.0,
    }

    def save_audio(response, save_path, current_dir):
        if save_path:
            full_save_path = current_dir / save_path
            full_save_path.parent.mkdir(parents=True, exist_ok=True)
            full_save_path.write_bytes(response.content)
            rprint(f"[bold green]音频保存成功:[/bold green] {full_save_path}")
        return True

    # 进行重试机制
    retries = 0
    while retries < max_retries:
        try:
            #print(f'{payload=}')
            response = requests.post('http://127.0.0.1:9880/tts', json=payload)
            if response.status_code == 200:
                return save_audio(response, save_path, current_dir)
            else:
                rprint(f"[bold red]TTS请求失败，状态码:[/bold red] {response.status_code}")
        except requests.exceptions.RequestException as e:
            rprint(f"[bold red]请求出现异常: {e}[/bold red]")
        
        retries += 1
        if retries < max_retries:
            rprint(f"[yellow]重试中... (第 {retries} 次尝试)[/yellow]")
            time.sleep(retry_delay)  # 等待一定时间后重试

    rprint(f"[bold red]TTS请求失败，已达到最大重试次数: {max_retries}[/bold red]")
    return False



from pydub import AudioSegment
from pathlib import Path

# 默认音频路径
default_audio_path = Path("audio/ElonMusk2.wav")

def process_ref_audio(ref_audio_path):
    ref_audio_path = Path(ref_audio_path)
    
    # 构造裁剪后的文件路径，添加 "_cropped" 后缀
    cropped_audio_path = ref_audio_path.with_name(ref_audio_path.stem + "_cropped.wav")
    
    # 检查裁剪后的文件是否存在
    if cropped_audio_path.exists():
        print(f"裁剪后的音频已存在，直接返回: {cropped_audio_path}")
        return cropped_audio_path
    
    try:
        # 使用 pydub 读取音频文件
        audio = AudioSegment.from_file(ref_audio_path)
        
        # 获取音频时长，单位为毫秒
        duration_ms = len(audio)
        duration_seconds = duration_ms / 1000
        
        if duration_seconds > 10:
            # 裁剪音频为 10 秒
            audio = audio[:10 * 1000]
            # 保存裁剪后的音频
            audio.export(cropped_audio_path, format="wav")
            print(f"音频长于10秒，裁剪为: {cropped_audio_path}")
            return cropped_audio_path
        
        elif duration_seconds < 3:
            # 使用默认音频
            print(f"音频小于3秒，使用默认音频: {default_audio_path}")
            return default_audio_path
        
        else:
            # 音频在3秒到10秒之间，直接返回原始路径
            print(f"音频长度合适，保持原始路径: {ref_audio_path}")
            return ref_audio_path
        
    except Exception as e:
        print(f"处理音频文件时出错: {e}")
        return default_audio_path  # 如果出现错误，使用默认音频

if __name__ == '__main__':
    # 示例使用
    ref_audio = "/Volumes/Data/AI/YouDub-webui/videos/原音色克隆/Hot Freestyle/20241011 2 Chainz Talks With Teslas New Robot /SPEAKER/未命名.wav"
    processed_audio_path = process_ref_audio(ref_audio)
    print(f"最终参考音频路径: {processed_audio_path}")

