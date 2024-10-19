import torch

from .voice_gender_classifier_model import ECAPA_gender

# You could directly download the model from the huggingface model hub
model = ECAPA_gender.from_pretrained("JaesungHuh/ecapa-gender")
model.eval()

# If you are using gpu or not.
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

def gender_identify(voice_file):
    try:
        # Load the voice file and use predict function to directly get the output
        with torch.no_grad():
            return model.predict(voice_file, device=device)
    except Exception as e:
        # 异常处理
        print(f"发生错误: {e}")
        return ''