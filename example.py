import time

from PhotosensitivitySafetyEngine.guidelines.w3c import *

start = time.time()
safe, result = w3c_guideline.analyse_file('pokemon.mp4', show_live_chart=False, show_dsp=False, show_analysis=True)
end = time.time()

print("\nTIME : ", end="")
print(end - start)
