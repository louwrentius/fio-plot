import unittest

from fiolib.bar3d import plot_3d

class Test3D(unittest.TestCase):
    def test_correct_bars_drawn(self):
        settings = {
            'type': ['iops'],
            'rw': 'read',
            'source': 'test',
            'title': 'test',
            'subtitle': '',
            'filter': ['read', 'write'],
            # intentionally using prime numbers
            'iodepth': [2, 3],
            'numjobs': [5, 11],
        }
        dataset = []
        for iodepth in settings['iodepth']:
            for numjobs in settings['numjobs']:
                dataset.append({
                    'iodepth': str(iodepth),
                    'numjobs': str(numjobs),
                    'rw': 'read',
                    'type': 'read',
                    'iops': iodepth * numjobs,
                })
        plot_3d(settings, dataset)


if __name__ == '__main__':
    unittest.main()
