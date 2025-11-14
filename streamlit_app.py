import streamlit as st
import wave
import struct
import os

# Function to embed watermark
def embed_watermark(input_wav, watermark_text, output_wav):
    with wave.open(input_wav, 'rb') as wav_file:
        params = wav_file.getparams()
        frames = wav_file.readframes(params.nframes)

    samples = list(struct.unpack('<' + 'h' * (len(frames) // 2), frames))

    watermark_bin = ''.join(f'{ord(c):08b}' for c in watermark_text)
    if len(watermark_bin) > len(samples):
        raise ValueError("Watermark too long for the audio file!")

    for i, bit in enumerate(watermark_bin):
        samples[i] = (samples[i] & ~1) | int(bit)

    modified_frames = struct.pack('<' + 'h' * len(samples), *samples)

    with wave.open(output_wav, 'wb') as out:
        out.setparams(params)
        out.writeframes(modified_frames)

    return output_wav

# Function to extract watermark
def extract_watermark(input_wav, watermark_length):
    with wave.open(input_wav, 'rb') as wav_file:
        frames = wav_file.readframes(wav_file.getnframes())

    samples = list(struct.unpack('<' + 'h' * (len(frames) // 2), frames))

    bits = [str(samples[i] & 1) for i in range(watermark_length * 8)]
    watermark_bin = ''.join(bits)

    chars = [chr(int(watermark_bin[i:i+8], 2)) for i in range(0, len(watermark_bin), 8)]
    return ''.join(chars)

# Streamlit UI layout
st.title("🎵 Audio Watermarking App")
st.write("Embed and extract hidden text inside WAV audio using LSB steganography.")

tab1, tab2 = st.tabs(["🔐 Embed Watermark", "🔍 Extract Watermark"])

with tab1:
    uploaded_file = st.file_uploader("Upload a .wav audio file", type=["wav"])
    watermark_text = st.text_input("Enter watermark text")
    if st.button("Embed Watermark"):
        if uploaded_file and watermark_text:
            input_path = "temp_input.wav"
            output_path = "output_watermarked.wav"

            with open(input_path, "wb") as f:
                f.write(uploaded_file.read())

            embed_watermark(input_path, watermark_text, output_path)

            st.success("Watermark embedded successfully!")
            st.download_button("Download Watermarked File", open(output_path, "rb"), file_name="watermarked.wav")

with tab2:
    extract_file = st.file_uploader("Upload a watermarked .wav file", type=["wav"])
    wm_length = st.number_input("Watermark length (number of characters)", min_value=1, step=1)

    if st.button("Extract Watermark"):
        if extract_file:
            input_path2 = "temp_extract.wav"
            with open(input_path2, "wb") as f:
                f.write(extract_file.read())

            result = extract_watermark(input_path2, int(wm_length))
            st.success("Extracted Watermark:")
            st.code(result)

