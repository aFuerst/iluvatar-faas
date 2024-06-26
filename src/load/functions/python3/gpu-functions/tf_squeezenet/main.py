msg = "good"
import traceback
session = None
try:
    import os, sys
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    os.environ['AUTOGRAPH_VERBOSITY'] = '2'
    # sys.stdout = open(os.devnull, 'w')
    # sys.stderr = open(os.devnull, 'w')
    import numpy as np
    import uuid
    from time import time
    import logging

    # import boto3
    import tensorflow.compat.v1 as tf

    from tensorflow.compat.v1 import ConfigProto
    from tensorflow.compat.v1 import InteractiveSession

    config = ConfigProto()
    config.gpu_options.allow_growth = True
    config.gpu_options.per_process_gpu_memory_fraction = 0.15
    session = InteractiveSession(config=config)

    from tensorflow.keras.preprocessing import image
    from tensorflow.keras.applications.resnet50 import preprocess_input, decode_predictions
    from tensorflow.keras.utils import get_file
    from squeezenet import SqueezeNet
    tf.disable_v2_behavior()
    # tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
    # tf.get_logger().setLevel('ERROR')
    # tf.get_logger().setLevel(logging.ERROR)
    # logging.getLogger("tensorflow").setLevel(logging.WARNING)
    # tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.WARNING)
    tf.get_logger().setLevel('WARNING')
    tf.get_logger().setLevel(logging.WARNING)
    logging.getLogger("tensorflow").setLevel(logging.WARNING)
    tf.keras.utils.disable_interactive_logging()

    # s3_client = boto3.client('s3')

except Exception as e:
    msg = traceback.format_exc()

tmp = "/tmp/"
cold = True

def predict(img_local_path):
    start = time()
    # config = tf.ConfigProto(device_count={"CPU": 1}, 
    #             inter_op_parallelism_threads = 1, 
    #             intra_op_parallelism_threads = 1)

    # with tf.Session(config=config) as sess:
      # with tf.device('/cpu:0'):
    model = SqueezeNet(weights='imagenet')
    img = image.load_img(img_local_path, target_size=(227, 227))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    preds = model.predict(x)
    res = decode_predictions(preds)
    end = time()
    latency = end - start
    return latency, res, start, end


def main(args):
    global cold
    start = time()
    was_cold = cold
    cold = False
    # return {"body": { "latency":-1, "msg":msg, "cold":was_cold }}
    try:
        input_bucket = args.get("input_bucket", 1)
        object_key = args.get("object_key", 1)

        model_object_key = args.get("model_object_key", 1) # example : squeezenet_weights_tf_dim_ordering_tf_kernels.h5
        model_bucket = args.get("model_bucket", 1)

        # download_path = tmp + '{}{}'.format(uuid.uuid4(), object_key)
        download_path = get_file('{}{}'.format(uuid.uuid4(), object_key),
                                    "https://github.com/kmu-bigdata/serverless-faas-workbench/raw/master/dataset/image/animal-dog.jpg",
                                    cache_dir='/tmp/')
        # s3_client.download_file(input_bucket, object_key, download_path)

        model_path = tmp + '{}{}'.format(uuid.uuid4(), model_object_key)
        # s3_client.download_file(model_bucket, model_object_key, model_path)
            
        infer_latency, result, infer_start, infer_end = predict(download_path)
            
        _tmp_dic = {x[1]: {'N': str(x[2])} for x in result[0]}
        end = time()
        return {"body": { "latency":end-start, "msg":msg, "cold":was_cold, "start":start, "end":end, "infer_latency":infer_latency }}
    except Exception as e:
        err = "whelp"
        try:
            err = traceback.format_exc()
        except Exception as fug:
            err = str(fug)
        return {"body": { "cust_error":msg, "thing":err, "cold":was_cold }}