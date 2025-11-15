import cv2
import numpy as np
import os
from ultralytics import YOLO

import easyocr
import torch
from PIL import Image  # <-- मुख्य सुधार: Image क्लास को PIL से इम्पोर्ट किया गया

from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from django.conf import settings # Django settings से path लेने के लिए

# --------------------------
# CONFIG
# --------------------------------
# MODEL_PATH को Django settings का उपयोग करके train_model फ़ोल्डर के अंदर सेट करें
MODEL_PATH = os.path.join(settings.BASE_DIR, 'mainapp', 'train_model', 'best.pt')

# --------------------------------

# --- सभी मॉडल्स को इनिशियलाइज़ करें ---
try:
     # 1. YOLO
  model_yolo = YOLO(MODEL_PATH)
  
  # 2. EasyOCR (लेआउट डिटेक्शन के लिए)
  reader_easyocr = easyocr.Reader(['en'], gpu=False) 
  print("YOLO and EasyOCR Reader initialized.")

  # 3. TrOCR (टेक्स्ट रीडिंग के लिए)
  device = "cuda" if torch.cuda.is_available() else "cpu"
  print(f"Using device for TrOCR: {device}")
  
  processor_trocr = TrOCRProcessor.from_pretrained('microsoft/trocr-base-printed')
  model_trocr = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-printed').to(device)
  
  print("TrOCR models initialized successfully.")
except Exception as e:
  print(f"Error initializing models: {e}")
  # production में इसे gracefully handle करें, अभी हम exit नहीं कर सकते
  # raise e # Django server को crash होने दें अगर मॉडल लोड नहीं हो सकते

# ----------------------------------------
# Utility: Positional Correction (9 और 10 कैरेक्टर, दोनों के लिए)
# ----------------------------------------
ALLOWED_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

MAP_LETTER_TO_NUM = {
  'O': '0', 'D': '0', 'Q': '0', 'I': '1', 'L': '1', 'Z': '2',
  'S': '5', 'B': '8', 'G': '6', 'E': '3', 'J': '3', 'T': '7', 'A': '4'
}

MAP_NUM_TO_LETTER = {
  '0': 'O', '1': 'I', '2': 'Z', '5': 'S', '8': 'B',
  '6': 'G', '3': 'E', '7': 'T', '4': 'A'
}

def clean_and_correct(text):
  """
  टेक्स्ट को साफ करता है और लंबाई के आधार पर 9 (LLNNLNNNN) या 10 (LLNNLLNNNN) 
  कैरेक्टर पैटर्न लागू करता है।
  """
  cleaned_text = "".join(filter(lambda ch: ch in ALLOWED_CHARS, text.upper()))
  length = len(cleaned_text)
  final_plate = ""

  # केस 1: अगर लंबाई 10 है (LLNNLLNNNN)
  if length == 10:
    for i, char in enumerate(cleaned_text):
      if i in [0, 1, 4, 5]: # LL / LL
        final_plate += MAP_NUM_TO_LETTER.get(char, char)
      elif i in [2, 3, 6, 7, 8, 9]: # NN / NNNN
        final_plate += MAP_LETTER_TO_NUM.get(char, char)
      
  # केस 2: अगर लंबाई 9 है (LLNNLNNNN)
  elif length == 9:
    for i, char in enumerate(cleaned_text):
      if i in [0, 1, 4]: # LL / L
        final_plate += MAP_NUM_TO_LETTER.get(char, char)
      elif i in [2, 3, 5, 6, 7, 8]: # NN / NNNN
        final_plate += MAP_LETTER_TO_NUM.get(char, char)

  else:
    return cleaned_text # बिना पोज़ीशनल करेक्शन के लौटा दें
      
  return final_plate


# ----------------------------------------
# TrOCR Recognizer 
# ----------------------------------------
def recognize_plate_trocr(img_cv2):
    # अब Image.fromarray का उपयोग करने के लिए PIL का Image क्लास उपलब्ध है
  try:
    img_pil = Image.fromarray(cv2.cvtColor(img_cv2, cv2.COLOR_BGR2RGB))
  except cv2.error:
    img_pil = Image.fromarray(img_cv2).convert("RGB")

  if img_pil.width < 10 or img_pil.height < 10:
    return ""

  pixel_values = processor_trocr(images=img_pil, return_tensors="pt").pixel_values.to(device)
  generated_ids = model_trocr.generate(pixel_values)
  generated_text = processor_trocr.batch_decode(generated_ids, skip_special_tokens=True)[0]
  return generated_text 

