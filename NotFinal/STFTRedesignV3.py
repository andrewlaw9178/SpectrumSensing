mport numpy as np
import matplotlib.pyplot as plt

# Generate a synthesised 5G NR signal
f_carrier = 100 # Carrier frequence in Hz
t = np.arange(0, 5, 0.01)
signal_cont = np.sin(2 * np.pi * f_carrier * t)

fs = 2000 # Sampling frequency in Hz
Ts = 1/fs
N = int((2*np.pi) / (np.pi / 10))
n_ = np.arange(N)
n = np.tile(n_, 5)
signal = np.sin(2 * np.pi * f_carrier * n / fs)

# Determine STFT parameters
window_size = 8
overlap = 0.5

# Determine overlap
step_size = int(window_size*overlap)
print('step_size = ', step_size)

# Determine number of frames
if len(signal) < window_size:
        num_frames = 1
else:
    num_frames = int(np.floor((len(n) - window_size) / step_size) + 1)
print('num_frames = ', num_frames)

# Segmentation - all frames must be window_size bits long
signal_input = np.zeros((window_size, num_frames))
print(signal_input)
for i in range(num_frames):
    if i == 0:
        start = i
        end = start + window_size
    else:
        start = end - step_size
        end = start + window_size
        if end > len(n):
            end = len(n)
    if (end-start)<window_size:
        signal_input[:, i] = np.append(signal[start:end], np.zeros(window_size - (end-start)))
    else:
        signal_input[:, i] = signal[start:end]

#Apply Hamming Window function
w_n = 0.54 + 0.46 * np.cos(2 * np.pi * n_ / N)
print('w_n = ', w_n)
print(len(n_))
print(len(w_n))
print(len(signal_input[:, 1]))
for i in range(num_frames):
    for j in range (window_size):
        signal_input[j, i] = signal_input[j, i] * w_n[j]

# Apply STFT transmformation
stft_matrix = np.zeros((num_frames, window_size), dtype = np.complex128)
for i in range(num_frames):
    frame = signal_input[:, i]
    stft_matrix[i, :] = np.fft.fft(frame, n=window_size)



# #Plot the original signal
# plt.figure(figsize=(12,6))
# plt.subplot(2, 1, 1)
# plt.plot(t,signal_cont)
# plt.title('Original 5G NR Signal')

plt.figure(figsize=(12,6))
plt.subplot(2, 1, 1)
plt.plot(n,signal)
plt.title('Original Sampled 5G NR Signal')

# Plot the STFT representation
plt.subplot(2, 1, 2)
plt.imshow(20 * np.log10(np.abs(stft_matrix.T)/2), aspect = 'auto', extent = [0, len(t), 0, fs/2], cmap = 'viridis')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Time (s)')
plt.title('Spectrogram')
plt.colorbar(label='Magnitude (dB)')

plt.tight_layout()
plt.show()
