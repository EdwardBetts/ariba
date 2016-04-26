import unittest
import copy
import filecmp
import os
from ariba import flag, summary, summary_cluster

modules_dir = os.path.dirname(os.path.abspath(summary.__file__))
data_dir = os.path.join(modules_dir, 'tests', 'data')

class TestSummary(unittest.TestCase):
    def test_init(self):
        '''Test init'''
        fofn = os.path.join(data_dir, 'summary_test_init.fofn')
        s = summary.Summary('out', fofn=fofn)
        self.assertEqual(s.filenames, ['file1', 'file2'])
        s = summary.Summary('out', filenames=['file42'])
        self.assertEqual(s.filenames, ['file42'])
        s = summary.Summary('out', fofn=fofn, filenames=['file42'])
        self.assertEqual(s.filenames, ['file42', 'file1', 'file2'])


    def test_gather_output_rows(self):
        '''Test _gather_output_rows'''
        infiles = [
            os.path.join(data_dir, 'summary_test_gather_output_rows.in.1.tsv'),
            os.path.join(data_dir, 'summary_test_gather_output_rows.in.2.tsv')
        ]
        got = summary.Summary._gather_output_rows(infiles, 90)
        expected = [
            ['filename', 'noncoding1', 'noncoding1;var.n.A14T', 'noncoding1;var.n.A6G', 'presence_absence1', 'presence_absence1;var.p.A10V', 'variants_only1'],
            [infiles[0], 1, 1, 0, 3, 1, 0],
            [infiles[1], 1, 1, 1, 3, 1, 0],
        ]

        self.assertEqual(expected, got)


    def test_filter_output_rows(self):
        '''Test _filter_output_rows'''
        rows = [
            ['filename', 'gene1', 'gene2', 'gene3'],
            ['file1', 0, 0, 0],
            ['file2', 1, 0, 3],
            ['file3', 2, 0, 4],
        ]

        expected = [
            ['filename', 'gene1', 'gene3'],
            ['file2', 1, 3],
            ['file3', 2, 4],
        ]

        got = summary.Summary._filter_output_rows(rows)
        self.assertEqual(expected, got)


    def test_write_tsv(self):
        '''Test _write_tsv'''
        tmp_out = 'tmp.out.tsv'
        rows = [
            ['filename', 'gene1', 'gene3'],
            ['file2', 1, 3],
            ['file3', 2, 4],
        ]
        summary.Summary._write_tsv(rows, tmp_out)
        expected = os.path.join(data_dir, 'summary_test_write_tsv.out.tsv')
        self.assertTrue(filecmp.cmp(tmp_out, expected, shallow=False))
        os.unlink(tmp_out)


    def test_write_phandango_csv(self):
        '''Test _write_phandango_csv'''
        tmp_out = 'tmp.test_write_phandango.csv'
        rows = [
            ['filename', 'seq1', 'seq1;var.p.I14L', 'seq1;var.p.P42Q', 'seq2', 'seq2;var.n.A14T'],
            ['file1', 3, 0, 1, 3, 1],
            ['file2', 3, 1, 0, 3, 0],
            ['file3', 1, 0, 0, 3, 0],
            ['file4', 2, 1, 0, 0, 0],
        ]
        summary.Summary._write_phandango_csv(rows, tmp_out)
        expected = os.path.join(data_dir, 'summary_test_write_phandango_csv.csv')
        self.assertTrue(filecmp.cmp(expected, tmp_out, shallow=False))
        os.unlink(tmp_out)


    def test_distance_score_bewteen_values(self):
        '''Test _distance_score_bewteen_values'''
        tests = [
            ((0, 0), 0),
            ((0, 1), 1),
            ((0, 2), 1),
            ((1, 0), 1),
            ((1, 1), 0),
            ((1, 2), 0),
            ((2, 0), 1),
            ((2, 1), 0),
            ((2, 2), 0),
        ]

        for (val1, val2), expected in tests:
            self.assertEqual(expected, summary.Summary._distance_score_between_values(val1, val2))

        # check distance calculation is commutative
        for val1 in range(5):
            for val2 in range(5):
                d1 = summary.Summary._distance_score_between_values(val1, val2)
                d2 = summary.Summary._distance_score_between_values(val2, val1)
                self.assertEqual(d1, d2)


    def test_distance_score_between_lists(self):
        '''Test _distance_score_between_lists'''
        list1 = ['na', 0, 0, 0, 1, 1, 1, 2, 2, 2]
        list2 = ['na', 0, 1, 2, 0, 1, 2, 1, 2, 2]
        self.assertEqual(3, summary.Summary._distance_score_between_lists(list1, list2))


    def test_write_distance_matrix(self):
        '''Test _write_distance_matrix'''
        rows = [
            ['filename', 'gene1', 'gene2', 'gene3'],
            ['file1', 0, 1, 0],
            ['file2', 1, 0, 3],
            ['file3', 0, 0, 4],
        ]

        tmp_distances = 'tmp.test.write_distance_matrix.distances'
        summary.Summary._write_distance_matrix(rows, tmp_distances)
        expected = os.path.join(data_dir, 'summary_test_write_distance_matrix.distances')
        self.assertTrue(filecmp.cmp(expected, tmp_distances, shallow=False))
        os.unlink(tmp_distances)


    def test_newick_from_dist_matrix(self):
        '''Test _newick_from_dist_matrix'''
        tmp_tree = 'tmp.test.newick_from_dist_matrix.tre'
        dist_file = os.path.join(data_dir, 'summary_test_newick_from_dist_matrix.distances')
        summary.Summary._newick_from_dist_matrix(dist_file, tmp_tree)
        expected = os.path.join(data_dir, 'summary_test_newick_from_dist_matrix.tre')
        self.assertTrue(filecmp.cmp(expected, tmp_tree, shallow=False))
        os.unlink(tmp_tree)


    def test_write_phandango_files(self):
        '''Test _write_phandango_files'''
        tmp_prefix = 'tmp.test.write_phandango_files'
        rows = [
            ['filename', 'seq1', 'seq1;var.p.I14L', 'seq1;var.p.P42Q', 'seq2', 'seq2;var.n.A14T'],
            ['file1', 3, 0, 1, 3, 1],
            ['file2', 3, 1, 0, 3, 0],
            ['file3', 1, 0, 0, 3, 0],
            ['file4', 2, 1, 0, 0, 0],
        ]
        summary.Summary._write_phandango_files(rows, tmp_prefix)
        expected_csv = os.path.join(data_dir, 'summary_test_write_phandango_files.csv')
        expected_tre = os.path.join(data_dir, 'summary_test_write_phandango_files.tre')
        self.assertTrue(filecmp.cmp(expected_csv, tmp_prefix + '.csv', shallow=False))
        self.assertTrue(filecmp.cmp(expected_tre, tmp_prefix + '.tre', shallow=False))
        os.unlink(tmp_prefix + '.csv')
        os.unlink(tmp_prefix + '.tre')

