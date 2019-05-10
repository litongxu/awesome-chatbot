#!/bin/bash

## typical configurations

TEST_4="--mode=long --basename=test_s2s_movie_openvocab_d300_v15000_len15 --load-babi --lr=0.001 --dropout=0.5 --load-recurrent --units=300 --record-loss --multiplier=0.5 --length=15 --no-vocab "
TEST_5="--mode=long --basename=test_s2s_new_attn_d300_v15000_length15_dropout050 --load-babi --lr=0.001 --dropout=0.5 --load-recurrent --units=300 --record-loss --multiplier=0.5 --length=15 --skip-unk --hide-unk"

LAUNCH=launch

if [ ! -f ${LAUNCH} ]; then


echo "quit -- no 'launch' file present."
exit

fi
export CHATBOT_MODE="sequence"

cd bot
python3.6 game.py ${TEST_5} # 2> /dev/null

## this file must be hard coded for any model you want to run
