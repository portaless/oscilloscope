import pyvisa
import numpy as np
import matplotlib.pyplot as plt

# Variables
visa_address = 'USB0::0x0699::0x03C7::C010286::INSTR'
buffer_size = 2000 * 1024  # 20 KiB

# Open instrument
rm = pyvisa.ResourceManager()
dpo2k = rm.open_resource(visa_address)
dpo2k.timeout = 10000  # Set timeout (in ms)
dpo2k.read_termination = '\n'
dpo2k.write_termination = '\n'

print(dpo2k.query('*IDN?'))  # Query instrument ID

# Configure output
dpo2k.write('wfmo:byt_n 1')
#record = int(dpo2k.query('hor:reco?'))
record = 2000
#print(f"record data = {record}")
dpo2k.write('header 0')
dpo2k.write('data:encdg rib')  # Signed integer, MSB first
dpo2k.write('data:comp singular_yt')
dpo2k.write('data:resolution full')
dpo2k.write(f'data:start 1')
dpo2k.write(f'data:stop {record}')

# Function to get data from each channel
def get_channel_data(channel):
    # Open session for each channel (avoid closing it prematurely)
    dpo2k.write(f'data:source CH{channel}')  # Select the channel
    dpo2k.write('curve?')
    raw_data = dpo2k.read_raw()

    # Parse binary data
    header_length = int(raw_data[1:2])
    data_length = int(raw_data[2:2+header_length])
    samples = np.frombuffer(raw_data[2+header_length:2+header_length+data_length], dtype=np.int8)

    # Get scaling values
    x_incr = float(dpo2k.query('wfmo:xincr?'))  # Horizontal increment per point
    x_zero = float(dpo2k.query('wfmo:xzero?'))  # Offset on the X axis (time)
    y_incr = float(dpo2k.query('wfmo:ymult?'))  # Vertical scaling (V/div)
    y_off = float(dpo2k.query('wfmo:yoff?'))    # Vertical offset (V)
    y_zero = float(dpo2k.query('wfmo:yzero?'))  # Vertical zero reference (V)

    # Apply scaling and offset
    scaled_samples = (samples * y_incr) + (y_zero + y_off)

    # Adjust time base correctly (without applying x_zero, as it only shifts the plot)
    time_base = np.linspace(0, (record * x_incr), record)

    return time_base, scaled_samples

# Create the plot for all 3 channels
fig, axs = plt.subplots(3, 1, figsize=(10, 6), sharex=True)

# Plot data for CH1
time_base, scaled_samples_ch1 = get_channel_data(1)
max_voltage_ch1 = max(scaled_samples_ch1)  # Find the maximum voltage for scaling
axs[0].plot(time_base, scaled_samples_ch1, label='CH1')
axs[0].set_ylabel("Voltage (V)")
axs[0].set_title("Channel 1 Waveform")
axs[0].grid(True)
axs[0].set_ylim(0, max_voltage_ch1 + 1)  # Set Y-axis limits from 0 to max + 1

# Plot data for CH2
time_base, scaled_samples_ch2 = get_channel_data(2)
max_voltage_ch2 = max(scaled_samples_ch2)  # Find the maximum voltage for scaling
axs[1].plot(time_base, scaled_samples_ch2, label='CH2')
axs[1].set_ylabel("Voltage (V)")
axs[1].set_title("Channel 2 Waveform")
axs[1].grid(True)
axs[1].set_ylim(0, max_voltage_ch2 + 1)  # Set Y-axis limits from 0 to max + 1

# Plot data for CH3
time_base, scaled_samples_ch3 = get_channel_data(3)
max_voltage_ch3 = max(scaled_samples_ch3)  # Find the maximum voltage for scaling
axs[2].plot(time_base, scaled_samples_ch3, label='CH3')
axs[2].set_xlabel("Time (s)")
axs[2].set_ylabel("Voltage (V)")
axs[2].set_title("Channel 3 Waveform")
axs[2].grid(True)
axs[2].set_ylim(0, max_voltage_ch3 + 1)  # Set Y-axis limits from 0 to max + 1

# Show the plot
plt.tight_layout()
plt.show()

# Close the instrument session after finishing all data retrieval
dpo2k.close()
