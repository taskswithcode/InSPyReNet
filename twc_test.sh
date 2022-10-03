Usage="Specify <input image/video file> [<output_dir>] [blur/map]"
inp=${1?$Usage}
output=${2-"results"}
mask_type=${3-"blur"}
python run/Inference.py --config configs/InSPyReNet_SwinB.yaml --source $inp  --dest $output --type $mask_type  --verbose

#python run/Inference.py --config configs/InSPyReNet_SwinB.yaml --source twc_samples/sample3.png --dest results --type map --gpu --jit --verbose
#python run/Inference.py --config configs/InSPyReNet_SwinB.yaml --source twc_samples/sample4.png --dest results --type map  --verbose
#python run/Inference.py --config configs/InSPyReNet_SwinB.yaml --source twc_samples/sample5.png --dest results --type map  --verbose
#python run/Inference.py --config configs/InSPyReNet_SwinB.yaml --source twc_samples/dog_running.mp4 --dest video_results --type map  --verbose
#python run/Inference.py --config configs/InSPyReNet_SwinB.yaml --source twc_samples/dog_running.mp4 --dest video_results2 --type blur  --verbose
#python run/Inference.py --config configs/InSPyReNet_SwinB.yaml --source twc_samples/sample1.png --dest results2 --type blur  --verbose
#python run/Inference.py --config configs/InSPyReNet_SwinB.yaml --source twc_samples/sample2.png --dest results2 --type blur  --verbose
#python run/Inference.py --config configs/InSPyReNet_SwinB.yaml --source twc_samples/sample3.png --dest results2 --type blur  --verbose
#python run/Inference.py --config configs/InSPyReNet_SwinB.yaml --source twc_samples/sample4.png --dest results2 --type blur  --verbose
#python run/Inference.py --config configs/InSPyReNet_SwinB.yaml --source twc_samples/sample5.png --dest results2 --type blur  --verbose
