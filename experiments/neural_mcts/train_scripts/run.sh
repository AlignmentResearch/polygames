#!/bin/bash
echo "hi training, we got to the bash script" 
cd /polygames
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
git remote set-url origin https://github.com/AlignmentResearch/polygames.git
git branch --set-upstream-to=origin/run_pure_mcts_experiments run_pure_mcts_experiments
git checkout run_pure_mcts_experiments
git pull
python /shared/polygames-parent/polygames-scripts/run_like.py /shared/polygames-parent/polygames-data/hex5pie/fb_checkpoints/Hex5pie_90_2019-10-02_ResConvConvLogitModel_epoch40166_job18307537_45_9ad68514.pt.gz /shared/polygames-parent/experiments/hex3_from_scratch_their_settings num_game=16 saving_period=10 game_name=Hex3
