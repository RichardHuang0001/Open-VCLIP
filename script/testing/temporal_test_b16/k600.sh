ROOT=/mnt/SSD8T/home/huangwei/projects/Open-VCLIP
CKPT=/mnt/SSD8T/home/huangwei/projects/Open-VCLIP/checkpoints
OUT_DIR=$CKPT/testing

K600_split=k600_split1

LOAD_CKPT_FILE=/mnt/SSD8T/home/huangwei/projects/Open-VCLIP/checkpoints/openvclip-b16/swa_2_22.pth
PATCHING_RATIO=0.5

# MODEL.TEMPORAL_MODELING_TYPE 'expand_temporal_view'  \
cd $ROOT
# MODEL.TEMPORAL_MODELING_TYPE 'expand_temporal_view'
python -W ignore -u tools/run_net.py \
    --cfg configs/Kinetics/TemporalCLIP_vitb16_8x16_STAdapter.yaml \
    --opts DATA.PATH_TO_DATA_DIR $ROOT/zs_label_db/$K600_split \
    DATA.PATH_PREFIX ../FROSTER/data/k600 \
    DATA.PATH_LABEL_SEPARATOR , \
    DATA.INDEX_LABEL_MAPPING_FILE $ROOT/zs_label_db/$K600_split/k600-openset-index2cls.json \
    TRAIN.ENABLE False \
    OUTPUT_DIR $OUT_DIR \
    TEST.BATCH_SIZE 60 \
    NUM_GPUS 1 \
    DATA.DECODING_BACKEND "pyav" \
    MODEL.NUM_CLASSES 160 \
    TEST.CUSTOM_LOAD True \
    TEST.CUSTOM_LOAD_FILE $LOAD_CKPT_FILE \
    TEST.SAVE_RESULTS_PATH temp.pyth \
    TEST.NUM_ENSEMBLE_VIEWS 3 \
    TEST.NUM_SPATIAL_CROPS 1 \
    TEST.PATCHING_MODEL True \
    TEST.PATCHING_RATIO $PATCHING_RATIO \
    TEST.CLIP_ORI_PATH ~/.cache/clip/ViT-B-16.pt \
