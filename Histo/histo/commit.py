def main():
    import sys
    folder = sys.argv[1]
    commit(folder)

def commit(folder):
    advancedCommit(folder)

def advancedCommit(folder, time=None, name=None, compression=True):
    with connect() as conn:
        conn.writeObject('Commit')
        p = {'Folder': folder,
             'Name': name,
             'Compression': compression,
             'Time': time}
        conn.writeObject(p)
        assert conn.readObject() == 'OK'

def connect():
    from picklestream import PickleClient
    return PickleClient(('127.0.0.1', 3750))

if __name__ == '__main__':
    main()