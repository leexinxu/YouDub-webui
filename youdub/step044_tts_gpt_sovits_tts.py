from pathlib import Path
import requests
from rich import print as rprint
import os, sys
import requests
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

def check_lang(text_lang, prompt_lang):
    #TODO 可以考虑用ask gpt来判断语言
    if any(lang in text_lang.lower() for lang in ['zh', 'cn', '中文', 'chinese']):
        text_lang = 'zh'
    elif any(lang in text_lang.lower() for lang in ['英文', '英语', 'english']):
        text_lang = 'en'
    else:
        raise ValueError("Unsupported text language. Only Chinese and English are supported.")
    
    if 'en' in prompt_lang.lower():
        prompt_lang = 'en'
    elif any(lang in prompt_lang.lower() for lang in ['zh', 'cn', '中文', 'chinese']):
        prompt_lang = 'zh'
    else:
        raise ValueError("Unsupported prompt language. Only Chinese and English are supported.")
    return text_lang, prompt_lang


def gpt_sovits_tts(text, text_lang, save_path, ref_audio_path, prompt_lang, prompt_text):
    text_lang, prompt_lang = check_lang(text_lang, prompt_lang)

    current_dir = Path.cwd()
    
    payload = {
        'text': text,
        'text_lang': text_lang,
        'ref_audio_path': str(ref_audio_path),
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

    response = requests.post('http://127.0.0.1:9880/tts', json=payload)
    if response.status_code == 200:
        return save_audio(response, save_path, current_dir)
    else:
        rprint(f"[bold red]TTS请求失败，状态码:[/bold red] {response.status_code}")
        return False
