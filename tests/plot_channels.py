import matplotlib.pyplot as plt
import json

with open("tests/signals.json", "r") as json_file:
    channels = json.load(json_file)

# Filter channels that contain data and sort them numerically
active_channels = sorted([k for k, v in channels.items() if v], key=lambda x: int(x[2:]))
num_plots = len(active_channels)

# Create a single figure with N subplots (stacked vertically)
if num_plots > 0:
    fig, axes = plt.subplots(num_plots, 1, sharex=True, figsize=(10, 2 * num_plots))
    fig.suptitle("Channels View Test")

    if num_plots == 1:
        axes = [axes]

    for i, channel_name in enumerate(active_channels):
        data = channels[channel_name]

        axes[i].plot(data, label=channel_name, color='tab:blue')
        axes[i].set_ylabel("Amp")
        axes[i].set_title(channel_name, loc='left', fontsize=10)
        axes[i].legend(loc="upper right")
        axes[i].grid(True, alpha=0.3)

    plt.xlabel("Samples")
    plt.tight_layout()
    plt.show()
else:
    print("No channels with data were found.")
