import pickle

# * the pickled STORAGE dictionaries should store 

def get_file(fname):
    try:
        return pickle.load( open( fname, "rb" ) )
    except:
        return {} # return a blank dict if the file doesn't exist

def save_file(f, fname):
    pickle.dump( f , open( fname, "wb" ) )
    print( f"{fname} stored.")
    return True