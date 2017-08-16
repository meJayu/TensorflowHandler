import tensorflow as tf
import numpy as np
import time
import os
from datetime import timedelta

IMAGE_DIM = 32#Num of rows / columns
IMAGE_DEPTH = 3#Number of channels
IMG_FLAT = IMAGE_DIM * IMAGE_DIM *IMAGE_DEPTH
IMG_SIZE = (32,32,3)#Image size as a tuple
global NUM_CLASSES 
NUM_CLASSES = 10
global BATCH_SIZE
BATCH_SIZE = 64
#model stored at
save_path = '/home/jay/Deep_Structures/TF/my_test_model'
#log_dir
log_dir = '/home/jay/Deep_Structures/Summary/'

def model(_Xs_images,_Ys_labels,keep_prob):
    
    with tf.name_scope('reshape'):    
        _Xs = tf.reshape(_Xs_images, shape=[-1, IMAGE_DIM,IMAGE_DIM,IMAGE_DEPTH]) 
        _Ys = tf.one_hot(_Ys_labels,depth=NUM_CLASSES)
    
    with tf.name_scope('conv_1') as scope:
        
        conv_weight1 = tf.get_variable(name = 'conv_weights1',shape=[3,3,3,16],initializer=tf.contrib.layers.variance_scaling_initializer(factor=2.0,
                                                                                                       mode='FAN_IN',
                                                                                                       uniform=False,
                                                                                                       seed=None,
                                                                                                       dtype=tf.float32))
        conv = tf.nn.conv2d(_Xs,conv_weight1,\
                                strides=[1,1,1,1],\
                                padding='SAME') 
        biases = tf.Variable(tf.constant(0.01,dtype=tf.float32,shape=[16],name='bias_1'))
        bias = tf.nn.bias_add(conv,biases)        
        conv1 = tf.nn.relu(bias,name=scope)
        pool1 = tf.nn.max_pool(conv1,ksize=[1,3,3,1],\
                               strides=[1,2,2,1],\
                               name='pool_1',padding='SAME')

    with tf.name_scope('conv_2') as scope:
        
        conv_weight2 = tf.get_variable(name = 'conv_weights2',shape=[3,3,16,32],initializer=tf.contrib.layers.variance_scaling_initializer(factor=2.0,
                                                                                                       mode='FAN_IN',
                                                                                                       uniform=False,
                                                                                                       seed=None,
                                                                                                       dtype=tf.float32))
        conv = tf.nn.conv2d(pool1,conv_weight2,\
                             strides=[1,1,1,1],\
                             padding='SAME') 
        biases = tf.Variable(tf.constant(0.01,dtype=tf.float32,shape=[32],name='bias_2'))
        bias = tf.nn.bias_add(conv,biases)        
        conv2 = tf.nn.relu(bias,name=scope)
        pool2 = tf.nn.max_pool(conv2,ksize=[1,3,3,1],\
                             strides=[1,2,2,1],\
                             name='pool_2',padding='SAME') 
                        
    activations = tf.contrib.layers.flatten(pool2)

    with tf.name_scope('fc_1') as scope:
                              
         fc_weight1 = tf.get_variable(name = 'fc_weights1',shape=[2048,64],initializer=tf.contrib.layers.variance_scaling_initializer(factor=2.0,
                                                                                                       mode='FAN_IN',
                                                                                                       uniform=False,
                                                                                                       seed=None,
                                                                                                       dtype=tf.float32))
        
         fc1 = tf.matmul(activations,fc_weight1) 
         biases1 = tf.Variable(tf.constant(0.01,dtype=tf.float32,shape=[64],name='fc_b1'))
         bias = tf.nn.bias_add(fc1,biases1)        
         fc_layer1 = tf.nn.relu(bias,name=scope)
         
    with tf.name_scope('dropout'):
        
        tf.summary.scalar('dropout_keep_probability', keep_prob)
        fc_layer1_dropped = tf.nn.dropout(fc_layer1, keep_prob)

    with tf.name_scope('fc_2') as scope:
         fc_weight2 = tf.get_variable(name = 'fc_weights2',shape=[64,10],initializer=tf.contrib.layers.variance_scaling_initializer(factor=2.0,
                                                                                                       mode='FAN_IN',
                                                                                                       uniform=False,
                                                                                                       seed=None,
                                                                                                       dtype=tf.float32))
        
         fc2 = tf.matmul(fc_layer1_dropped,fc_weight2) 
         biases2 = tf.Variable(tf.constant(0.01,dtype=tf.float32,shape=[10],name='fc_b2'))
         bias = tf.nn.bias_add(fc2,biases2)        
         fc_layer2 = tf.nn.relu(bias,name=scope)
    
    
    #cross_entropy loss
    with tf.name_scope('cross_entropy_loss'):
         cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=_Ys,
                                                            logits = fc_layer2))
    
    #prediction    
    with tf.name_scope('y_pred'):
        _y_pred = tf.cast(tf.argmax(fc_layer2,1),dtype=tf.float32)     
    
    return _y_pred,cross_entropy,_Ys   
    


