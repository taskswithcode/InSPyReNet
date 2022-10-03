#apt-get update
#apt-get install ffmpeg libsm6 libxext6  -y
mkdir -p data/backbone_ckpt
cp twc_models/latest.pth data/backbone_ckpt/swin_base_patch4_window12_384_22kto1k.pth
