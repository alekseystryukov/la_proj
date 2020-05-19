from la_proj.data.decoder import to_native
import unittest


class DateDecoderTestCase(unittest.TestCase):

    def test_apple_1(self):
        lines = (
            "CgRBQVBMFexhnUMYkI6yi8VcKgNOTVMwCDgBRW68EkBItJzfEGXAwuFA2AEE",
            "CgRBQVBMFR9lnUMYoNyyi8VcKgNOTVMwCDgBRYJBE0BI5J7fEGWAj+JA2AEE"
        )

        for l in lines:
            print(to_native(l))

