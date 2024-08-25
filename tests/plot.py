import matplotlib.pyplot as plt
import json

# Open the JSON file containing the collected data
jsonFile = open("tests/signals.json")

# Load the JSON data into a Python dictionary
channels = json.load(jsonFile)

# Iterate through each channel in the dictionary
for i in range(len(channels)):

    # Check if the channel has any data
    if not channels[f"Ch{i}"]:
        pass
    else:
        # Create a new figure for the channel
        plt.figure(i)

        # Set the title of the figure to the channel number
        plt.title("Channel " + str(i))

        # Plot the data from the channel
        plt.plot(channels[f"Ch{i}"])

# Display the plots
plt.show()

# # Uncomment the following lines to plot specific channels
# # plt.figure(0)
# # plt.title("Channel " + str(0))
# # plt.plot(channels[f"Ch{0}"])
# # plt.figure(15)
# # plt.title("Channel " + str(15))
# # plt.plot(channels[f"Ch{15}"])

# # Display the plots
# # plt.show()

# # Uncomment the following line to print the data from a specific channel
# # print(channels[f"Ch{1}"])
# # print(channels[0])

# # Uncomment the following lines to create a subplot for each channel
# # fig, axs = plt.subplots(16)
# # for i in range(len(channels)):
# #     if not channels[f"Ch{i}"]:
# #         pass
# #     else:
# #         axs[i].set_title("Channel " + str(i))
# #         axs[i].plot(channels[f"Ch{i}"])
# # plt.show()
