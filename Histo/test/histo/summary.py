def main():
    initLogger()
    #testSimplify()
    testSummary()

def initLogger():
    import logging
    logging.basicConfig(format='%(asctime)s %(message)s', level=0)

def testSimplify():
    summary = [[1,5,9,5,[1,2,3,4,2,4,3],2,5,[1,2,5,6,2,3]],2,[5,[9,8,5,2,3,4],7,8],4]
    from histo.server.summary import simplify
    summary = simplify(summary, 10)
    from pprint import pprint
    pprint(summary, indent=4, width=1)

def testSummary():
    #root = 'D:\\ed'
    root = r'C:\Users\pc\appdata\local\temp\tmp3of00x.histo\Visitor'
    from histo.server.summary import generateSummary, simplify
    summary = generateSummary('TestSummary', root)
    from pprint import pprint
    pprint(simplify(summary, 1000), indent=4, width=1)
    
if __name__ == '__main__':
    main()