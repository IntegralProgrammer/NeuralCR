import tensorflow as tf
import numpy as np
import reader
import phraseConfig
import phrase_model

class NeuralPhraseAnnotator:
	def __get_top_concepts(self, indecies_querry, res_querry, count):
		tmp_res = []
		if self.compWithPhrases:
			for i in indecies_querry:
				res_item = (self.rd.concepts[self.rd.name2conceptid.values()[i]],res_querry[i])
				if res_item[0] not in [x[0] for x in tmp_res]:
					tmp_res.append(res_item)
				if len(tmp_res)>=count:
					break
		else:
			for i in indecies_querry:
				tmp_res.append((self.rd.concepts[i],res_querry[i]))
				if len(tmp_res)>=count:
					break
		return tmp_res

	def get_hp_id(self, querry, count=1):
		inp = self.rd.create_test_sample(querry)
		querry_dict = {self.model.input_sequence : inp['seq'], self.model.input_sequence_lengths: inp['seq_len']}
		res_querry = self.sess.run(self.querry_distances, feed_dict = querry_dict)

		results=[]
		for s in range(len(querry)):
			indecies_querry = np.argsort(res_querry[s,:])
			results.append(self.__get_top_concepts(indecies_querry, res_querry[s,:], count))

		return results

	def __init__(self, model, rd ,sess, compWithPhrases = False):
		self.model=model
		self.rd = rd
		self.sess = sess
		self.compWithPhrases = compWithPhrases

		if self.compWithPhrases:
			inp = self.rd.create_test_sample(self.rd.name2conceptid.keys())
			querry_dict = {self.model.input_sequence : inp['seq'], self.model.input_sequence_lengths: inp['seq_len']}
			res_querry = self.sess.run(self.model.gru_state, feed_dict = querry_dict)
			ref_vecs = tf.Variable(res_querry, False)
			sess.run(tf.assign(ref_vecs, res_querry))
			self.querry_distances = self.model.euclid_dis_cartesian(ref_vecs, self.model.gru_state)
		else:
			self.querry_distances = self.model.euclid_dis_cartesian(self.model.get_HPO_embedding(), self.model.gru_state)

def create_annotator(repdir, datadir=None, compWithPhrases = False):
	if datadir is None:
		datadir = repdir
	oboFile = open(datadir+"/hp.obo")
	vectorFile = open(datadir+"/vectors.txt")

	rd = reader.Reader(oboFile, vectorFile)
	config = phraseConfig.Config
	config.update_with_reader(rd)

	model = phrase_model.NCRModel(config)

	sess = tf.Session()
	saver = tf.train.Saver()
	saver.restore(sess, repdir + '/training.ckpt')

	return NeuralPhraseAnnotator(model, rd, sess, compWithPhrases)