def optimize(iterations,IMG_FLAT=IMG_FLAT,\
                            IMAGE_DIM=IMAGE_DIM,\
                            IMAGE_DEPTH=IMAGE_DEPTH,\
                            NUM_CLASSES=NUM_CLASSES,k=1):
         sess = tf.InteractiveSession()                       
         #to feed the network
         with tf.name_scope('Xs'):
             _Xs_images = tf.placeholder(tf.float32,shape=[None,IMG_FLAT],name='images')
            
         with tf.name_scope('Ys'):    
             _Ys_labels = tf.placeholder(tf.int32,shape=[None],name='labels')
             
         keep_prob = tf.placeholder(tf.float32)    

         with tf.name_scope('Model'):
             #input the image and get the softmax output 
             _y_pred,cross_entropy,_Ys = model(_Xs_images,_Ys_labels,keep_prob)            
         
         #optimization   
         with tf.name_scope('Optimization'):                                                   
             train_net = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy) 
         
         with tf.name_scope('Accuracy'):
             _y = tf.cast(tf.argmax(_Ys,1),dtype=tf.float32)
             with tf.name_scope('Correct_prediction'):
                 #finding the accuracy         
                 correct_prediction = tf.equal(_y_pred,_y)
             with tf.name_scope('Accuracy'):
                 accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
         
         tf.summary.scalar('accuracy', accuracy)
         # Create a summary to monitor cost tensor
         tf.summary.scalar("loss", cross_entropy)
         # Create a summary to monitor accuracy tensor
         _op_summary =tf.summary.merge_all()
         
         
         ### SAVE PARAMETERS
         saver = tf.train.Saver()
         save_dir = save_path #directory name

         
         if True:
             summary_writer = tf.summary.FileWriter(log_dir + '/train', sess.graph)
             sess.run(tf.initialize_all_variables())
             
             
             start_time = time.time()
             for i in range(1,iterations):
                 
                 images,labels = get_data(batch=i%4,isTraining=True)
                 
                 for j in range(images.shape[0] / BATCH_SIZE + 1):
                     if k%5 == 0:
                         _trainXs = images[j*BATCH_SIZE:(j+1)*BATCH_SIZE,:]
                         _trainYs= labels[j*BATCH_SIZE:(j+1)*BATCH_SIZE]
                    
                         feed_dict={_Xs_images:_trainXs,_Ys_labels:_trainYs,keep_prob:0.5}
                    
                         run_options = tf.RunOptions(trace_level=tf.RunOptions.FULL_TRACE)
                         run_metadata = tf.RunMetadata()
                    
                         summary,_,loss= sess.run([_op_summary,train_net,cross_entropy],feed_dict,\
                                                        options=run_options,\
                                                        run_metadata=run_metadata)
                         summary_writer.add_run_metadata(run_metadata, 'step%d' % k)
                         summary_writer.add_summary(summary, k)
                         print('Adding run metadata for', k)
                         k += 1
                     else:#training mini-batch
                         
                         _trainXs = images[j*BATCH_SIZE:(j+1)*BATCH_SIZE,:]
                         _trainYs= labels[j*BATCH_SIZE:(j+1)*BATCH_SIZE]
                    
                         feed_dict={_Xs_images:_trainXs,_Ys_labels:_trainYs,keep_prob:0.5}
                    
                         summary,_,loss= sess.run([_op_summary,train_net,cross_entropy],feed_dict) 
                         print loss                            
                         summary_writer.add_summary(summary, k)
                         k += 1
             
             summary_writer.close()       

             saver.save(sess = sess,save_path=save_dir)
             print("Model stored in file: %s" % save_dir)  
             
         end_time = time.time()
         
         # Difference between start and end-times.
         time_dif = end_time - start_time

         # Print the time-usage.
         print("Time usage: " + str(timedelta(seconds=int(round(time_dif)))))

