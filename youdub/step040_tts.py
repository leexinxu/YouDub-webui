import json
import os
import re
import librosa

from loguru import logger
import numpy as np

from .utils import save_wav, save_wav_norm
from .step041_tts_bytedance import tts as bytedance_tts
#from .step042_tts_xtts import tts as xtts_tts
from .step043_tts_chattts import tts as chattts_tts
from .step044_tts_gpt_sovits_tts import gpt_sovits_tts
from .cn_tx import TextNorm
from audiostretchy.stretch import stretch_audio

from langdetect import detect

from .voice_gender_classifier import gender_identify

normalizer = TextNorm()
def preprocess_text(text):
    text = text.replace('AI', '人工智能')
    text = re.sub(r'(?<!^)([A-Z])', r' \1', text)
    text = normalizer(text)
    # 使用正则表达式在字母和数字之间插入空格
    text = re.sub(r'(?<=[a-zA-Z])(?=\d)|(?<=\d)(?=[a-zA-Z])', ' ', text)
    return text
    
    
def adjust_audio_length(wav_path, desired_length, sample_rate = 24000, min_speed_factor = 0.8, max_speed_factor = 1.05):
    wav, sample_rate = librosa.load(wav_path, sr=sample_rate)
    current_length = len(wav)/sample_rate
    speed_factor = max(
        min(desired_length / current_length, max_speed_factor), min_speed_factor)
    desired_length = current_length * speed_factor
    target_path = wav_path.replace('.wav', f'_adjusted.wav')
    stretch_audio(wav_path, target_path, ratio=speed_factor, sample_rate=sample_rate)
    wav, sample_rate = librosa.load(target_path, sr=sample_rate)
    return wav[:int(desired_length*sample_rate)], desired_length


def generate_wavs(folder, force_bytedance=False):
    transcript_path = os.path.join(folder, 'translation.json')
    output_folder = os.path.join(folder, 'wavs')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    with open(transcript_path, 'r', encoding='utf-8') as f:
        transcript = json.load(f)
    speakers = set()
    
    for line in transcript:
        speakers.add(line['speaker'])
    num_speakers = len(speakers)
    logger.info(f'Found {num_speakers} speakers')

    if '多角色' in folder:
        chattts_voice = {
            "男": [
                "seed_2222_restored_emb-covert.pt",
                "seed_1346_restored_emb-covert.pt",
                "seed_1457_restored_emb-covert.pt",
                "seed_1509_restored_emb-covert.pt",
                "seed_1345_restored_emb-covert.pt"
                
            ],
            "女": [
                "seed_1754_restored_emb-covert.pt",
                "seed_742_restored_emb-covert.pt",
                "seed_1742_restored_emb-covert.pt",
                "seed_2_restored_emb-covert.pt",
                "seed_2218_restored_emb-covert.pt"
            ]
        }

        # 分配配音角色
        speaker_roles = {}
        male_index = 0
        female_index = 0

        for speaker in speakers:
            gender = gender_identify(os.path.join(folder, 'SPEAKER', f'{speaker}.wav'))
            logger.info(f'Identified speaker {speaker} as {gender}')
            if "male" == gender:
                # 按顺序分配男性角色
                role = chattts_voice["男"][male_index % len(chattts_voice["男"])]  # 循环分配男性角色
                male_index += 1  # 更新男性角色索引
            else:
                # 按顺序分配女性角色
                role = chattts_voice["女"][female_index % len(chattts_voice["女"])]  # 循环分配女性角色
                female_index += 1  # 更新女性角色索引

            speaker_roles[speaker] = role
        logger.info(f'{speaker_roles=}')
        
    full_wav = np.zeros((0, ))
    for i, line in enumerate(transcript):
        speaker = line['speaker']
        text = preprocess_text(line['translation'])
        output_path = os.path.join(output_folder, f'{str(i).zfill(4)}.wav')
        speaker_wav = os.path.join(folder, 'SPEAKER', f'{speaker}.wav')
        # if num_speakers == 1:
        #     bytedance_tts(text, output_path, speaker_wav, voice_type='BV701_streaming')
        # elif force_bytedance:
        #     bytedance_tts(text, output_path, speaker_wav)
        # else:
        #     xtts_tts(text, output_path, speaker_wav)

        if '原音色克隆' in folder: 
            if not gpt_sovits_tts(text, 'zh', output_path, speaker_wav, 'auto', ''):
                chattts_tts(text=text, output_path=output_path, speaker_wav=None, voice_type='seed_1754_restored_emb-covert.pt')
        elif '多角色' in folder:
            chattts_tts(text=text, output_path=output_path, speaker_wav=None, voice_type=speaker_roles[speaker])
        elif '中配男' in folder:
            chattts_tts(text=text, output_path=output_path, speaker_wav=None, voice_type='seed_2222_restored_emb-covert.pt')
        else:
            chattts_tts(text=text, output_path=output_path, speaker_wav=None, voice_type='seed_1754_restored_emb-covert.pt')

        start = line['start']
        end = line['end']
        length = end-start
        last_end = len(full_wav)/24000
        if start > last_end:
            full_wav = np.concatenate((full_wav, np.zeros((int((start - last_end) * 24000), ))))
        start = len(full_wav)/24000
        line['start'] = start
        if i < len(transcript) - 1:
            next_line = transcript[i+1]
            next_end = next_line['end']
            end = min(start + length, next_end)
        wav, length = adjust_audio_length(output_path, end-start)

        full_wav = np.concatenate((full_wav, wav))
        line['end'] = start + length
        
    vocal_wav, sr = librosa.load(os.path.join(folder, 'audio_vocals.wav'), sr=24000)
    full_wav = full_wav / np.max(np.abs(full_wav)) * np.max(np.abs(vocal_wav))
    save_wav(full_wav, os.path.join(folder, 'audio_tts.wav'))
    with open(transcript_path, 'w', encoding='utf-8') as f:
        json.dump(transcript, f, indent=2, ensure_ascii=False)
    
    instruments_wav, sr = librosa.load(os.path.join(folder, 'audio_instruments.wav'), sr=24000)
    len_full_wav = len(full_wav)
    len_instruments_wav = len(instruments_wav)
    
    if len_full_wav > len_instruments_wav:
        # 如果 full_wav 更长，将 instruments_wav 延伸到相同长度
        instruments_wav = np.pad(
            instruments_wav, (0, len_full_wav - len_instruments_wav), mode='constant')
    elif len_instruments_wav > len_full_wav:
        # 如果 instruments_wav 更长，将 full_wav 延伸到相同长度
        full_wav = np.pad(
            full_wav, (0, len_instruments_wav - len_full_wav), mode='constant')
    combined_wav = full_wav + instruments_wav
    # combined_wav /= np.max(np.abs(combined_wav))
    save_wav_norm(combined_wav, os.path.join(folder, 'audio_combined.wav'))
    logger.info(f'Generated {os.path.join(folder, "audio_combined.wav")}')
        

def generate_all_wavs_under_folder(root_folder, force_bytedance=False):
    for root, dirs, files in os.walk(root_folder):
        if 'translation.json' in files and 'audio_combined.wav' not in files:
            generate_wavs(root, force_bytedance)
    return f'Generated all wavs under {root_folder}'

if __name__ == '__main__':
    folder = r'videos/原音色克隆/Hot Freestyle/20241011 2 Chainz Talks With Teslas New Robot '
    #generate_wavs(folder, force_bytedance=False)
    gender = gender_identify('/Volumes/Data/AI/YouDub-webui/test/hello.wav')
    print(gender)
