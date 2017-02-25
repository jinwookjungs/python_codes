'''
    File name      : check_compressed.py
    Author         : Jinwook Jung
    Created on     : Fri Feb 24 20:16:50 2017
    Last modified  : 2017-02-24 20:16:50
    Python version : 
'''

def get_file_type(file_name):
    signature_dict = { "\x1f\x8b\x08" : "gz",
                       "\x42\x5a\x68" : "bz2" }
   
    with open(file_name) as f:
        file_head = f.read(3)

    try:
        return signature_dict[file_head]
    
    except KeyError:
        return None


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser("Check it whether compressed or not.")
    parser.add_argument('-i', action='store', dest='src', required=True)
    opt = parser.parse_args()

    print(get_file_type(opt.src))
