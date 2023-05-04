import matplotlib.pyplot as plt
import json

jsonFile = open("signals.json")
channels = json.load(jsonFile)

for i in range(len(channels)):

    if not channels[f"Ch{i}"]:
        pass
    else:
        plt.figure(i)
        plt.title("Channel " + str(i))
        plt.plot(channels[f"Ch{i}"])

# plt.figure(0)
# plt.title("Channel " + str(0))
# plt.plot(channels[f"Ch{0}"])
# plt.figure(15)
# plt.title("Channel " + str(15))
# plt.plot(channels[f"Ch{15}"])

plt.show()

# print(channels[f"Ch{1}"])
# print(channels[0])

# fig, axs = plt.subplots(16)
# for i in range(len(channels)):

#     if not channels[f"Ch{i}"]:
#         pass
#     else:
#         axs[i].set_title("Channel " + str(i))
#         axs[i].plot(channels[f"Ch{i}"])
# plt.show()
