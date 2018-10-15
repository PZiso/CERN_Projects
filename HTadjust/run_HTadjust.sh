#!/bin/bash



ssh -f ln3op@cwe-513-vol262 \
"cd /user/ln3op/GHOST/HTadjust/src/ && source /acc"\
"/local/share/python/L866/setup.sh && nohup python /user/ln3op/GHOST/"\
"HTadjust/src/HTadjust.py > garbage.in 2> garbage.out < /dev/null &"

# Note the Line continuations before messing with the commands ;) 



# run the module in the background. Remove & for shell print.

# # source /acc/local/share/python/L867/setup.sh # Use Python 3 Officialy supported by CO (Attention: The L867 subdir depends on the CPU of the running machine. Try L866 if this doesn't work.)

# # # Send everything to /dev/null so the program gets executed in the background-Use nohuup for no hungup