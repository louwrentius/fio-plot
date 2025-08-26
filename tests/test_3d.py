import unittest
from fio_plot.fiolib.bar3d import plot_3d


class Test3D(unittest.TestCase):
    def test_correct_bars_drawn(self):
        settings = {
            "type": ["iops"],
            "rw": "read",
            "source": "test",
            "title": "test",
            "title_fontsize": 12,
            "subtitle_fontsize": 20,
            "subtitle": "",
            "filter": ["read", "write"],
            # intentionally using prime numbers
            "iodepth": [2, 3],
            "numjobs": [5, 11],
            "maxjobs": 32,
            "maxdepth": 32,
            "max_z": None,
            "dpi": 200,
            "disable_fio_version": 2.0,
            "output_filename": "/tmp/test.png",
            "truncate_xaxis": False,
            "source_fontsize": 12,
        }

        dataset = [{"data": []}]
        for iodepth in settings["iodepth"]:
            for numjobs in settings["numjobs"]:
                dataset[0]["data"].append(
                    {
                        "fio_version": 3.1,
                        "iodepth": str(iodepth),
                        "numjobs": str(numjobs),
                        "rw": "read",
                        "type": "read",
                        "iops": iodepth * numjobs,
                    }
                )
        plot_3d(settings, dataset)


if __name__ == "__main__":
    unittest.main()
