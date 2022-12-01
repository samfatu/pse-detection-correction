import re


def count_flashes(flashes_lighter, flashes_darker, frame_rate):
    # this may be over-counting slightly
    flashes_lighter[0], flashes_darker[0] = 0, 0
    channel1, channel2 = flashes_lighter[-(frame_rate - 1):], flashes_darker[-(frame_rate - 1):]
    both_channels = ''
    for i in range(len(channel1)):
        if channel1[i] and channel2[i]:
            both_channels += 'X'
        elif channel1[i]:
            both_channels += '1'
        elif channel2[i]:
            both_channels += '2'
    both_channels = re.sub('1+', '1', both_channels)
    both_channels = re.sub('2+', '2', both_channels)
    count = len(both_channels)
    return count
