import main
import unittest
from io import StringIO
import pandas as pd

def read2str(filename):

    with open(filename, 'r') as f:
        
        thisfile=f.read()

    return thisfile


class TestNotificationBot(unittest.TestCase):

    testfile_id = "1mmlQc6fOPfE044YtShJUIPTz6bODJwHo_rWXdBmqHLQ"
    def test_pull(self):

        returned_string = main.pull_schedule(self.testfile_id)
        original_string = read2str("test_pull.txt")
        collist_ret = pd.read_csv(StringIO(returned_string),sep='\t',comment="#").columns.tolist()
        collist_orig = pd.read_csv(StringIO(original_string),sep='\t',comment="#").columns.tolist()

        self.assertEqual( collist_orig, collist_ret )


    def test_parser(self):

        parsed_results = main.parse_tsv(read2str("test_pull.txt"), speaker_col=2, topics_col=3)
        self.assertEqual( parsed_results[0], "testspeaker4")


    def test_message(self):
        
        self.assertEqual(main.create_message(["testspeaker4", ["option10","option11","option12"]]) ,read2str("test_message.txt"))



if __name__ == '__main__':
    unittest.main()