def inference():
    """
    predict on a test set
    """
    #to feed the network
    _Xs_images = tf.placeholder(tf.float32,shape=[None,IMG_FLAT],name='images')
    _Xs = tf.reshape(_Xs_images, shape=[-1, IMAGE_DIM,IMAGE_DIM,IMAGE_DEPTH])
    _Ys_labels = tf.placeholder(tf.int32,shape=[None],name='labels')
    _Ys = tf.one_hot(_Ys_labels,depth=NUM_CLASSES)
    #input the image and get the softmax output         
    fc_layer2 = model(_Xs)         
    
    # predicted output and actual output
    _y_pred = tf.cast(tf.argmax(fc_layer2,1),dtype=tf.float32)
    _y = tf.cast(tf.argmax(_Ys,1),dtype=tf.float32)
    #finding the accuracy         
    correct_prediction = tf.equal(_y_pred,_y)
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
         
    with tf.Session() as session:
        session.run(tf.initialize_all_variables())
        saver = tf.train.import_meta_graph('/home/jay/Deep_Structures/TF/my_test_model.meta')
        saver.restore(session,'/home/jay/Deep_Structures/TF/my_test_model')
        all_vars = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES)
        print all_vars
        #session.run(tf.initialize_all_variables())
        #ckpt = tf.train.get_checkpoint_state(os.path.dirname('/home/jay/Deep Network Structures/Tensorflow/TrainedModels/'))
        #if ckpt and ckpt.model_checkpoint_path:
        #    tf.train.Saver.restore(session, ckpt.model_checkpoint_path)
        _batch_acc = []
        images,labels = get_data(isTraining=False)
        for j in range(images.shape[0] / BATCH_SIZE + 1):
        
            _trainXs = images[j*BATCH_SIZE:(j+1)*BATCH_SIZE,:]
            _trainYs= labels[j*BATCH_SIZE:(j+1)*BATCH_SIZE]
                    
            feed_dict={_Xs_images:_trainXs,_Ys_labels:_trainYs}
            _miniAcc = session.run(accuracy,feed_dict)
            _batch_acc.append(_miniAcc)        
        msg = "Accuracy on Test-Set: {0:.1%}"
        print(msg.format(sum(_batch_acc)/float(len(_batch_acc))))
    
def get_data(batch=0,isTraining=True):

    ROOT_PATH = "/home/jay/Deep_Structures/cifar-10-python"
    #for training and testing separately
    if isTraining:
        path = os.path.join(ROOT_PATH,"train_batches/")
        file_names = [f for f in os.listdir(path)]
        batch = unpickle(os.path.join(path,file_names[batch]))
        images,labels = np.array(batch['data'],np.float32),batch['labels']  
    else:
        path = os.path.join(ROOT_PATH,"test_batches/")
        file_names = [f for f in os.listdir(path)]
        batch = unpickle(os.path.join(path,file_names[0]))
        images,labels = np.array(batch['data'],np.float32),batch['labels']
    #normalize the data
    images,labels = prepare_input(data=images,labels=labels)
    
    return images,np.array(labels,dtype=np.int32)

def prepare_input(data=None, labels=None):
    
    #do mean normaization across all samples
    mu = np.mean(data, axis=0)
    mu = mu.reshape(1,-1)
    sigma = np.std(data, axis=0)
    sigma = sigma.reshape(1, -1)
    data = data - mu
    data = data / sigma
    return data,labels
    
def unpickle(file):
    import cPickle
    fo = open(file, 'rb')
    dict = cPickle.load(fo)
    fo.close()
    return dict
                                