import streamlit as st
import wave
import struct
import os

# ---------- EMBED ---------- #
def embed_watermark(input_wav, watermark_text, output_wav):
    with wave.open(input_wav, "rb") as wav:
        params = wav.getparams()
        frames = wav.readframes(params.nframes)

    samples = list(struct.unpack("<" + "h" * (len(frames) // 2), frames))

    watermark_bits = ''.join(format(ord(c), '08b') for c in watermark_text)
    length_bits = format(len(watermark_bits), '016b')  # 16 bits for length

    final_bits = length_bits + watermark_bits

    for i, bit in enumerate(final_bits):
        if i < len(samples):
            samples[i] = (samples[i] & ~1) | int(bit)

    new_frames = struct.pack("<" + "h" * len(samples), *samples)

    with wave.open(output_wav, "wb") as wav_out:
        wav_out.setparams(params)
        wav_out.writeframes(new_frames)

    return output_wav


# ---------- EXTRACT ---------- #
def extract_watermark(input_wav):
    with wave.open(input_wav, "rb") as wav:
        frames = wav.readframes(wav.getnframes())

    samples = list(struct.unpack("<" + "h" * (len(frames) // 2), frames))

    # 1. Read first 16 bits = watermark length
    length_bits = ''.join(str(samples[i] & 1) for i in range(16))
    wm_length = int(length_bits, 2)

    # 2. Read watermark bits
    watermark_bits = ''.join(str(samples[16 + i] & 1) for i in range(wm_length))

    # 3. Convert to text
    watermark = ''.join(chr(int(watermark_bits[i:i+8], 2)) for i in range(0, wm_length, 8))

    return watermark


# ---------- STREAMLIT UI ---------- #
st.title("🎵 Audio Watermarking App")
st.write("Embed and extract hidden text inside WAV audio using LSB steganography.")

tab1, tab2 = st.tabs(["🔐 Embed Watermark", "🔍 Extract Watermark"])

# Embed tab
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
            st.download_button("Download Watermarked File", open(output_path, "rb"),
                               file_name="watermarked.wav")

# Extract tab
with tab2:
    extract_file = st.file_uploader("Upload a watermarked .wav audio", type=["wav"])

    if st.button("Extract Watermark"):
        if extract_file:
            path2 = "temp_extract.wav"
            with open(path2, "wb") as f:
                f.write(extract_file.read())

            result = extract_watermark(path2)
            st.success("Extracted Watermark:")
            st.code(result)
