article_vector = []
def search_in_vector(s):
	with open('../vectors.bin','r') as f:
        	for data in f:
                	key = data.split()[0]
			value = data.split()[1:]
                	#print key
			if s == key:
				#print '!!',key,s
				article_vector.append(value)
				#print article_vector
if __name__ == "__main__":
	vector = []
	f2 = open('Preprocess.txt','w')
	with open('AllNew.txt','r') as f:
		for data in f:
			f2.write(data.replace(',',' '))	
	#print len(article_vector.split(','))
	f2.close()
