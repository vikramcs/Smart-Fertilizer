'''
####################################################################################################################################
FERTILIZER PREDICTION
Framework : Tensorflow
DL tools : Deep Neural Net
Code developed by : vikram kumar
####################################################################################################################################
'''
import tensorflow as tf 
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

'''
input > weight > hidden layer 1(act fn) > weights > hidden layer 2(act fn) > weight
> output layer
compare output to intended output > cost function(cross entropy)
 optimization function(optimizer) > minimizer cost (AdamOptimizer....SGD(stochastic gradient decent, AdaGrad)
backpropagation
feed forward + backprop = epoch
'''

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
xin = tf.placeholder('float',[None, 9])
yin = tf.placeholder('float')
t1,t2,t3,t4,t5,t6,t7,t8,t9=0,0,0,0,0,0,0,0,0

# read dataset

df = pd.read_csv('FertPredictDataset4.csv') 
x = df.drop('class',1) 
y = df['class']


from numpy import array
from numpy import argmax
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder

# define example

values = array(y)

# integer encode

label_encoder = LabelEncoder()
integer_encoded = label_encoder.fit_transform(values)

# binary encode

onehot_encoder = OneHotEncoder(sparse=False)
integer_encoded = integer_encoded.reshape(len(integer_encoded), 1)
y = onehot_encoder.fit_transform(integer_encoded)

x_train, x_test,y_train,y_test = train_test_split(x,y,test_size=0.3, shuffle=False) 

# neural network parameters

n_nodes_hl1 = 500
n_nodes_hl2 = 500
n_nodes_hl3 = 500
n_classes = 4
batch_size = 100
data_index = 0


# generate batch 

def generate_batch(batch_size):
    global data_index
    batch = np.ndarray(shape=(batch_size, 9), dtype=np.float32)  #the same shapes as train data
    labels = np.ndarray(shape=(batch_size, 4), dtype=np.float32)
    for i in range(batch_size):
        batch[i] = np.array(x_train)[data_index]
        labels[i] = y_train[data_index]
        data_index = (data_index + 1) % len(x_train)
    return batch, labels

# define the model

def neural_network_model(data):
	# input data* weights + bias 
	hidden_1_layer = {'weights': tf.Variable(tf.random_normal([9, n_nodes_hl1])),
						'biases': tf.Variable(tf.random_normal([n_nodes_hl1]))}

	hidden_2_layer = {'weights': tf.Variable(tf.random_normal([n_nodes_hl1, n_nodes_hl2])),
						'biases': tf.Variable(tf.random_normal([n_nodes_hl2]))}

	hidden_3_layer = {'weights': tf.Variable(tf.random_normal([n_nodes_hl2, n_nodes_hl3])),
						'biases': tf.Variable(tf.random_normal([n_nodes_hl3]))}

	output_layer = {'weights': tf.Variable(tf.random_normal([n_nodes_hl3, n_classes])),
						'biases': tf.Variable(tf.random_normal([n_classes]))}

	l1 = tf.add(tf.matmul(data, hidden_1_layer['weights']) , hidden_1_layer['biases'])
	l1 = tf.nn.relu(l1) # rectified linear --> activation function

	l2 = tf.add(tf.matmul(l1, hidden_2_layer['weights']) , hidden_2_layer['biases'])
	l2 = tf.nn.relu(l2)

	l3 = tf.add(tf.matmul(l2, hidden_3_layer['weights']) , hidden_3_layer['biases'])
	l3 = tf.nn.relu(l3)

	output = tf.matmul(l3, output_layer['weights']) + output_layer['biases']

	return output 

# train neural network

def train_neural_network(xin,l): 
	prediction = neural_network_model(xin) 
	

	with tf.name_scope('Cost') :
		cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=yin,logits=prediction))
		optimizer =  tf.train.AdamOptimizer(0.0002).minimize(cost)  #learning rate = 0.001
		
	
	tf.summary.scalar("Cost", cost)

	hm_epochs = 20 
	eploss = []
	cost_n = []
	with tf.Session() as sess: 
		writer = tf.summary.FileWriter("./logs/FertPrediction", sess.graph) # for 0.8
			
		sess.run(tf.global_variables_initializer()) 

		correct = tf.equal(tf.argmax(prediction,1), tf.argmax(yin,1)) 
		accuracy = tf.reduce_mean(tf.cast(correct,'float'))
		
		merged = tf.summary.merge_all()
		for epoch in range(hm_epochs): 
			epoch_loss = 0
			for _ in range(int(len(x_train)/batch_size)) : 
				epoch_x,epoch_y = generate_batch(batch_size) 
				_,c,summary = sess.run([optimizer,cost,merged], feed_dict={xin:epoch_x, yin:epoch_y}) 
				cost_n.append(c)
				epoch_loss += c

			writer.add_summary(summary, epoch)
			print('Epoch',epoch,'completed out of', hm_epochs, 'loss: ', epoch_loss)
			eploss.append(epoch_loss)	 

		a = float(accuracy.eval({xin:x_test, yin:y_test}))
		print('accuracy: ', a*100,'%') 

		# feed_dict = {x: [0.05, 0.01, 0.01, 0.02, 0.01, 0.03, 0.02, 0.01, 0.01]}
		# classification = tf.run(y, feed_dict)
		# print(classification)
		# prediction=tf.argmax(y,1)
		# print(eploss)

# predict an output
		
		predict = tf.argmax(prediction,1)
		example = np.array(l)
		example = example.reshape(-1,len(example))
		predict = predict.eval({xin:example})
		print("prediction : Fertilizer", label_encoder.inverse_transform(predict))
		return "Fertilizer"+str(label_encoder.inverse_transform(predict)) 
		
# plot epoch_loss vs no. of epochs
		plt.figure()
		plt.plot(eploss)
		plt.title('Loss vs Number of epochs')
		plt.ylabel('Loss')
		plt.xlabel('Number of epochs')
		plt.show()

