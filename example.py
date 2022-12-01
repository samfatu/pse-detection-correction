import time

from PhotosensitivitySafetyEngine.guidelines.w3c import *

THRESHOLD = 3

start = time.time()
result = w3c_guideline.analyse_file('pokemon.mp4', show_live_chart=False, show_dsp=False, show_analysis=False)
end = time.time()

is_general = False
general_flashes = []
red_flashes = []
for i, (general, red) in enumerate(zip(result["General Flashes"], result["Red Flashes"])):
  print(i, (general, red))
  pass

print("\nTIME : ", end="")
print(end - start)
