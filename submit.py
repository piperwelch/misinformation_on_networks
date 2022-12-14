import os 
for gen in [1, 2, 3, 4, 5]:
    for mis_source in [0.75]:
        for inf_source in [0.25]:
            for targeted_reduction in [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
                os.system('sbatch submit.sh {} {} {} {}'.format(gen, mis_source, inf_source, targeted_reduction))