# ----------------------------------------
# Preprocessing for EasyOCR
# ----------------------------------------
def preprocess_for_easyocr(img):
  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  gray = cv2.GaussianBlur(gray, (5, 5), 0)
  clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
  enhanced = clahe.apply(gray)
  return enhanced

# ----------------------------------------
# HYBRID OCR 
# ----------------------------------------
def recognize_plate_hybrid(plate_crop):
  
  processed_for_easyocr = preprocess_for_easyocr(plate_crop)
  
  results = reader_easyocr.readtext(processed_for_easyocr, 
                  allowlist=ALLOWED_CHARS,
                  paragraph=False,
                  min_size=10,
                  y_ths=0.7,
                  x_ths=0.5
                  )
  
  if not results:
    # अगर EasyOCR कुछ नहीं ढूँढ पाता है, तो TrOCR को पूरी क्रॉप दें
    full_text = recognize_plate_trocr(plate_crop)
    return clean_and_correct(full_text)

  results.sort(key=lambda r: r[0][0][1]) # top-left Y

  lines_bboxes = []
  current_line_y = -1
  current_line_bboxes = []
  line_height_threshold = 0
  
  for (bbox, text, prob) in results:
    # ... (लाइन डिटेक्शन लॉजिक, जैसा आपने दिया) ...
    top_left_y = bbox[0][1]
    
    if not current_line_bboxes:
      current_line_y = top_left_y
      current_line_bboxes.append(bbox)
      line_height_threshold = (bbox[3][1] - bbox[0][1]) * 0.7
    elif abs(top_left_y - current_line_y) < line_height_threshold:
      current_line_bboxes.append(bbox)
    else:
      lines_bboxes.append(current_line_bboxes)
      current_line_y = top_left_y
      current_line_bboxes = [bbox]
      line_height_threshold = (bbox[3][1] - bbox[0][1]) * 0.7

  if current_line_bboxes:
    lines_bboxes.append(current_line_bboxes)

  final_text = ""
  PADDING = 2
  
  for line_bboxes in lines_bboxes:
    x_min = min(b[0][0] for b in line_bboxes)
    y_min = min(b[0][1] for b in line_bboxes)
    x_max = max(b[1][0] for b in line_bboxes) 
    y_max = max(b[2][1] for b in line_bboxes) 
    
    x_min = int(x_min)
    y_min = int(y_min)
    x_max = int(x_max)
    y_max = int(y_max)
    
    y_min_pad = max(0, y_min - PADDING)
    y_max_pad = min(plate_crop.shape[0], y_max + PADDING)
    x_min_pad = max(0, x_min - PADDING)
    x_max_pad = min(plate_crop.shape[1], x_max + PADDING)

    line_crop_img = plate_crop[y_min_pad:y_max_pad, x_min_pad:x_max_pad]
    
    line_text = recognize_plate_trocr(line_crop_img)
    final_text += line_text

  return clean_and_correct(final_text)

# ----------------------------------------
# MAIN RUNNER FUNCTION FOR DJANGO VIEW
# ----------------------------------------
def run_anpr(frame):
  """
  इनपुट BGR numpy array पर पूरा ANPR पाइपलाइन चलाता है।
  
  Args:
    frame (np.array): BGR फॉर्मेट में इनपुट इमेज फ्रेम।
    
  Returns:
    str: recognized license plate number, or empty string.
  """
  try:
    # 1. YOLO डिटेक्शन
    results = model_yolo(frame)
    detections = results[0].boxes.xyxy.cpu().numpy()
    
    if len(detections) == 0:
      return "" # No plate detected

    # सबसे पहले डिटेक्टेड प्लेट को प्रोसेस करें
    x1, y1, x2, y2 = map(int, detections[0, :4])
    
    # 2. क्रॉपिंग और पैडिंग
    y1_b = max(0, y1 - 5)
    y2_b = min(frame.shape[0], y2 + 5)
    x1_b = max(0, x1 - 5)
    x2_b = min(frame.shape[1], x2 + 5) 
    plate_crop = frame[y1_b:y2_b, x1_b:x2_b]

    if plate_crop.size == 0:
      return ""

    # 3. हाइब्रिड OCR
    final_text = recognize_plate_hybrid(plate_crop)

    return final_text
  
  except Exception as e:
    print(f"ANPR Core Error: {e}")
    return f"ERROR: {e}"