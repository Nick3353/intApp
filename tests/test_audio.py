import unittest

from inclusivoice.audio import AudioCaptureService


class AudioCaptureServiceTests(unittest.TestCase):
    def test_queue_is_bounded(self):
        service = AudioCaptureService(chunk_seconds=0.001, max_queue_size=2)
        service.start()
        try:
            import time

            time.sleep(0.02)
            self.assertLessEqual(service.output.qsize(), 2)
        finally:
            service.stop()


if __name__ == "__main__":
    unittest.main()
